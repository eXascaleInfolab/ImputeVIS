import numpy as np
from sklearn.feature_selection import mutual_info_regression
# https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.mutual_info_regression.html

# Load ground-truth and imputed matrices from text files
ground_truth_matrix = np.loadtxt("../Datasets/bafu/raw_matrices/BAFU_tiny.txt")
nan_matrix = np.loadtxt("../Datasets/bafu/raw_matrices/BAFU_tiny_with_NaN.txt")
imputed_matrix = np.loadtxt("../Results/5l_BAFU_tiny_with_NaN.txt")

# Check if the matrices have the same shape, otherwise raise an error
if ground_truth_matrix.shape != imputed_matrix.shape:
    raise ValueError("The shapes of ground_truth_matrix and imputed_matrix are not the same")


nan_locations = np.isnan(nan_matrix)

# Flatten ground_truth_matrix to be used as the target vector
target_vector = ground_truth_matrix[nan_locations].flatten()

# Calculate mutual information between imputed_matrix and target_vector
mi = mutual_info_regression(imputed_matrix[nan_locations].reshape(-1, 1), target_vector, random_state=42)

print("Mutual information:", mi)

# nan_file_path <- "Datasets/bafu/raw_matrices/BAFU_tiny_with_NaN.txt" # Replace with the path to your file
