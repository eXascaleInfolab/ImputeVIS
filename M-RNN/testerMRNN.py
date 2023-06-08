import time
import numpy as np
from Data_Loader import Data_Loader_Incomplete
from M_RNN import M_RNN


def mrnn_recov(matrix_in, matrix_out, runtime):
    seq_length = 7

    _, trainZ, trainM, trainT, testX, testZ, testM, testT, dmin, dmax, train_size, x = Data_Loader_Incomplete(
        seq_length, matrix_in)

    start_time = time.time()

    _, Recover_testX = M_RNN(trainZ, trainM, trainT, testZ, testM, testT)

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
    #x = x[::-1]

    print("Time (M-RNN):", (timev * 1000 * 1000))

    if runtime > 0:
        np.savetxt(matrix_out, np.array([timev * 1000 * 1000]), fmt='%f', delimiter=' ')  # to microsec
    else:
        np.savetxt(matrix_out, x, fmt='%f', delimiter=' ')


def main(filename_input: str = "../Datasets/bafu/raw_matrices/BAFU_small_with_NaN.txt",
         filename_output: str = "../Results/2_BAFU_small_with_NaN.txt", runtime: int = 0):
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
    mrnn_recov(filename_input, filename_output, runtime)


# TODO Pass parameters
if __name__ == '__main__':
    dataset = "BAFU_small_with_NaN.txt"

    main("../Datasets/bafu/raw_matrices/" + dataset, "../Results/M-RNN/" + dataset, 0)
