import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import LinearRegression, Ridge
import time


def iim_recovery(matrix_nan: np.ndarray, adaptive_flag: bool = False, learning_neighbors: int = 5):
    """Implementation of the IIM algorithm
    Via the adaptive flag, the algorithm can be run in two modes:
    - Adaptive: The algorithm will run the adaptive version of the algorithm, as described in the paper
        - Essentially, the algorithm will determine the best number of learning neighbors
    - Non-adaptive: The algorithm will run the non-adaptive version of the algorithm, as described in the paper

    Parameters
    ----------
    matrix_nan : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
    adaptive_flag : bool, optional
        Whether to use the adaptive version of the algorithm, by default False.
    learning_neighbors : int, optional
        The number of neighbors to use for the KNN classifier, by default 5.

    Returns
    -------
    matrix_nan : np.ndarray
        The complete matrix of values with missing values imputed.
    """
    tuples_with_nan = np.isnan(matrix_nan).any(axis=1)
    if np.any(tuples_with_nan):  # if there are any tuples with missing values as NaN
        incomplete_tuples_indices = np.array(np.where(tuples_with_nan == True))
        incomplete_tuples = matrix_nan[tuples_with_nan]
        columns_with_nan = np.array(np.where(np.isnan(matrix_nan).any(axis=0) == True))
        complete_tuples = matrix_nan[~tuples_with_nan]  # Rows that do not contain a NaN value
        col_with_max_nan = np.argmax(np.count_nonzero(np.isnan(matrix_nan), axis=0))
        if adaptive_flag:
            print("Running IIM algorithm with adaptive algorithm, k = " + str(learning_neighbors) + "...")
            lr_models = adaptive(complete_tuples, incomplete_tuples, learning_neighbors)
            imputation_result = imputation(incomplete_tuples, lr_models, learning_neighbors)

        else:
            print("Running IIM algorithm with k = " + str(learning_neighbors) + "...")
            lr_models = learning(complete_tuples, incomplete_tuples, learning_neighbors)
            imputation_result = imputation(incomplete_tuples, lr_models, learning_neighbors)

        for result in imputation_result:
            matrix_nan[np.array(incomplete_tuples_indices)[:, result[0]], result[1]] = result[2]
        return matrix_nan
    else:
        print("No missing values as NaN, returning original matrix")
        return matrix_nan


#  Algorithm 1: Learning
def learning(complete_tuples: np.ndarray, incomplete_tuples: np.ndarray, l: int = 5):
    """Learns individual regression models for each learning neighbor,
        by fitting on the other attributes and the missing attribute

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

    Returns
    -------
    model_params
        The learned regression models.
    """

    knn_euc = NearestNeighbors(n_neighbors=l, metric='euclidean')
    knn_euc.fit(complete_tuples)
    model_params, neighbors = [], []
    model_params = np.empty((len(incomplete_tuples),l), dtype=object)
    for tuple_index, incomplete_tuple in enumerate(incomplete_tuples):  # for t_i in r
        # If all imputed values are in a single col, the following line could be foregone to simply ignore that col
        learning_neighbors = knn_euc.kneighbors(np.nan_to_num(incomplete_tuple).reshape(1, -1), return_distance=False)[
            0]  # k nearest neighbors
        neighbors.append(learning_neighbors)

        # Fit linear regression based on neighbors of missing tuple
        nan_indicator = np.isnan(incomplete_tuple)  # show which attribute is missing as NaN

        # learn the relevant value/column
        for neighbor_index, neighbor in enumerate(learning_neighbors):
            lr = Ridge(tol=1e-10)  # According to IIM paper, use Ridge regression
            lr.fit(complete_tuples[neighbor][~nan_indicator].reshape(1, -1),
                   complete_tuples[neighbor][nan_indicator])
            model_params[tuple_index, neighbor_index] = lr
    return model_params


