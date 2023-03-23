import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import LinearRegression, Ridge
import time


def iim_recovery(matrix_nan: np.ndarray, adaptive_flag: bool = False, k: int = 5):
    """Implementation of the IIM algorithm
    TODO More desc

    Parameters
    ----------
    matrix_nan : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
    adaptive_flag : bool, optional
        Whether to use the adaptive version of the algorithm, by default False.
    k : int, optional
        The number of neighbors to use for the KNN classifier, by default 5.

    Returns
    -------
    imputed_values : list[list[int, int, float]]
        Returns the imputed values in the form of a list of lists, where each list contains the tuple index,
        the attribute index and the imputed value.
    """
    tuples_with_nan = np.isnan(matrix_nan).any(axis=1)
    incomplete_tuples_indices = np.array(np.where(tuples_with_nan == True))
    incomplete_tuples = matrix_nan[tuples_with_nan]
    columns_with_nan = np.array(np.where(np.isnan(matrix_nan).any(axis=0) == True))
    complete_tuples = matrix_nan[~tuples_with_nan]  # Rows that do not contain a NaN value
    if adaptive_flag:
        lr_models, neighbors = learning(complete_tuples, incomplete_tuples, return_neighbors=True)  # lines 1-2 of Alg 3
        lr_models = adaptive(complete_tuples, incomplete_tuples, columns_with_nan, k)  # rest of Alg 3 (lines 3-11)
        imputation_result = imputation(complete_tuples, incomplete_tuples, lr_models, neighbors)  # TODO Correct params passed?

    else:
        lr_models, neighbors = learning(complete_tuples, incomplete_tuples, return_neighbors=True)
        imputation_result = imputation(complete_tuples, incomplete_tuples, lr_models, neighbors)

    for result in imputation_result:
        matrix_nan[np.array(incomplete_tuples_indices)[:, result[0]], result[1]] = result[2]
    return matrix_nan


#  Algorithm 1: Learning
def learning(complete_tuples: np.ndarray, incomplete_tuples: np.ndarray, l: int = 5, return_neighbors: bool = False):
    """Learns individual regression models for each learning partner

    Parameters
    ----------
    complete_tuples : np.ndarray
        The complete matrix of values without missing values.
        Should already be normalized.
    incomplete_tuples : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
        Should already be normalized.
    l : int, optional
        The number of neighbors to use for the KNN classifier, by default 5.
    return_neighbors : bool, optional
        Whether to return the learning neighbors of each missing tuple, by default False.

    Returns
    -------
    model_params
        The learned regression models.
    neighbors
        The learning neighbors of each missing tuple.
    """

    knn_euc = KNeighborsClassifier(n_neighbors=l, metric='euclidean')
    knn_euc.fit(complete_tuples, np.arange(complete_tuples.shape[0]))
    model_params, neighbors = [], []
    for incomplete_tuple in incomplete_tuples:  # for t_i in r
        # If all imputed values are in a single col, the following line could be foregone to simply ignore that col
        learning_neighbors = knn_euc.kneighbors(np.nan_to_num(incomplete_tuple).reshape(1, -1))  # k nearest neighbors
        neighbors.append(learning_neighbors[1])

        lr = Ridge()  # According to IIM paper, use Ridge regression
        # Fit linear regression based on neighbors of missing tuple
        for neighbor in learning_neighbors[1]:
            lr.fit(complete_tuples[neighbor, :], complete_tuples[neighbor, :])
            model_params.append(lr)  # alternatively: pass lr coefficients?
    if return_neighbors:
        return model_params, neighbors
    else:
        return model_params


# Algorithm 2: Imputation
def imputation(complete_tuples: np.ndarray, incomplete_tuples: np.ndarray, lr_models: list[Ridge],
               imputation_neighbors: list[np.ndarray]):
    """ Imputes the missing values of the incomplete tuples using the learned linear regression models.

    Parameters
    ----------
    complete_tuples : np.ndarray
        The complete matrix of values without missing values.
        Should already be normalized.
    incomplete_tuples : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
        Should already be normalized.
    lr_models : list[Ridge]
        The learned regression models
    imputation_neighbors : list[np.ndarray]
        The learning neighbors of each missing tuple

    Returns
    -------
    imputed_values : list[list[int, int, float]]
        Returns the imputed values in the form of a list of lists, where each list contains the tuple index,
        the attribute index and the imputed value.
    """
    imputed_values = []
    # For each missing tuple
    for i, incomplete_tuple in enumerate(incomplete_tuples):  # for t_i in r

        # impute missing values
        for attribute in range(len(incomplete_tuple)):
            if np.isnan(incomplete_tuple[attribute]):  # if attribute is missing, impute
                candidate_suggestions = []
                for impute_neighbor in np.nditer(imputation_neighbors[i]):
                    candidate_suggestions.append((lr_models[i].predict(complete_tuples[impute_neighbor, :]
                                                                       .reshape(1, -1)))[0][attribute])

                distances = compute_distances(candidate_suggestions)
                weights = compute_weights(distances)

                impute_result = sum(np.asarray(candidate_suggestions) * np.asarray(weights))
                # Create tuple with index (in missing tuples), attribute, imputed value
                imputed_values.append([i, attribute, impute_result])
    return imputed_values


