import numpy as np
from sklearn.feature_selection import mutual_info_regression
from scipy.stats import pearsonr
import sys
import os


def determine_rmse(ground_truth_matrix, imputed_matrix, obfuscated_matrix):
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
    individual_rmse = []
    tuples_with_nan = np.isnan(obfuscated_matrix).any(axis=1)

    incomplete_tuples_rows = np.array(np.where(tuples_with_nan == True))
    # incomplete_tuples = obfuscated_matrix[incomplete_tuples_rows]
    for row in (incomplete_tuples_rows[0]):
        nan_positions = np.where(np.isnan(obfuscated_matrix[row]) == True)
        # nan_positions = np.where(np.isnan(incomplete_tuples[row]) == True)
        for column in nan_positions[0]:
            ground_truth_value = ground_truth_matrix[row][column]
            imputed_value = imputed_matrix[row][column]
            individual_rmse.append((ground_truth_value - imputed_value) ** 2)
    rmse = np.sqrt(np.mean(individual_rmse))
    return rmse


def determine_mae(ground_truth_matrix, imputed_matrix, obfuscated_matrix):
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

    individual_errors = []
    tuples_with_nan = np.isnan(obfuscated_matrix).any(axis=1)

    incomplete_tuples_rows = np.array(np.where(tuples_with_nan == True))
    for row in (incomplete_tuples_rows[0]):
        nan_positions = np.where(np.isnan(obfuscated_matrix[row]) == True)
        for column in nan_positions[0]:
            ground_truth_value = ground_truth_matrix[row][column]
            imputed_value = imputed_matrix[row][column]
            individual_errors.append(np.abs(ground_truth_value - imputed_value))

    mae = np.mean(individual_errors)
    return mae


def determine_mutual_info(ground_truth_matrix, imputed_matrix, nan_matrix):
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

    print("Mutual information:", mi)
    return mi[0]

def determine_correlation(ground_truth_matrix, imputed_matrix, obfuscated_matrix):
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

    individual_truths = []
    individual_imputations = []
    tuples_with_nan = np.isnan(obfuscated_matrix).any(axis=1)

    incomplete_tuples_rows = np.array(np.where(tuples_with_nan == True))
    for row in (incomplete_tuples_rows[0]):
        nan_positions = np.where(np.isnan(obfuscated_matrix[row]) == True)
        for column in nan_positions[0]:
            ground_truth_value = ground_truth_matrix[row][column]
            imputed_value = imputed_matrix[row][column]
            individual_truths.append(ground_truth_value)
            individual_imputations.append(imputed_value)

    correlation, _ = pearsonr(individual_truths, individual_imputations)
    return correlation



# Uncomment for testing and troubleshooting
# sys.path.insert(0, os.path.abspath(".."))
# determine_rmse(np.loadtxt("D:/Git/msc_thesis_timeseries/Datasets/bafu/raw_matrices/BAFU_tiny.txt"), np.loadtxt("D:/Git/msc_thesis_timeseries/Datasets/bafu/raw_matrices/BAFU_tiny.txt"), np.loadtxt("D:/Git/msc_thesis_timeseries/Datasets/bafu/obfuscated/BAFU_tiny_obfuscated_10.txt"))