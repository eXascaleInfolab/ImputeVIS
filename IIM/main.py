import numpy as np
import re
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import Ridge
import time


def iim_recovery(matrix_nan: np.ndarray, adaptive_flag: bool = False, learning_neighbors: int = 10):
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
        The number of neighbors to use for the KNN classifier, by default 10.

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

        determine_rmse(imputation_result, incomplete_tuples_indices, matrix_nan)
        # To ignore RMSE, uncomment the following lines and comment the above line
        # for result in imputation_result:
        #     matrix_nan[np.array(incomplete_tuples_indices)[:, result[0]], result[1]] = result[2]
        return matrix_nan
    else:
        print("No missing values as NaN, returning original matrix")
        return matrix_nan


def determine_rmse(imputation_result, incomplete_tuples_indices, matrix_nan):
    rmse = []

    complete_matrix = np.loadtxt("../Datasets/bafu/raw_matrices/BAFU_small.txt", delimiter=' ', )
    for result in imputation_result:
        matrix_nan[np.array(incomplete_tuples_indices)[:, result[0]], result[1]] = result[2]
        rmse.append((result[2] - complete_matrix[result[0], result[1]]) ** 2)
    print("RMSE: " + str(np.sqrt(np.mean(rmse))))


#  Algorithm 1: Learning
def learning(complete_tuples: np.ndarray, incomplete_tuples: np.ndarray, l: int = 10):
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
        The number of neighbors to use for the KNN classifier, by default 10.

    Returns
    -------
    model_params: np.ndarray[Ridge]
        The learned regression models.
    """

    knn_euc = NearestNeighbors(n_neighbors=l, metric='euclidean').fit(complete_tuples)
    model_params = np.empty((len(incomplete_tuples), l), dtype=Ridge)

    # Replace NaN values with 0
    incomplete_tuples_no_nan = np.nan_to_num(incomplete_tuples)

    # Find the k nearest neighbors for all incomplete tuples at once
    learning_neighbors = knn_euc.kneighbors(incomplete_tuples_no_nan, return_distance=False)

    for tuple_index, incomplete_tuple in enumerate(incomplete_tuples):
        nan_indicator = np.isnan(incomplete_tuple)

        # Learn the relevant value/column
        # for neighbor_index, neighbor in enumerate(learning_neighbors[tuple_index]):
        # lr = Ridge(tol=1e-10)
        # X = complete_tuples[neighbor][~nan_indicator].reshape(1, -1)
        # y = complete_tuples[neighbor][nan_indicator]

        # lr.fit(X, y)
        # model_params[tuple_index, neighbor_index] = lr
        X = complete_tuples[learning_neighbors[tuple_index]][:, ~nan_indicator]
        y = complete_tuples[learning_neighbors[tuple_index]][:, nan_indicator]
        model_params[tuple_index] = [Ridge(tol=1e-10).fit(X_i.reshape(1, -1), y_i) for X_i, y_i in zip(X, y)]
    return model_params


# Algorithm 2: Imputation
def imputation(incomplete_tuples: np.ndarray, lr_models: list[Ridge], learning_neighbors: int = 100):
    """ Imputes the missing values of the incomplete tuples using the learned linear regression models.

    Parameters
    ----------
    incomplete_tuples : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
        Should already be normalized.
    lr_models : list[Ridge]
        The learned regression models
    learning_neighbors : int, optional
        The number of neighbors to use for the KNN classifier, by default 10.

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

        missing_attribute_index = int(np.where(nan_indicator)[0])  # index of missing attribute

        # Prepare the input array for multiple samples
        incomplete_tuple_no_nan = incomplete_tuple[~nan_indicator].reshape(1, -1)

        # Predict the missing values using the learned Ridge models
        candidate_suggestions = np.array([lr.predict(incomplete_tuple_no_nan).item() for lr in lr_models[i]])

        distances = compute_distances(candidate_suggestions)
        weights = compute_weights(distances)

        impute_result = np.sum(candidate_suggestions * weights)
        # Create tuple with index (in missing tuples), attribute, imputed value
        imputed_values.append([i, missing_attribute_index, impute_result])

    return imputed_values


