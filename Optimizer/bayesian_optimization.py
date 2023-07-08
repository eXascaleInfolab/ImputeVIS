from skopt import gp_minimize
from skopt.space import Integer, Real
from skopt.utils import use_named_args

# Define the search space
space  = [Integer(0, 10, name='rank'),
          Real(1e-6, 1, "log-uniform", name='eps'),
          Integer(100, 1000, name='iters')]

# Define the objective function (to minimize)
@use_named_args(space)
def objective(**params):
    return evaluate_params(matrix, params['rank'], params['eps'], params['iters'])

res_gp = gp_minimize(objective, space, n_calls=50, random_state=0)

# Optimal parameters
optimal_params = res_gp.x
