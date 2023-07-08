import numpy as np
from sklearn.metrics import mean_squared_error
from typing import Dict, List

import Optimizer.algorithm_parameters as alg_params
from Utils_Thesis import statistics
from Wrapper import algo_collection


def evaluate_params(ground_truth_matrix: np.ndarray, obfuscated_matrix: np.ndarray, rank: int, eps: float, iters: int,
                    selected_metrics: List[str]) -> Dict[str, float]:
    """
    Evaluate various statistics for given parameters.

    Parameters
    ----------
    ground_truth_matrix : np.ndarray
        The original unobfuscated matrix.
    obfuscated_matrix : np.ndarray
        The obfuscated matrix.
    rank : int
        The rank parameter for the native_cdrec_param algorithm.
    eps : float
        The eps parameter for the native_cdrec_param algorithm.
    iters : int
        The iters parameter for the native_cdrec_param algorithm.
    selected_metrics : List[str]
        List of selected metrics to compute.

    Returns
    -------
    dict
        A dictionary of computed statistics.
    """

    recovered_matrix = algo_collection.native_cdrec_param(obfuscated_matrix, rank, eps, iters)
    error_measures = {}

    # if 'mse' in selected_metrics:
    #     error_measures['mse'] = mean_squared_error(ground_truth_matrix, recovered_matrix)
    if 'rmse' in selected_metrics:
        error_measures['rmse'] = statistics.determine_rmse(ground_truth_matrix, recovered_matrix,
                                                           obfuscated_matrix)
    if 'mae' in selected_metrics:
        error_measures['mae'] = statistics.determine_mae(ground_truth_matrix, recovered_matrix,
                                                         obfuscated_matrix)
    if 'mi' in selected_metrics:
        error_measures['mi'] = statistics.determine_mutual_info(ground_truth_matrix, recovered_matrix,
                                                                obfuscated_matrix)
    if 'corr' in selected_metrics:
        error_measures['corr'] = statistics.determine_correlation(ground_truth_matrix, recovered_matrix,
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
                       selected_metrics: List[str]) -> tuple:
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

    Returns
    -------
    tuple
        The configuration with the lowest average selected error measures.
    """

    num_configs = 50  # number of configurations to try
    num_iterations = 5
    configs = [(np.random.choice(alg_params.cdrec_rank_range), np.random.choice(alg_params.cdrec_eps_range), np.random.choice(alg_params.cdrec_iters_range)) for _ in
               range(num_configs)]

    for i in range(num_iterations):
        scores = [select_and_average_errors(
            evaluate_params(ground_truth_matrix, obfuscated_matrix, *config, selected_metrics), selected_metrics) for
            config in configs]
        top_configs_idx = np.argsort(scores)[:len(configs) // 2]
        configs = [configs[i] for i in top_configs_idx]

    return min(configs, key=lambda config: select_and_average_errors(
        evaluate_params(ground_truth_matrix, obfuscated_matrix, *config, selected_metrics), selected_metrics))


if __name__ == '__main__':
    print(successive_halving(
        np.loadtxt("../Datasets/bafu/raw_matrices/BAFU_tiny.txt", delimiter=" ", ),
        np.loadtxt("../Datasets/bafu/obfuscated/BAFU_tiny_obfuscated_40.txt", delimiter=" ", ),
        ['mae', 'rmse']
    ))
