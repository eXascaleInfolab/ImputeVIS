import numpy as np
from typing import Dict, List
import re
import M_RNN
from sklearn.metrics import mean_squared_error
from Utils_Thesis import statistics

import IIM.iim as iim_alg
import M_RNN.testerMRNN
import M_RNN.Data_Loader
import Wrapper.algo_collection


def evaluate_params(ground_truth_matrix: np.ndarray, obfuscated_matrix: np.ndarray, algorithm: str, config: tuple,
                    selected_metrics: List[str] = ["rmse"]) -> Dict[str, float]:
    """
    Evaluate various statistics for given parameters.

    Parameters
    ----------
    ground_truth_matrix : np.ndarray
        The original unobfuscated matrix.
    obfuscated_matrix : np.ndarray
        The obfuscated matrix.
    algorithm : str
        The algorithm to use.
        Valid values: 'cdrec', 'mrnn', 'stmvl', 'iim'
    config : tuple
        The configuration of the algorithm.
    selected_metrics : List[str]
        List of selected metrics to compute. Defaults to ["rmse"].

    Returns
    -------
    dict
        A dictionary of computed statistics.
    """
    obfuscated_matrix_copy = np.copy(obfuscated_matrix)
    if algorithm == 'cdrec':
        rank, eps, iters = config
        recovered_matrix = Wrapper.algo_collection.native_cdrec_param(obfuscated_matrix_copy, rank, eps, iters)
    elif algorithm == 'iim':
        learning_neighbours = config
        alg_code = "iim " + re.sub(r'[\W_]', '', str(learning_neighbours))
        recovered_matrix = iim_alg.impute_with_algorithm(alg_code, obfuscated_matrix_copy)
    elif algorithm == 'mrnn':
        hidden_dim, learning_rate, iterations, keep_prob = config
        # hidden_dim, learning_rate, iterations, keep_prob, seq_len = config
        recovered_matrix = M_RNN.testerMRNN.mrnn_recov_with_data(obfuscated_matrix_copy, runtime=0,
                                                                 hidden_dim=hidden_dim,
                                                                 learning_rate=learning_rate,
                                                                 iterations=iterations,
                                                                 keep_prob=keep_prob,
                                                                 # seq_length=seq_len
                                                                 )
        recovered_matrix = np.array(recovered_matrix)
    elif algorithm == 'stmvl':
        window_size, gamma, alpha = config
        recovered_matrix = Wrapper.algo_collection.native_stmvl_param(
            __py_matrix=obfuscated_matrix_copy,
            __py_window=int(window_size),
            __py_gamma=float(gamma),
            __py_alpha=int(alpha)
        )
    else:
        raise ValueError(f"Invalid algorithm: {algorithm}")
    error_measures = {}

    if 'mse' in selected_metrics:
        error_measures['mse'] = mean_squared_error(ground_truth_matrix, recovered_matrix)
    if 'rmse' in selected_metrics:
        error_measures['rmse'] = statistics.determine_rmse(ground_truth_matrix, recovered_matrix,
                                                           obfuscated_matrix)
    if 'mae' in selected_metrics:
        error_measures['mae'] = statistics.determine_mae(ground_truth_matrix, recovered_matrix,
                                                         obfuscated_matrix)
    if 'mi' in selected_metrics:
        error_measures['mi'] = 1 - statistics.normalized_mutual_info(ground_truth_matrix, recovered_matrix,
                                                                           obfuscated_matrix)
    if 'corr' in selected_metrics:
        error_measures['corr'] = 1 - statistics.determine_correlation(ground_truth_matrix, recovered_matrix,
                                                                      obfuscated_matrix)

    return error_measures
