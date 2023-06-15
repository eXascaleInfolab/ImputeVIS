import numpy as np
import os
import random


def obfuscate_data(filename_input, percentage, allow_full_nan_line=False):
    """
    This function obfuscates a given percentage of data in a given file by replacing it with NaN.

    Parameters:
    -----------
    filename_input : str
        The path to the input file, relative to the current directory.
    percentage : int
        The percentage of data to replace with NaN.
    allow_full_nan_line : bool, optional
        Whether to allow lines that are entirely NaN.
        Defaults to False.

    Returns:
    --------
    filename_output : str
        The path to the obfuscated output file, relative to the current directory.
    """

    # Load the data from the input file.
    data = np.loadtxt(filename_input, delimiter=' ')

    # Keep a copy of the original data for restoring values.
    original_data = data.copy()

    # Calculate the total number of elements in the data.
    total_elements = data.size

    # Calculate the number of elements to replace with NaN.
    num_nan = int(total_elements * percentage / 100)

    # Get the shape of the data array for indexing.
    shape = data.shape

    # Generate random indices for the elements to be replaced.
    random.seed(6)
    indices = random.sample(range(total_elements), num_nan)

    # Convert the 1D indices to 2D indices for multi-dimensional data.
    indices = np.unravel_index(indices, shape)

    # Replace the selected elements with NaN.
    data[indices] = np.nan

    # If lines that are entirely NaN are not allowed and such a line exists, retry the obfuscation.
    # If lines that are entirely NaN are not allowed, iteratively update blocks of data until no rows are entirely NaN.
    if not allow_full_nan_line:
        while np.isnan(data).all(axis=1).any():
            # Find the indices of the rows that are entirely NaN.
            nan_rows = np.where(np.isnan(data).all(axis=1))[0]
            for row in nan_rows:
                # Generate a random index for the column.
                col = random.randint(0, shape[1] - 1)
                # Replace the NaN value at the randomly selected index with the original value from the data.
                data[row, col] = original_data[row, col]

    # Create the output directory if it does not exist.
    # output_dir = os.path.join('..', '..', 'Datasets', 'Obfuscated')
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    # Construct the output filename.
    # filename_output = os.path.join(output_dir, os.path.splitext(os.path.basename(filename_input))[0] + f'_obfuscated_{percentage}.txt')
    filename_output = os.path.join('D:/Git/msc_thesis_timeseries/Datasets/bafu/obfuscated',
                                   os.path.splitext(os.path.basename(filename_input))[0] + f'_obfuscated_{percentage}.txt')

    # Save the obfuscated data to the output file.
    np.savetxt(filename_output, data, delimiter=' ', fmt='%f')

    return filename_output


# Use the function with the BAFU file and obfuscate 10%, 20%, 40% and 80% of its data.
for percentage in [10, 20, 40, 60, 80]:
    for proportion in ["_tiny", "_small", ""]:
        # obfuscate_data(os.path.join(D:/Git/msc_thesis_timeseries/Datasets/bafu/raw_matrices/BAFU_{proportion}.txt'), percentage)
        obfuscate_data(os.path.join('..', '..', 'Datasets', 'bafu', 'raw_matrices', f'BAFU{proportion}.txt'),
                       percentage)
