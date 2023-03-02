import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LinearRegression, Ridge
import time


def iim_recovery(matrix, matrix_nan, k: int = 5):
    """Implementation of the IIM algorithm
    TODO More desc

    Parameters
    ----------
    matrix : np.ndarray
        The complete matrix of values without missing values.
    matrix_nan : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
    k : int, optional
        The number of neighbors to use for the KNN classifier, by default 5.

    Returns
    -------
    imputed_values : list[list[int, int, float]]
        Returns the imputed values in the form of a list of lists, where each list contains the tuple index,
        the attribute index and the imputed value.
    """
    knn_euc = KNeighborsClassifier(n_neighbors=k, metric='euclidean')
    knn_euc.fit(matrix, np.arange(matrix.shape[0]).reshape(-1, 1))
    lr_models, neighbors = learning(knn_euc, matrix, matrix_nan)
    incomplete_tuples = np.array(np.where(np.isnan(matrix_nan)))
    return imputation(matrix, incomplete_tuples, knn_euc, lr_models, matrix_nan, neighbors)


#  Algorithm 1: Learning
def learning(knn_euc: KNeighborsClassifier, matrix, matrix_nan):
    """Learns individual regression models for each learning partner

    Parameters
    ----------
    knn_euc : KNeighborsClassifier
        K neighbors classifier, euclidean with custom k.
    matrix : np.ndarray
        The complete matrix of values without missing values.
    matrix_nan : np.ndarray
        The complete matrix of values with missing values in the form of NaN.

    Returns
    -------
    model_params
        The learned regression models.
    neighbors
        The learning neighbors of each missing tuple.
    """
    # TODO When to use complete and when to use masked matrix
    # TODO Normalization? (Only care about neighbors but still relevant?
    model_params, neighbors = [], []
    incomplete_tuples = np.array(np.where(np.isnan(matrix_nan)))
    complete_tuples = np.array(np.where(~np.isnan(matrix_nan)))
    for tuple_index in incomplete_tuples[0]:  # for t_i in r
        learning_neighbors = knn_euc.kneighbors(np.array(matrix[tuple_index, :]).reshape(1, -1))  # k nearest neighbors
        neighbors.append(learning_neighbors[1])

        lr = Ridge()  # According to IIM paper, use Ridge regression
        # Fit linear regression based on neighbors of missing tuple
        for neighbor in learning_neighbors[1]:
            lr.fit(matrix[neighbor, :], matrix[neighbor, :])
            model_params.append(lr)  # alternatively: pass lr coefficients?
    return model_params, neighbors


# Algorithm 2: Imputation
def imputation(matrix, incomplete_tuples, knn_euc: KNeighborsClassifier, lr_models: list[Ridge], matrix_nan: np.ndarray,
               imputation_neighbors: list[np.ndarray]):
    """Gets and prints the spreadsheet's header columns

    Parameters
    ----------
    matrix : np.ndarray
        The complete matrix of values without missing values.
    incomplete_tuples :
        A flag used to print the columns to the console (default is False)
    knn_euc : KNeighborsClassifier
        K neighbors classifier, euclidean with custom k
    lr_models : list[Ridge]
        The learned regression models
    matrix_nan : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
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
    for i, tuple_index in enumerate(incomplete_tuples[0]):  # for t_i in r
        imputation_neighbors = np.array(knn_euc.kneighbors()[1])  # k nearest neighbors

        # impute missing values
        tuple_with_missing_val = matrix_nan[tuple_index]
        # TODO Fix number of neighbors, shouldn't calculate for _all_ fields!!!
        current_imputation_neighbors = imputation_neighbors[tuple_index]
        for attribute in range(len(tuple_with_missing_val)):
            if np.isnan(tuple_with_missing_val[attribute]):  # if attribute is missing
                # impute missing value
                candidate_suggestions = []
                for impute_neighbor in current_imputation_neighbors:
                    candidate_suggestions.append(
                        (lr_models[i].predict(matrix[impute_neighbor, :].reshape(1, -1)))[0][attribute])

                distances = []
                for candidate in candidate_suggestions:
                    distances.append(candidate_distances(candidate, candidate_suggestions))

                weights = []
                for dist in distances:
                    weights.append(candidate_weight(dist, distances))

                impute_result = sum(np.asarray(candidate_suggestions) * np.asarray(weights))
                # Create tuple with index, attribute, imputed value
                imputed_values.append([tuple_index, attribute, impute_result])
    return imputed_values


# TODO Prevent self-comparison! (?)
def candidate_distances(candidate: float, candidate_suggestions: list[float]):
    """For a single candidate, calculate the sum of distances to all other candidates (Manhattan)

    Parameters
    ----------
    candidate : float
        The candidate's value to be regarded
    candidate_suggestions : list[float]
        All other candidates to compare the values to

    Returns
    -------
    distances
        The sum of distances to all other candidates.
    """
    distances = []
    for candidate_2 in candidate_suggestions:
        distances.append(np.sum(np.abs(candidate - candidate_2)))
    return sum(distances)


def candidate_weight(candidate_distance: float, all_distances: list[float]):
    """ A candidate's weight is determined by normalizing by all other candidates' values.
    All weights together sum up to 1.

    Parameters
    ----------
    candidate_distance : float
        The distance to be weighted.
    all_distances : list[float]
        A list of all distances.

    Returns
    -------
    weight
        The weight of the candidate.
    """
    return (1 / candidate_distance) / (sum(1 / np.asarray(all_distances)))


def main(alg_code: str, filename_input: str, filename_output: str, runtime: int):
    """TODO

    Parameters
    ----------
    alg_code : str
        The algorithm to be used. [Not implemented]
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
    matrix = np.loadtxt(filename_input, delimiter=' ')
    matrix_with_nan = np.loadtxt("../Datasets/bafu/raw_matrices/BAFU_tiny_with_NaN.txt", delimiter=' ')

    # beginning of imputation process - start time measurement
    start_time = time.time()

    matrix_imputed = iim_recovery(matrix, matrix_with_nan, 5)

    # imputation is complete - stop time measurement
    end_time = time.time()

    # calculate the time elapsed in [!] microseconds
    exec_time = (end_time - start_time) * 1000 * 1000

    # verification
    # nan_mask = np.isnan(matrix_imputed)
    # matrix_imputed[nan_mask] = np.sqrt(np.finfo('d').max / 100000.0)

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
    main("iim", "../Datasets/bafu/raw_matrices/BAFU_tiny.txt", "../Results/Bafu.csv", 0)
