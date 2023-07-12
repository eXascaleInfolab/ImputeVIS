import numpy as np
import skopt
from skopt import Optimizer

from skopt.utils import use_named_args
from typing import List, Optional, Tuple, Union, Any

from Optimizer.algorithm_parameters import SEARCH_SPACES
import Optimizer.evaluate_params

# Define the search space for each algorithm separately
search_spaces = SEARCH_SPACES


def bayesian_optimization(ground_truth_matrix: np.ndarray, obfuscated_matrix: np.ndarray,
                          selected_metrics: List[str], algorithm: str,
                          n_calls: int = 50, n_random_starts: Optional[int] = None,
                          acq_func: str = 'gp_hedge') -> Tuple[dict, Union[Union[int, float, complex], Any]]:
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
    n_calls: int
        Number of calls to the objective function.
    n_random_starts: Optional[int]
        Number of initial calls to the objective function, from random points.
    acq_func: str
        Function to minimize over the Gaussian prior (one of 'LCB', 'EI', 'PI', 'gp_hedge').

    Returns
    -------
    Tuple[dict, Union[Union[int, float, complex], Any]]
        The best parameters and their corresponding scores.
    """

    # Define the search space
    space = search_spaces[algorithm]

    # Define the objective function (to minimize)
    @use_named_args(space)
    def objective(**params):
        errors = Optimizer.evaluate_params.evaluate_params(ground_truth_matrix, obfuscated_matrix, algorithm, tuple(params.values()),
                                 selected_metrics)
        return np.mean([errors[metric] for metric in selected_metrics])

    # Conduct Bayesian optimization
    optimizer = skopt.Optimizer(dimensions=space, n_random_starts=n_random_starts, acq_func=acq_func)
    for i in range(n_calls):
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