# Algorithm 3: Adaptive
def adaptive(complete_tuples: np.ndarray, incomplete_tuples: np.ndarray, k: int, max_learning_neighbors: int = 100, step_size: int = 5):
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
        The maximum number of neighbors to use for the learning phase, by default 100.
    step_size : int, optional
        The step size for the learning phase, by default 3.

    Returns
    -------
    phi: np.ndarray[Ridge]
        The learned regression parameters for all tuples in r.
    """
    print("Starting Algorithm 3 'adaptive'")
    all_entries = min(int(complete_tuples.shape[0]), max_learning_neighbors)
    phi_list = [learning(complete_tuples, incomplete_tuples, l_learning)  # for l in 1..n
                for l_learning in
                range(1, all_entries + 1, step_size)]
    nn = NearestNeighbors(n_neighbors=k, metric='euclidean').fit(complete_tuples)
    number_of_models = len(phi_list) - 1
    number_of_incomplete_tuples = len(incomplete_tuples)
    costs = np.zeros((number_of_incomplete_tuples, number_of_models))
    print("Finished learning; Starting main loop of Algorithm 3 'adaptive'")
    for log, complete_tuple in enumerate(complete_tuples, 1):  # for t_i in r
        if (log % 50) == 0: print("Algorithm 3 'adaptive', processing tuple {}".format(str(log)))
        neighbors = nn.kneighbors(complete_tuple.reshape(1, -1), return_distance=False)[0]
        for incomplete_tuple_idx, incomplete_tuple in enumerate(incomplete_tuples):
            nan_indicator = np.isnan(incomplete_tuple)  # Show which attribute is missing as NaN
            neighbor_filtered = np.delete(complete_tuples[neighbors], nan_indicator, axis=1)
            for l in range(0, number_of_models):  # Line 6, for l in 1..n
                phi_models = np.array([phi.predict(neighbor_filtered)
                                       for phi in phi_list[l][incomplete_tuple_idx]])
                errors = complete_tuple[nan_indicator] - phi_models
                costs[incomplete_tuple_idx, l] += np.sum(np.power(np.sum(np.abs(errors), axis=1)
                                                                  / len(phi_list[l][incomplete_tuple_idx]), 2))

    # Line 8-10 Select best model for each tuple
    best_models_indices = np.argmin(costs, axis=1)
    print("Determined following learning neighbors for each tuple with missing attributes: {}"
          .format(best_models_indices))
    phi = [phi_list[best_models_indices[i]][i] for i in range(number_of_incomplete_tuples)]
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

    if len(alg_code) > 1:
        match = re.match(r"(\d+)([a-zA-Z]+)", alg_code[1], re.I)
        if match:
            neighbors, adaptive_flag = match.groups()
            matrix_imputed = iim_recovery(matrix, adaptive_flag=adaptive_flag.startswith("a"),
                                          learning_neighbors=int(neighbors))
        else:
            matrix_imputed = iim_recovery(matrix, adaptive_flag=False, learning_neighbors=int(alg_code[1]))

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
    dataset = "BAFU_small_with_NaN.txt"
    # To use the dataset from the IIM paper, uncomment the following line and comment the previous one
    # dataset = "asf1_0.1miss.csv"
    # example arguments: "iim 5a" -> 5 neighbors & adaptive, "iim 10" -> 10  neighbors and not adaptive
    neighbors = str(7)
    adaptive_flag = "a"
    main("iim" + " " + neighbors + adaptive_flag, "../Datasets/bafu/raw_matrices/" + dataset, "../Results/"
         + neighbors + adaptive_flag + "_" + dataset, 0)
