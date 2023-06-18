import numpy as np
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


# def determine_mae(ground_truth_matrix, imputed_matrix, obfuscated_matrix):

# Uncomment for testing and troubleshooting
# sys.path.insert(0, os.path.abspath(".."))
# determine_rmse(np.loadtxt("D:/Git/msc_thesis_timeseries/Datasets/bafu/raw_matrices/BAFU_tiny.txt"), np.loadtxt("D:/Git/msc_thesis_timeseries/Datasets/bafu/raw_matrices/BAFU_tiny.txt"), np.loadtxt("D:/Git/msc_thesis_timeseries/Datasets/bafu/obfuscated/BAFU_tiny_obfuscated_10.txt"))