import numpy as np
from skopt import Optimizer

from skopt.utils import use_named_args
from typing import Dict, List

from Optimizer.algorithm_parameters import SEARCH_SPACES

# Define the search space for each algorithm separately
search_spaces = SEARCH_SPACES


# Import the 'evaluate_params' function from the 'successive_halving' module
from successive_halving import evaluate_params


def bayesian_optimization(ground_truth_matrix: np.ndarray, obfuscated_matrix: np.ndarray,
                          selected_metrics: List[str], algorithm: str) -> Dict[str, float]:
    """
    Conduct the Bayesian optimization hyperparameter optimization.

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
    dict
        The best parameters and their corresponding scores.
    """

    # Define the search space
    space = search_spaces[algorithm]

    # Define the objective function (to minimize)
    @use_named_args(space)
    def objective(**params):
        errors = evaluate_params(ground_truth_matrix, obfuscated_matrix, algorithm, tuple(params.values()), selected_metrics)
        return np.mean([errors[metric] for metric in selected_metrics])

    # Conduct Bayesian optimization
    optimizer = Optimizer(space)
    for i in range(50):
        suggested_params = optimizer.ask()
        score = objective(suggested_params)
        optimizer.tell(suggested_params, score)

    # Optimal parameters
    optimal_params = optimizer.Xi[np.argmin(optimizer.yi)]
    optimal_params_dict = {name: value for name, value in zip([dim.name for dim in space], optimal_params)}

    return optimal_params_dict, np.min(optimizer.yi)


if __name__ == '__main__':
    algo = "cdrec"  # choose an algorithm to optimize
    raw_matrix = np.loadtxt("../Datasets/bafu/raw_matrices/BAFU_tiny.txt", delimiter=" ", )
    obf_matrix = np.loadtxt("../Datasets/bafu/obfuscated/BAFU_tiny_obfuscated_10.txt", delimiter=" ", )

    best_params, best_score = bayesian_optimization(
        raw_matrix,
        obf_matrix,
        ['rmse'],  # choose one or more metrics to optimize
        algo
    )

    print(f"Best parameters for {algo}: {best_params}")
    print(f"Best score: {best_score}")