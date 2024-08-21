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


    if isinstance(data, np.ndarray):
        flat_data = data.flatten().tolist()
    else:
        flat_data = [float(item) for sublist in data for item in sublist]

    # If the data is a 2D list (similar to what's being read from the file),
    # then flatten it into a 1D list.
    if isinstance(flat_data[0], list):
        flat_data = [float(item) for sublist in flat_data for item in sublist]


    print("%%%%% pycatch22 : ready for pycatch22 %%%%%")

    catch_out = pycatch22.catch22_all(flat_data, catch24=do_catch24)

    feature_names = catch_out['names']
    feature_values = catch_out['values']
    results = {}

    print("%%%%% pycatch22 : Features :")
    for feature_name, feature_value in zip(feature_names, feature_values):
        results[feature_name] = feature_value
        #print('%s : %1.6f' % (feature_name, feature_value))

    return results


def extract_features_naterq(data: ArrayLike, do_catch24: bool, featureCategories, featuresList) -> []:
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

    data = [[0 if num is None else num for num in sublist] for sublist in data]
    data = np.array(data)

    contains_none = np.any(data == None)
    #print(f"Array contains None: {contains_none}")

    if isinstance(data, np.ndarray):
        flat_data = data.flatten().tolist()
    else:
        flat_data = [float(item) for sublist in data for item in sublist]

    # If the data is a 2D list (similar to what's being read from the file),
    # then flatten it into a 1D list.
    if isinstance(flat_data[0], list):
        flat_data = [float(item) for sublist in flat_data for item in sublist]


    #print("%%%%% pycatch22 : ready for pycatch22 %%%%%")

    catch_out = pycatch22.catch22_all(flat_data, catch24=do_catch24)

    feature_names = catch_out['names']
    feature_values = catch_out['values']
    results = {}
    descriptions = []

    for feature_name, feature_value in zip(feature_names, feature_values):
        results[feature_name] = feature_value

        for category, features in featureCategories.items():
            if feature_name in features:
                category_value = category
                break

        feature_description = featuresList.get(feature_name)

        descriptions.append((feature_name, category_value, feature_description))

    print("\n%%%%% pycatch22 : features extracted successfully %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n")

    return results, descriptions