# Algorithm 3: Adaptive
def adaptive(complete_tuples: np.ndarray, incomplete_tuples: np.ndarray, columns_with_nan: np.ndarray, k: int):
    """Adaptive imputation of missing values

    Parameters
    ----------
    complete_tuples : np.ndarray
        The complete matrix of values without missing values.
        Should already be normalized.
    incomplete_tuples : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
        Should already be normalized.
    columns_with_nan : np.ndarray
        The indices of the columns with missing values.
    k : int
        The number of neighbors to use for the k nearest neighbors classifier.

    Returns
    -------
    phi: np.ndarray
        The learned regression parameters for all tuples in r.
    """

    phi_list = [learning(complete_tuples, incomplete_tuples, l)
                           for l in range(1, complete_tuples.shape[0] + 1)]  # for l in 1..n
    nn = NearestNeighbors(n_neighbors=k, metric='euclidean')
    nn.fit(complete_tuples)
    costs = np.zeros((complete_tuples.shape[0], complete_tuples.shape[0]-1))
    for log, complete_tuple in enumerate(complete_tuples):  # for t_i in r
        if (log + 1 % 100) == 0: print("Algorithm 3 'adaptive', processing tuple {}".format(log))
        neighbors = nn.kneighbors(complete_tuple.reshape(1, -1), return_distance=False)[0]
        for i, neighbor in enumerate(neighbors):  # Line 5
            for l in range(0, complete_tuples.shape[0]-1):  # Line 6, for l in 1..n
                for attribute in np.nditer(columns_with_nan):  # iterate over all columns, as not just a single column is of interest
                    # Line 7, calculating the squared difference for each column with missing values to imputed value
                    # TODO Fix cost assignment
                    costs[i, l] += np.power(np.abs(complete_tuple[attribute] -
                                                   (phi_list[l][i].predict(complete_tuples[neighbor, :]))[0][attribute])
                                            , 2)

    # Line 8-10 Select best model for each tuple
    best_models_indices = np.argmin(costs, axis=0)
    phi = [phi_list[best_models_indices[i]][i] for i in range(len(incomplete_tuples))]
    return phi


def compute_distances(candidate_suggestions: list[float]):
    """ Calculate the sum of distances to all other candidates (Manhattan) for each candidate

    Parameters
    ----------
    candidate_suggestions : list[float]
        All other candidates to compare the values to.

    Returns
    -------
    distances
        The sum of distances to all other candidates.
    """
    distances = []
    for candidate in candidate_suggestions:
        temp_distances = []
        for candidate_2 in candidate_suggestions:
            temp_distances.append(np.sum(np.abs(candidate - candidate_2)))
        distances.append(sum(temp_distances))
    return distances


def compute_weights(distances: list[float]):
    """ A candidate's weight is determined by normalizing by all other candidates' values.
    All weights together sum up to 1.

    Parameters
    ----------
    distances : list[float]
        A list of all distances.

    Returns
    -------
    weight
        The weight of the candidate.
    """

    weights = []
    for idx, dist in enumerate(distances):
        dist_without_self = np.asarray(distances[:idx] + distances[idx + 1:])
        if np.all(np.asarray(distances) == 0):  # If all 0, just weigh equally, TODO Is this okay?
            weights.append(1 / len(distances))
        else:
            weights.append((1 / dist) / (sum(1 / np.asarray(dist_without_self))))
    return weights


def main(alg_code: str, filename_input: str, filename_output: str, runtime: int):
    """Executes the imputation algorithm given an input matrix.

    Parameters
    ----------
    alg_code : str
        The algorithm and its parameters.
        The first parameter is the name, the second the number of neighbors and the third whether to use adaptive or not.
    filename_input : str
        The input matrix to be imputed.
    filename_output : str
        The output matrix with imputed values.
    runtime : int
        Whether to save values or not.

    Returns
    -------
    distances
        The sum of distances to all other candidates.
    """
    # read input matrix
    matrix = np.loadtxt(filename_input, delimiter=' ', )

    # For dataset delimited by ',' and having a header
    # matrix = np.loadtxt(filename_input, delimiter=',', skiprows=1)

    # beginning of imputation process - start time measurement
    start_time = time.time()

    # Imputation
    alg_code = alg_code.split()

    if len(alg_code) > 3:
        matrix_imputed = iim_recovery(matrix, adaptive_flag=alg_code[3] == "adaptive", k=int(alg_code[2]))
    else:
        matrix_imputed = iim_recovery(matrix, adaptive_flag=False, k=int(alg_code[1]))


    # imputation is complete - stop time measurement
    end_time = time.time()

    # calculate the time elapsed in [!] microseconds
    exec_time = (end_time - start_time) * 1000 * 1000

    # verification to check for NaN. If found, assign absurdly high value to them.
    nan_mask = np.isnan(matrix_imputed)
    matrix_imputed[nan_mask] = np.sqrt(np.finfo('d').max / 100000.0)

    print("Time", alg_code, ":", exec_time)

    # Use binary flag to indicate runtime results or algorithm output
    if runtime > 0:
        # if we need runtime, we only save one value with the time in microseconds
        np.savetxt(filename_output, np.array([exec_time]))
    else:
        # if we need the output, we instead save the matrix with imputed values to the same file
        # Tuple_Index (row), Attribute_Index (column), Imputed_Value
        np.savetxt(filename_output, matrix_imputed, fmt='%f', delimiter=' ')


if __name__ == '__main__':
    dataset = "BAFU_tiny_with_NaN.txt"
    # To use the dataset from the IIM paper, uncomment the following line and comment the previous one
    # dataset = "asf1_0.1miss.csv"
    main("-algx iim 5 adaptive ", "../Datasets/bafu/raw_matrices/" + dataset, "../Results/" + dataset, 0)
