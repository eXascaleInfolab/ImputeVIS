import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LinearRegression, Ridge
import time


def knn_recovery(matrix, matrix_nan, k):
    knn_euc = KNeighborsClassifier(n_neighbors=k, metric='euclidean')
    learning(knn_euc, matrix, matrix_nan)
    return matrix


# Algorithm 1: Learning
def learning(knn_euc, matrix, matrix_nan):
    model_params, neighbors = [], []
    # TODO When to use complete and when to use masked matrix
    # TODO Normalization? (Only care about neighbors but still relevant?
    incomplete_tuples = np.array(np.where(np.isnan(matrix_nan)))
    complete_tuples = np.array(np.where(~np.isnan(matrix_nan)))
    knn_euc.fit(matrix, np.arange(matrix.shape[0]).reshape(-1, 1))
    for tuple_index in incomplete_tuples[0]:  # for t_i in r
        learning_neighbors = knn_euc.kneighbors(np.array(matrix[tuple_index, :]).reshape(1, -1))  # k nearest neighbors
        neighbors.append(learning_neighbors[1])

        lr = Ridge()  # According to IIM paper, use Ridge regression
        # Fit linear regression based on neighbors of missing tuple
        for neighbor in learning_neighbors[1]:
            lr.fit(matrix[neighbor, :], matrix[neighbor, :])
            model_params.append(lr)  # alternatively: pass lr coefficients?
    k = 5
    imputation(matrix, incomplete_tuples, k, model_params, matrix_nan, neighbors)


# Algorithm 2: Imputation
def imputation(matrix, incomplete_tuples, k, model_params, matrix_nan, imputation_neighbors):
    matrix_scaled = (matrix * 1000).astype(int)
    knn_euc = KNeighborsClassifier(n_neighbors=k, metric='euclidean')

    knn_euc.fit(np.arange(matrix.shape[0]).reshape(-1, 1), matrix_scaled)
    i = 0
    imputed_values = []
    # For each missing tuple
    for tuple_index in incomplete_tuples[0]:  # for t_i in r
        imputation_neighbors = np.array(knn_euc.kneighbors()[1])  # k nearest neighbors

        # impute missing values
        tuple_with_missing_val = matrix_nan[tuple_index]
        # TODO Fix number of neighbors, shouldn't calculate for _all_ fields!!!
        current_imputation_neighbors = imputation_neighbors[tuple_index]
        for attribute in range(len(tuple_with_missing_val)):
            if np.isnan(tuple_with_missing_val[attribute]):
                # impute missing value
                candidate_suggestions = []
                for impute_neighbor in current_imputation_neighbors:
                    candidate_suggestions.append(
                        (model_params[i].predict(matrix[impute_neighbor, :].reshape(1, -1)))[0][attribute])

                distances = []
                for candidate in candidate_suggestions:
                    distances.append(candidate_distances(candidate, candidate_suggestions))

                weights = []
                for dist in distances:
                    weights.append(candidate_weight(dist, distances))

                impute_result = sum(np.asarray(candidate_suggestions) * np.asarray(weights))
                imputed_values.append([tuple_index, attribute, impute_result])
        i = i + 1
    return imputed_values


def candidate_distances(candidate, candidate_suggestions):
    distances = []
    for candidate_2 in candidate_suggestions:
        distances.append(np.sum(np.abs(candidate - candidate_2)))
    return sum(distances)


# Weights are normed, all weights together sum up to 1
def candidate_weight(candidate_distance, all_distances):
    return (1 / candidate_distance) / (sum(1 / np.asarray(all_distances)))


def main(alg_code, filename_input, filename_output, runtime):
    # read input matrix
    matrix = np.loadtxt(filename_input, delimiter=' ')
    matrix_with_nan = np.loadtxt("../Datasets/bafu/raw_matrices/BAFU_tiny_with_NaN.txt", delimiter=' ')

    # beginning of imputation process - start time measurement
    start_time = time.time()

    matrix_imputed = knn_recovery(matrix, matrix_with_nan, 5)

    # imputation is complete - stop time measurement
    end_time = time.time()

    # calculate the time elapsed in [!] microseconds
    exec_time = (end_time - start_time) * 1000 * 1000

    # verification
    nan_mask = np.isnan(matrix_imputed)
    matrix_imputed[nan_mask] = np.sqrt(np.finfo('d').max / 100000.0)

    print("Time", alg_code, ":", exec_time)

    # Use binary flag to indicate runtime results or algorithm output
    if runtime > 0:
        # if we need runtime, we only save one value with the time in microseconds
        np.savetxt(filename_output, np.array([exec_time]))
    else:
        # if we need the output, we instead save the matrix with imputed values to the same file
        np.savetxt(filename_output, matrix_imputed)
    # end if


if __name__ == '__main__':
    main("IIM", "../Datasets/bafu/raw_matrices/BAFU_tiny.txt", "../Results/Bafu.csv", 0)
