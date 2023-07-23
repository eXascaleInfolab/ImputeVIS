import numpy as np
import time
import json
import skopt
from skopt import Optimizer
from typing import List, Optional, Tuple, Union, Any


def json_serializable(item: Any) -> Union[int, float, list, dict, tuple, str]:
    """
    Convert objects, especially numpy objects, to native Python objects for JSON serialization.

    Parameters
    ----------
    item : Any
        The item or object to be converted to a JSON serializable format.

    Returns
    -------
    Union[int, float, list, dict, tuple, str]
        The item converted to a Python native format suitable for JSON serialization.

    Raises
    ------
    TypeError
        If the item is of a type that is not serializable.
    """

    if isinstance(item, (np.integer, np.int64)):  # Added np.int64 for clarity
        return int(item)
    elif isinstance(item, (np.floating, float)):
        return float(item)
    elif isinstance(item, np.ndarray):
        return item.tolist()
    elif isinstance(item, tuple):
        return tuple(json_serializable(i) for i in item)
    elif isinstance(item, list):
        return [json_serializable(i) for i in item]
    elif isinstance(item, dict):
        return {k: json_serializable(v) for k, v in item.items()}
    elif isinstance(item, (str, int)):  # Allow native Python str and int types
        return item
    else:
        raise TypeError(f"Type {type(item)} not serializable")
