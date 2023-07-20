import numpy as np
from typing import Dict, List
import Optimizer.algorithm_parameters as alg_params

import sys
import os

import Optimizer.evaluate_params

sys.path.insert(0, os.path.abspath(".."))  # Add parent directory to path for imports to work


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
                       selected_metrics: List[str], algorithm: str,
                       num_configs: int = 10, num_iterations: int = 5,
                       reduction_factor: int = 2) -> tuple:
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
    num_configs: int
        Number of configurations to try.
    num_iterations: int
        Number of iterations to run the optimization.
    reduction_factor: int
        Reduction factor for the number of configurations kept after each iteration.

    Returns
    -------
    tuple
        The configuration with the lowest average selected error measures.
    """

    # Define the parameter names for each algorithm
    param_names = alg_params.PARAM_NAMES

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
                    # np.random.choice(alg_params.MRNN_SEQ_LEN_RANGE)
                    ) for _ in range(num_configs)]
    elif algorithm == 'stmvl':
        configs = [(np.random.choice(alg_params.STMVL_WINDOW_SIZE_RANGE),
                    np.random.choice(alg_params.STMVL_GAMMA_RANGE),
                    np.random.choice(alg_params.STMVL_ALPHA_RANGE)) for _ in range(num_configs)]
    else:
        raise ValueError(f"Invalid algorithm: {algorithm}")

    for i in range(num_iterations):
        scores = [select_and_average_errors(
            Optimizer.evaluate_params.evaluate_params(ground_truth_matrix, obfuscated_matrix, algorithm, config, selected_metrics),
            selected_metrics) for
            config in configs]
        top_configs_idx = np.argsort(scores)[:max(1, len(configs) // reduction_factor)]
        configs = [configs[i] for i in top_configs_idx]

    if not configs:
        raise ValueError("No configurations left after successive halving.")

    best_config = min(configs, key=lambda config: select_and_average_errors(
        Optimizer.evaluate_params.evaluate_params(ground_truth_matrix, obfuscated_matrix, algorithm, config,
                                                  selected_metrics), selected_metrics))
    best_score = select_and_average_errors(
        Optimizer.evaluate_params.evaluate_params(ground_truth_matrix, obfuscated_matrix, algorithm, best_config,
                                                  selected_metrics), selected_metrics)

    # Convert the configuration tuple to a dictionary
    best_config_dict = {name: value for name, value in zip(param_names[algorithm], best_config)}

    return best_config_dict, best_score


if __name__ == '__main__':
    algo = "cdrec"
    raw_matrix = np.loadtxt("../Datasets/bafu/raw_matrices/BAFU_tiny.txt", delimiter=" ", )
    obf_matrix = np.loadtxt("../Datasets/bafu/obfuscated/BAFU_tiny_obfuscated_10.txt", delimiter=" ", )

    print(successive_halving(
        raw_matrix,
        obf_matrix,
        ['rmse'],
        algo
    ))
