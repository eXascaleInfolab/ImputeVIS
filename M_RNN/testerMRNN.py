import time
import numpy as np

import M_RNN
from M_RNN import MRNN
from M_RNN import Data_Loader


def mrnn_recov(matrix_in, runtime=0, hidden_dim=10, learning_rate=0.01, iterations=1000, keep_prob=1.0,
               matrix_out="../Results/M-RNN/BAFU_temp.txt"):
    seq_length = 7

    _, trainZ, trainM, trainT, testX, testZ, testM, testT, dmin, dmax, train_size, x = Data_Loader.Data_Loader_Incomplete(
        seq_length, matrix_in)

    start_time = time.time()

    _, Recover_testX = MRNN.M_RNN(trainZ, trainM, trainT, testZ, testM, testT,
                                  hidden_dim=hidden_dim,
                                  learning_rate=learning_rate,
                                  iterations=iterations,
                                  keep_prob_var=keep_prob
                                  )

    m = len(x[0])  # columns

    # part 1: upper block
    for si in range(0, seq_length - 1):  # si = sequence index
        i = train_size + si  # index in the main matrix
        for j in range(0, m):
            if np.isnan(x[i][j]):
                val = 0.0
                for sj in range(0, si + 1):
                    val += Recover_testX[sj][si - sj][j]
                x[i][j] = val / (si + 1)  # average

    # part 2: middle block
    for ri in range(seq_length - 1, len(Recover_testX)):# - seq_length):
        i = train_size + ri
        for j in range(0, m):
            if np.isnan(x[i][j]):
                val = 0.0
                for sj in range(0, seq_length):
                    val += Recover_testX[ri - sj][sj][j]
                x[i][j] = val / seq_length  # average

    # part 3: lower block
    for si in range(0, seq_length):  # si = sequence index
        i = len(x) - si - 1  # index in the main matrix
        ri = len(Recover_testX) - si - 1
        for j in range(0, m):
            if np.isnan(x[i][j]):
                val = 0.0
                for sj in range(0, si + 1):
                    val += Recover_testX[ri + sj][seq_length - sj - 1][j]
                x[i][j] = val / (si + 1)  # average

    end_time = time.time()
    timev = end_time - start_time

    # reverse changes introduced to data
    denominator = dmax - dmin
    x = (x * denominator) + dmin
    # verification to check for NaN. If found, assign absurdly high value to them.
    nan_mask = np.isnan(x)
    x[nan_mask] = np.sqrt(np.finfo('d').max / 100000.0)
    #x = x[::-1]

    print("Time (M-RNN):", (timev * 1000 * 1000))

    if runtime > 0:
        np.savetxt(matrix_out, np.array([timev * 1000 * 1000]), fmt='%f', delimiter=' ')  # to microsec
    else:
        np.savetxt(matrix_out, x, fmt='%f', delimiter=' ')

    return np.asarray(x).tolist()


def main(filename_input: str = "../Datasets/bafu/obfuscated/BAFU_tiny_obfuscated_40.txt",
         filename_output: str = "../Results/M-RNN/BAFU_temp.txt", runtime: int = 0):
    """Executes M-RNN algorithm given an input matrix.

    Parameters
    ----------.
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
    # matrix = np.loadtxt(filename_input, delimiter=' ', )
    mrnn_recov(matrix_in=filename_input, matrix_out=filename_output, runtime=runtime)


if __name__ == '__main__':
    dataset = "BAFU_tiny_obfuscated_10.txt"

    main("../Datasets/bafu/obfuscated/BAFU_tiny_obfuscated_10.txt", "../Results/M-RNN/" + dataset, 0)


# TODO: To have less issues with Django imports, duplicate Data_Loader.py here:
# %% Google data loading

'''
1. train_rate: training / testing set ratio
2. missing_rate: the amount of introducing missingness
'''