# Algorithm 2: Imputation
def imputation(incomplete_tuples: np.ndarray, lr_models: list[Ridge], learning_neighbors: int = 5):
    """ Imputes the missing values of the incomplete tuples using the learned linear regression models.

    Parameters
    ----------
    incomplete_tuples : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
        Should already be normalized.
    lr_models : list[Ridge]
        The learned regression models
    learning_neighbors : int, optional
        The number of neighbors to use for the KNN classifier, by default 5.

    Returns
    -------
    imputed_values : list[list[int, int, float]]
        Returns the imputed values in the form of a list of lists,
        where each list contains the tuple index, the attribute index and the imputed value.
    """
    imputed_values = []
    # For each missing tuple
    for i, incomplete_tuple in enumerate(incomplete_tuples):  # for t_i in r
        nan_indicator = np.isnan(incomplete_tuple)  # show which attribute is missing as NaN

        # impute missing values
        missing_attribute_index = int(np.where(nan_indicator)[0])  # index of missing attribute
        candidate_suggestions = []
        for neighbor in range(learning_neighbors):
            candidate_suggestions.append((lr_models[i][neighbor].predict(incomplete_tuple[~nan_indicator]
                                                                         .reshape(1, -1))).item())
        distances = compute_distances(candidate_suggestions)
        weights = compute_weights(distances)
        impute_result = sum(np.asarray(candidate_suggestions) * np.asarray(weights))
        # Create tuple with index (in missing tuples), attribute, imputed value
        imputed_values.append([i, missing_attribute_index, impute_result])
    return imputed_values


# Algorithm 3: Adaptive
def adaptive(complete_tuples: np.ndarray, incomplete_tuples: np.ndarray, k: int, max_learning_neighbors: int = 100):
    """Adaptive learning of regression parameters

    Parameters
    ----------
    complete_tuples : np.ndarray
        The complete matrix of values without missing values.
        Should already be normalized.
    incomplete_tuples : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
        Should already be normalized.
    k : int
        The number of neighbors to use for the k nearest neighbors classifier.
    max_learning_neighbors : int, optional
        The maximum number of neighbors to use for the learning phase, by default 200.

    Returns
    -------
    phi: np.ndarray
        The learned regression parameters for all tuples in r.
    """
    print("Starting Algorithm 3 'adaptive'")
    all_entries = min(int(complete_tuples.shape[0]), max_learning_neighbors)
    phi_list = [learning(complete_tuples, incomplete_tuples, l_learning)  # for l in 1..n
                for l_learning in
                range(1, all_entries + 1)]
    nn = NearestNeighbors(n_neighbors=k, metric='euclidean')
    nn.fit(complete_tuples)
    costs = np.zeros((len(incomplete_tuples), all_entries - 1))
    print("Finished learning; Starting main loop of Algorithm 3 'adaptive'")
    for log, complete_tuple in enumerate(complete_tuples[:all_entries, ], 1):  # for t_i in r
        if (log % 100) == 0: print("Algorithm 3 'adaptive', processing tuple {}".format(str(log)))
        neighbors = nn.kneighbors(complete_tuple.reshape(1, -1), return_distance=False)[0]
        for incomplete_tuple_idx, incomplete_tuple in enumerate(incomplete_tuples):
            nan_indicator = np.isnan(incomplete_tuple)  # show which attribute is missing as NaN
            for i, neighbor in enumerate(neighbors):  # Line 5
                for l in range(0, all_entries - 1):  # Line 6, for l in 1..n
                    error = 0
                    number_of_models_considered = 0
                    for phi_index, phi in enumerate(phi_list[l][incomplete_tuple_idx], 1):  # Iterate over all models using l neighbors
                        # Line 7, calculate squared error for column with most NaNs
                        error += abs(float(complete_tuple[nan_indicator]
                                           - (phi.predict(np.delete(complete_tuples[neighbor], nan_indicator)
                                                          .reshape(1, -1)))
                                           ))
                        number_of_models_considered = phi_index  # Used to take average error
                    costs[incomplete_tuple_idx, l] += np.power(error / number_of_models_considered, 2)

    # Line 8-10 Select best model for each tuple
    best_models_indices = np.argmin(costs, axis=1)
    print("Determined following learning neighbors for each tuple with missing attributes: {}"
          .format(best_models_indices))
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
    """ A candidate's weight is determined by normalizing by all other candidates' distances.
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
        matrix_imputed = iim_recovery(matrix, adaptive_flag=alg_code[3].startswith("a"),
                                      learning_neighbors=int(alg_code[2]))
    else:
        matrix_imputed = iim_recovery(matrix, adaptive_flag=False, learning_neighbors=int(alg_code[2]))

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
    main("-algx iim 5 a", "../Datasets/bafu/raw_matrices/" + dataset, "../Results/5l_adaptive_" + dataset, 0)
