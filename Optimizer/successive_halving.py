import numpy as np
from sklearn.metrics import mean_squared_error
from typing import Dict, List
import re
import M_RNN
import Optimizer.algorithm_parameters as alg_params

import sys
import os
import Wrapper.algo_collection

sys.path.insert(0, os.path.abspath(".."))  # Add parent directory to path for imports to work
from Utils_Thesis import statistics

import IIM.iim as iim_alg
import M_RNN.testerMRNN
import M_RNN.Data_Loader


def evaluate_params(ground_truth_matrix: np.ndarray, obfuscated_matrix: np.ndarray, algorithm: str, config: tuple,
                    selected_metrics: List[str]) -> Dict[str, float]:
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
        List of selected metrics to compute.

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
        hidden_dim, learning_rate, iterations, keep_prob, seq_len = config
        recovered_matrix = M_RNN.testerMRNN.mrnn_recov_with_data(obfuscated_matrix_copy, runtime=0,
                                                                 hidden_dim=hidden_dim,
                                                                 learning_rate=learning_rate,
                                                                 iterations=iterations,
                                                                 keep_prob=keep_prob,
                                                                 seq_length=seq_len)
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
        error_measures['mi'] = 1 - statistics.determine_mutual_info(ground_truth_matrix, recovered_matrix,
                                                                    obfuscated_matrix)
    if 'corr' in selected_metrics:
        error_measures['corr'] = 1 - statistics.determine_correlation(ground_truth_matrix, recovered_matrix,
                                                                      obfuscated_matrix)

    return error_measures


def select_and_average_errors(errors_dict: Dict[str, float], selected_metrics: List[str]) -> float:
    """
    Select and average specified errors.

    Parameters
    ----------
    errors_dict : dict
        Dictionary of computed error measures.
    selected_metrics : list
        List of selected metrics to average.

    Returns
    -------
    float
        The average of the selected error measures.
    """

    selected_errors = [errors_dict[metric] for metric in selected_metrics]
    return np.mean(selected_errors)


def successive_halving(ground_truth_matrix: np.ndarray, obfuscated_matrix: np.ndarray,
                       selected_metrics: List[str], algorithm: str) -> tuple:
    """
    Conduct the successive halving hyperparameter optimization.

    Parameters
    ----------
    ground_truth_matrix : np.ndarray
        The original unobfuscated matrix.
    obfuscated_matrix : np.ndarray
        The obfuscated matrix.
    selected_metrics : list
        List of selected metrics to consider for optimization.
    algorithm : str
        The algorithm to use.
        Valid values: 'cdrec', 'mrnn', 'stmvl', 'iim'

    Returns
    -------
    tuple
        The configuration with the lowest average selected error measures.
    """

    num_configs = 10  # number of configurations to try
    num_iterations = 5

    # prepare configurations for each algorithm separately
    if algorithm == 'cdrec':
        configs = [(np.random.choice(alg_params.CDREC_RANK_RANGE),
                    np.random.choice(alg_params.CDREC_EPS_RANGE),
                    np.random.choice(alg_params.CDREC_ITERS_RANGE)) for _ in range(num_configs)]
    elif algorithm == 'iim':
        configs = [(np.random.choice(alg_params.IIM_LEARNING_NEIGHBOR_RANGE))
                   for _ in range(num_configs)]
    elif algorithm == 'mrnn':
        configs = [(np.random.choice(alg_params.MRNN_HIDDEN_DIM_RANGE),
                    np.random.choice(alg_params.MRNN_LEARNING_RATE_CHANGE),
                    np.random.choice(alg_params.MRNN_NUM_ITER_RANGE),
                    np.random.choice(alg_params.MRNN_KEEP_PROB_RANGE),
                    np.random.choice(alg_params.MRNN_SEQ_LEN_RANGE)) for _ in range(num_configs)]
    elif algorithm == 'stmvl':
        configs = [(np.random.choice(alg_params.STMVL_WINDOW_SIZE_RANGE),
                    np.random.choice(alg_params.STMVL_GAMMA_RANGE),
                    np.random.choice(alg_params.STMVL_ALPHA_RANGE)) for _ in range(num_configs)]
    else:
        raise ValueError(f"Invalid algorithm: {algorithm}")

    for i in range(num_iterations):
        scores = [select_and_average_errors(
            evaluate_params(ground_truth_matrix, obfuscated_matrix, algorithm, config, selected_metrics),
            selected_metrics) for
            config in configs]
        top_configs_idx = np.argsort(scores)[:max(1, len(configs) // 2)]
        configs = [configs[i] for i in top_configs_idx]

    if not configs:
        raise ValueError("No configurations left after successive halving.")

    return min(configs, key=lambda config: select_and_average_errors(
        evaluate_params(ground_truth_matrix, obfuscated_matrix, algorithm, config, selected_metrics), selected_metrics))


if __name__ == '__main__':
    algo = "mrnn"
    raw_matrix = np.loadtxt("../Datasets/bafu/raw_matrices/BAFU_tiny.txt", delimiter=" ", )
    obf_matrix = np.loadtxt("../Datasets/bafu/obfuscated/BAFU_tiny_obfuscated_10.txt", delimiter=" ", )

    print(successive_halving(
        raw_matrix,
        obf_matrix,
        ['rmse'],
        algo
    ))
