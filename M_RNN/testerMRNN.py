import time
import numpy as np
from M_RNN import M_RNN


def mrnn_recov(matrix_in, matrix_out, runtime, hidden_dim=10, learning_rate=0.01, iterations=1000, keep_prob=1.0):
    seq_length = 7

    _, trainZ, trainM, trainT, testX, testZ, testM, testT, dmin, dmax, train_size, x = Data_Loader_Incomplete(
        seq_length, matrix_in)

    start_time = time.time()

    _, Recover_testX = M_RNN(trainZ, trainM, trainT, testZ, testM, testT,
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


# TODO: To have less issues with Django imports, duplicate Data_Loader.py here:
# %% Google data loading

'''
1. train_rate: training / testing set ratio
2. missing_rate: the amount of introducing missingness
'''


def Data_Loader_Incomplete(seq_length, filename):
    # %% Normalization
    def MinMaxScaler(data):
        dmin = np.nanmin(data, 0)
        dmax = np.nanmax(data, 0)
        numerator = data - dmin
        denominator = dmax - dmin
        return numerator / (denominator + 1e-8), dmin, dmax

    # %% Data Preprocessing
    xy = np.loadtxt(filename, delimiter=" ", skiprows=0)
    # xy = xy[::-1]
    xy, dmin, dmax = MinMaxScaler(xy)
    x = xy

    # %% Parameters
    col_no = len(x[0, :])
    row_no = len(x[:, 0]) - seq_length

    # Dataset build
    dataX = []
    for i in range(0, len(x[:, 0]) - seq_length):
        _x = x[i:i + seq_length]
        dataX.append(_x)

    train_size = 0

    for i in range(0, len(x)):
        anynan = False

        for j in range(0, len(x[i])):
            if np.isnan(x[i][j]):
                anynan = True

        if anynan:
            train_size = i - int(i / 3.0)
            break

    # %% Introduce Missingness (MCAR)

    dataZ = []
    dataM = []
    dataT = []

    for i in range(row_no):

        # %% Missing matrix construct
        m = np.ones([seq_length, col_no])
        m[np.where(np.isnan(dataX[i]) == 1)] = 0

        dataM.append(m)

        # %% Introduce missingness to the original data
        z = np.copy(dataX[i])
        z[np.where(m == 0)] = 0

        dataZ.append(z)

        # %% Time gap generation
        t = np.ones([seq_length, col_no])
        for j in range(col_no):
            for k in range(seq_length):
                if (k > 0):
                    if (m[k, j] == 0):
                        t[k, j] = t[k - 1, j] + 1

        dataT.append(t)

    # %% Building the dataset
    '''
    X: Original Feature
    Z: Feature with Missing
    M: Missing Matrix
    T: Time Gap
    '''

    # %% Train / Test Division
    # train_size = int(len(dataX) * train_rate)

    trainX, testX = np.array(dataX[0:train_size]), np.array(dataX[train_size:len(dataX)])
    trainZ, testZ = np.array(dataZ[0:train_size]), np.array(dataZ[train_size:len(dataX)])
    trainM, testM = np.array(dataM[0:train_size]), np.array(dataM[train_size:len(dataX)])
    trainT, testT = np.array(dataT[0:train_size]), np.array(dataT[train_size:len(dataX)])

    return [trainX, trainZ, trainM, trainT, testX, testZ, testM, testT, dmin, dmax, train_size, x]


'''    
#%% Data with missingness

xy = np.loadtxt('/home/jinsung/Documents/Jinsung/MRNN/MRNN_New_Revision/Data/GOOGLE_Missing.csv', delimiter = ",",skiprows = 1)
row_no = len(xy[:,0])
col_no = len(xy[0,:])

temp_m = np.random.uniform(0,1,[row_no, col_no]) 
m = np.zeros([row_no, col_no])
m[np.where(temp_m >= 0.2)] = 1

xy[np.where(m==0)] = np.nan

np.savetxt('/home/jinsung/Documents/Jinsung/MRNN/MRNN_New_Revision/Data/GOOGLE_Missing.csv',xy)
'''