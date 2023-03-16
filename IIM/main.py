import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.impute import KNNImputer
from sklearn.linear_model import LinearRegression, Ridge
import time


def iim_recovery(matrix_nan, k: int = 5):
    """Implementation of the IIM algorithm
    TODO More desc

    Parameters
    ----------
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
    knn_euc = KNeighborsClassifier(n_neighbors=k, metric='nan_euclidean')
    tuples_with_nan = np.isnan(matrix_nan).any(axis=1)
    incomplete_tuples_indices = np.array(np.where(tuples_with_nan == True))
    incomplete_tuples = matrix_nan[tuples_with_nan]
    complete_tuples = matrix_nan[~tuples_with_nan]  # Only return rows that do not contain a NaN value
    knn_euc.fit(complete_tuples, np.arange(complete_tuples.shape[0]).reshape(-1, 1))
    lr_models, neighbors = learning(knn_euc, complete_tuples, incomplete_tuples)
    imputation_result = imputation(complete_tuples, incomplete_tuples, lr_models, neighbors)

    for result in imputation_result:
        matrix_nan[np.array(incomplete_tuples_indices)[:,result[0]], result[1]] = result[2]
    return matrix_nan


#  Algorithm 1: Learning
def learning(knn_euc: KNeighborsClassifier, complete_tuples, incomplete_tuples):
    """Learns individual regression models for each learning partner

    Parameters
    ----------
    knn_euc : KNeighborsClassifier
        K neighbors classifier, euclidean with custom k.
    complete_tuples : np.ndarray
        The complete matrix of values without missing values.
        Should already be normalized.
    incomplete_tuples : np.ndarray
        The complete matrix of values with missing values in the form of NaN.
        Should already be normalized.

    Returns
    -------
    model_params
        The learned regression models.
    neighbors
        The learning neighbors of each missing tuple.
    """

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
    return model_params, neighbors


# Algorithm 2: Imputation
def imputation(complete_tuples, incomplete_tuples, lr_models: list[Ridge], imputation_neighbors: list[np.ndarray]):
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
        dist_without_self = distances[:idx] + distances[idx + 1:]
        weights.append((1 / dist) / (sum(1 / np.asarray(dist_without_self))))
    return weights


def main(alg_code: str, filename_input: str, filename_output: str, runtime: int):
    """Executes the imputation algorithm given an input matrix.

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
    matrix = np.loadtxt(filename_input, delimiter=' ',)

    # For asf dataset:
    # matrix = np.loadtxt(filename_input, delimiter=',', skiprows=1)

    # beginning of imputation process - start time measurement
    start_time = time.time()

    # Imputation
    matrix_imputed = iim_recovery(matrix, 5)

    # imputation is complete - stop time measurement
    end_time = time.time()

    # calculate the time elapsed in [!] microseconds
    exec_time = (end_time - start_time) * 1000 * 1000

    # verification TODO?
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
    dataset = "BAFU_tiny_with_NaN.txt"
    # dataset = "asf1_0.1miss.csv"
    main("iim", "../Datasets/bafu/raw_matrices/" + dataset, "../Results/" + dataset, 0)
