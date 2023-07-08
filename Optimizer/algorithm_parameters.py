import numpy as np

# CDRec parameters
cdrec_rank_range = [i for i in range(10)]  # replace with actual range
cdrec_eps_range = np.logspace(-6, 0, num=10)  # log scale for eps
# array([1.e-06, 3.59381366e-06, 1.29154967e-05, 4.64158883e-05,
#        1.66810054e-04, 5.99484250e-04, 2.15443469e-03, 7.74263683e-03,
#        2.78255940e-02, 1.e-01, 1.e+00])
cdrec_iters_range = [i * 100 for i in range(1, 11)]  # replace with actual range

# IIM parameters
learning_neighbor_range = [i for i in range(100)]  # Test up to 100 learning neighbors
# adaptive_range = [True, False]  # Test with and without adaptive learning

# MRNN parameters
mrnn_learning_rate_range = np.logspace(-6, 0, num=20)  # log scale for learning rate
mrnn_hidden_dim_range = [i for i in range(10)]  # hidden dimension
mrnn_seq_len_range = [i for i in range(100)]  # sequence length
mrnn_num_iter_range = [i for i in range(100, 0, 5)]  # number of epochs
mrnn_keep_prob_range = np.logspace(-6, 0, num=10)  # dropout keep probability

# STMVL parameters
stmvl_window_size_range = [i for i in range(2, 100)]  # window size
stmvl_gamma_range = np.logspace(-6, 0, num=10)  # smoothing parameter gamma
stmvl_alpha_range = [i for i in range(10)]  # smoothing parameter alpha
