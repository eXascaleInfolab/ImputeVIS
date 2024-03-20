import pycatch22
import numpy as np
from numpy.typing import ArrayLike


def extract_features(data: ArrayLike, do_catch24: bool = True) -> dict:
    """
    Extract features from data using pycatch22.

    Parameters
    ----------
    data : ArrayLike
        Input data array.
    do_catch24 : bool, optional
        Flag to compute the mean and standard deviation. Defaults to True.

    Returns
    -------
    dict
        Dictionary containing feature names and their corresponding values.
    """
    # Check if data is a numpy array
    if isinstance(data, np.ndarray):
        # Flatten the numpy array
        flat_data = data.flatten().tolist()
    else:
        # Assume it's a list-like structure and flatten it
        flat_data = [float(item) for sublist in data for item in sublist]

    # If the data is a 2D list (similar to what's being read from the file),
    # then flatten it into a 1D list.
    if isinstance(flat_data[0], list):
        flat_data = [float(item) for sublist in flat_data for item in sublist]

    catch_out = pycatch22.catch22_all(flat_data, catch24=do_catch24)

    feature_names = catch_out['names']
    feature_values = catch_out['values']
    results = {}

    #print("Extracted features for data with shape ", data.shape)
    for feature_name, feature_value in zip(feature_names, feature_values):
        results[feature_name] = feature_value
        # print('%s : %1.6f' % (feature_name, feature_value))

    return results


# Usage example
# generated_data = np.random.rand(1000)  # Random example data
# extracted_features = extract_features(generated_data)

