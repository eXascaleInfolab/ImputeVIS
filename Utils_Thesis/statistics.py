import numpy as np
from sklearn.feature_selection import mutual_info_regression
from sklearn.metrics import normalized_mutual_info_score, mutual_info_score
from scipy.stats import pearsonr, entropy
import sys
import os


def determine_rmse(ground_truth_matrix: np.ndarray, imputed_matrix: np.ndarray, obfuscated_matrix: np.ndarray):
    """Determines the RMSE between the ground truth and the imputed matrix.

    Parameters
    ----------
    ground_truth_matrix : numpy.ndarray
        The ground truth matrix.
    imputed_matrix : numpy.ndarray
        The imputed matrix.
    obfuscated_matrix : numpy.ndarray
        The obfuscated matrix.

    Returns
    -------
    float
        The RMSE between the ground truth and the imputed matrix as a float.


    """
    nan_locations = np.isnan(obfuscated_matrix)
    ground_truth_values = ground_truth_matrix[nan_locations]
    imputed_values = imputed_matrix[nan_locations]

    individual_rmse = (ground_truth_values - imputed_values) ** 2
    rmse = np.sqrt(np.mean(individual_rmse))
    return float(rmse)


def determine_mae(ground_truth_matrix: np.ndarray, imputed_matrix: np.ndarray, obfuscated_matrix: np.ndarray):
    """
    Calculate the Mean Absolute Error (MAE) between ground truth data and imputed data.

    Parameters
    ----------
    ground_truth_matrix : numpy.ndarray
        The ground truth matrix.
    imputed_matrix : numpy.ndarray
        The imputed matrix.
    obfuscated_matrix : numpy.ndarray
        The obfuscated matrix

    Returns
    -------
    float
        The MAE between the ground truth and the imputed matrix.
    """

    nan_locations = np.isnan(obfuscated_matrix)
    ground_truth_values = ground_truth_matrix[nan_locations]
    imputed_values = imputed_matrix[nan_locations]

    individual_errors = np.abs(ground_truth_values - imputed_values)
    mae = np.mean(individual_errors)
    return float(mae)


def determine_mutual_info(ground_truth_matrix: np.ndarray, imputed_matrix: np.ndarray, nan_matrix: np.ndarray):
    """
    Calculate the mutual information between ground truth data and imputed data.
    https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.mutual_info_regression.html

    Parameters
    ----------
    ground_truth_matrix : numpy.ndarray
        The ground truth matrix.
    imputed_matrix : numpy.ndarray
        The imputed matrix.
    nan_matrix : numpy.ndarray
        The matrix with NaN values.

    Returns
    -------
    mi : numpy.ndarray
        Mutual information between the imputed matrix and the ground truth matrix.

    Raises
    ------
    ValueError
        If the shapes of ground_truth_matrix and imputed_matrix are not the same.
    """

    # Check if the matrices have the same shape, otherwise raise an error
    if ground_truth_matrix.shape != imputed_matrix.shape:
        raise ValueError("The shapes of ground_truth_matrix and imputed_matrix are not the same")

    # Get locations of NaN values in the nan_matrix
    nan_locations = np.isnan(nan_matrix)

    # Flatten ground_truth_matrix to be used as the target vector
    target_vector = ground_truth_matrix[nan_locations].flatten()

    # Calculate mutual information between imputed_matrix and target_vector
    mi = mutual_info_regression(imputed_matrix[nan_locations].reshape(-1, 1), target_vector, random_state=42)

    # print("Mutual information:", mi)
    return float(mi[0])


def normalized_mutual_info(ground_truth_matrix: np.ndarray, imputed_matrix: np.ndarray, nan_matrix: np.ndarray):
    """
    Calculate the normalized mutual information between ground truth data and imputed data.

    Parameters
    ----------
    ground_truth_matrix : numpy.ndarray
        The ground truth matrix.
    imputed_matrix : numpy.ndarray
        The imputed matrix.
    nan_matrix : numpy.ndarray
        The matrix with NaN values.

    Returns
    -------
    nmi : float
        Normalized mutual information between the imputed matrix and the ground truth matrix.

    Raises
    ------
    ValueError
        If the shapes of ground_truth_matrix and imputed_matrix are not the same.
    """

    # Check if the matrices have the same shape, otherwise raise an error
    if ground_truth_matrix.shape != imputed_matrix.shape:
        raise ValueError("The shapes of ground_truth_matrix and imputed_matrix are not the same")

    # Get locations of NaN values in the nan_matrix
    nan_locations = np.isnan(nan_matrix)

    # Flatten ground_truth_matrix to be used as the target vector
    target_vector = ground_truth_matrix[nan_locations].flatten()

    # Flatten imputed matrix
    imputed_vector = imputed_matrix[nan_locations].flatten()

    # Determine number of bins based on the number of NaN values
    num_bins = int(np.sqrt(len(target_vector)))

    # Discretize the data
    target_vector_discretized, _ = np.histogram(target_vector, bins=num_bins)
    imputed_vector_discretized, _ = np.histogram(imputed_vector, bins=num_bins)

    # Calculate mutual information between imputed_matrix and target_vector
    mi = mutual_info_score(target_vector_discretized, imputed_vector_discretized)

    # Calculate entropy of the ground_truth_matrix and imputed_matrix
    h_ground_truth = entropy(target_vector_discretized)
    h_imputed = entropy(imputed_vector_discretized)

    # Calculate normalized mutual information
    nmi = mi / (h_ground_truth + h_imputed)

    return nmi


def determine_correlation(ground_truth_matrix: np.ndarray, imputed_matrix: np.ndarray, obfuscated_matrix: np.ndarray):
    """
    Calculate the Pearson correlation coefficient between ground truth data and imputed data.

    Parameters
    ----------
    ground_truth_matrix : numpy.ndarray
        The ground truth matrix.
    imputed_matrix : numpy.ndarray
        The imputed matrix.
    obfuscated_matrix : numpy.ndarray
        The obfuscated matrix.

    Returns
    -------
    float
        The Pearson correlation coefficient between the ground truth and the imputed matrix.
    """

    nan_locations = np.isnan(obfuscated_matrix)
    ground_truth_values = ground_truth_matrix[nan_locations]
    imputed_values = imputed_matrix[nan_locations]

    correlation, _ = pearsonr(ground_truth_values, imputed_values)
    return float(correlation)



# Uncomment for testing and troubleshooting
# sys.path.insert(0, os.path.abspath(".."))
# determine_rmse(np.loadtxt("D:/Git/msc_thesis_timeseries/Datasets/bafu/raw_matrices/BAFU_tiny.txt"), np.loadtxt("D:/Git/msc_thesis_timeseries/Datasets/bafu/raw_matrices/BAFU_tiny.txt"), np.loadtxt("D:/Git/msc_thesis_timeseries/Datasets/bafu/obfuscated/BAFU_tiny_obfuscated_10.txt"))