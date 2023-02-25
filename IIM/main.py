import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LinearRegression, Ridge
import time


def recover_matrix_with_knn(matrix):
    return knn_recovery(matrix, 5)


def knn_recovery(matrix, k):
    knn_euc = KNeighborsClassifier(n_neighbors=k, metric='euclidean')
    model_params = []
    incomplete_attributes = np.array([matrix.shape[0] + 1] * matrix.shape[1]).reshape(-1, 1)
    for idx, tuple in enumerate(matrix, start=1):  # for t_i in r
        # convert float to int (could be circumvented by multiplying)
        tuple_int = tuple.astype(int).reshape(-1, 1)
        idx_array = np.array([idx] * matrix.shape[1]).reshape(-1, 1)
        knn_euc.fit(idx_array, tuple_int)
        learning_neighbors = np.array(knn_euc.kneighbors()[1])  # k nearest neighbors

        lr = Ridge()  # According to IIM paper, use Ridge regression
        # Simply trying to predict the next tuple in the sequence, based on nearest neighbors
        lr.fit(learning_neighbors, incomplete_attributes)
        model_params.append(lr)  # alternatively: pass lr coefficients
    return matrix


def main(alg_code, filename_input, filename_output, runtime):
    # read input matrix
    matrix = np.loadtxt(filename_input, delimiter=' ')

    # beginning of imputation process - start time measurement
    start_time = time.time()

    matrix_imputed = recover_matrix_with_knn(matrix)

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
