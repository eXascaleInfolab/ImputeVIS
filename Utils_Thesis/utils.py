import numpy as np
import glob
import os
import random
import fnmatch
from typing import Optional


def obfuscate_data(filename_input: str, percentage: int, output_dir: str, rows_to_skip_percentage=5,
                   allow_full_nan_line=False):
    """
    This function obfuscates a given percentage of data in a given file by replacing it with NaN.

    Parameters:
    -----------
    filename_input : str
        The path to the input file, relative to the current directory.
    percentage : int
        The percentage of data to replace with NaN.
    output_dir: str
        The directory where the obfuscated data will be saved.
    rows_to_skip_percentage: int, optional
        The percentage of rows to skip from the beginning. Defaults to 5.
    allow_full_nan_line : bool, optional
        Whether to allow lines that are entirely NaN.
        Defaults to False.

    Returns:
    --------
    filename_output : str
        The path to the obfuscated output file, relative to the current directory.
    """
    skiprows = 0
    with open(filename_input, 'r') as file:
        first_line = file.readline().strip()  # read the first line of the file
        try:
            # try to convert to a float (or any numeric type)
            np.array(first_line.split(), dtype=float)
        except ValueError:
            # if it fails, we know it's a header line and we should skip it
            skiprows = 1

    # Load the data from the input file, adjust delimiter and skiprows as needed.
    data = np.loadtxt(filename_input, delimiter=' ', skiprows=skiprows)

    # Keep a copy of the original data for restoring values.
    original_data = data.copy()

    # Calculate the total number of elements in the data.
    total_elements = data.size

    # Calculate the number of elements to replace with NaN.
    num_nan = max(1, int(total_elements * percentage / 100))

    # Get the shape of the data array for indexing.
    shape = data.shape

    # Calculate rows to skip based on the given percentage.
    rows_to_skip = max(int(shape[0] * rows_to_skip_percentage / 100), rows_to_skip_percentage * 10)

    # Generate random indices for the elements to be replaced.
    random.seed(6)
    try:
        indices = random.sample(range(rows_to_skip * shape[1], total_elements), num_nan)
    except ValueError:
        print(f'Not enough elements for obfuscation in file {filename_input} after skipping rows. File skipped.')
        return None  # Return None to indicate that the file was skipped.

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

    # Construct the output filename.
    # output_dir = os.path.join('../timeSeriesImputerParameterizer', '..', 'Datasets', 'bafu', 'obfuscated')
    filename_output = os.path.join(output_dir, os.path.splitext(os.path.basename(filename_input))[
        0] + f'_obfuscated_{percentage}.txt')

    # Create the output directory if it does not exist.
    os.makedirs(output_dir, exist_ok=True)

    # Save the obfuscated data to the output file.
    np.savetxt(filename_output, data, delimiter=' ', fmt='%f')

    return filename_output


def automate_obfuscate(input_directory: str, output_dir: str):
    # Use the function with the matching file(s) and obfuscate 1%, 5%, 10%, 20%, 40% and 80% of its data with NaN.
    for dataset_name in ['bafu', 'chlorine', 'climate', 'electricity', 'meteo']:
        input_dir = os.path.join(input_directory, dataset_name, 'raw_matrices')
        dataset_output_dir = os.path.join(output_dir, dataset_name,
                                          'obfuscated')  # Create a new output directory variable for this dataset
        for filename in get_files(input_dir):
            for percentage in [1, 5, 10, 20, 40, 60, 80]:
                filename_output = obfuscate_data(filename, percentage, dataset_output_dir, allow_full_nan_line=True)
                if filename_output is None:  # If the file was skipped, continue with the next file.
                    continue

    # Special case for 'drift'
    drift_dir = os.path.join(input_directory, 'drift', 'drift10', 'raw_matrices')
    drift_output_dir = os.path.join(output_dir, 'drift', 'drift10',
                                    'obfuscated')  # Create a new output directory variable for the 'drift' dataset
    for filename in get_files(drift_dir):
        for percentage in [1, 5, 10, 20, 40, 60, 80]:
            filename_output = obfuscate_data(filename, percentage, drift_output_dir, allow_full_nan_line=True)
            if filename_output is None:  # If the file was skipped, continue with the next file.
                continue


def process_directory(input_directory: str, output_dir: str):
    # Iterate over the .txt and .csv files in the given directory and call the obfuscate_data function for each one.
    for filename in glob.glob(os.path.join(input_directory, '*')):
        if filename.endswith('.txt') or filename.endswith('.csv'):
            automate_obfuscate(input_directory, output_dir)


def get_files(directory: str, file_extensions=[".txt", ".csv"]) -> list:
    """
    This function returns a list of file paths from a given directory.

    Parameters:
    -----------
    directory : str
        The path to the directory from which to get the files.
    file_extensions : list, optional
        List of file extensions to be considered. Defaults to ".txt" and ".csv".

    Returns:
    --------
    files : list
        A list of file paths.
    """
    files = []
    for extension in file_extensions:
        files.extend(glob.glob(os.path.join(directory, f"*{extension}")))
    return files


def split_file_lines(input_folder: str):
    """
    Iterates over each file in a directory, splits the content of the file into 1/2 and 1/4 based on number of lines,
    and writes the split contents into new files. The new files have the same name as the original files, but
    with '_half' and '_quarter' appended to the base of the filename.

    Parameters
    ----------
    input_folder : str
        The path to the directory containing the files to be split.

    Returns
    -------
    None

    Notes
    -----
    This function does not return any value. It writes the split contents directly to new files in
    the same directory as the original files. The function does not check if a file is a text file
    before trying to split it, so it should be used with directories containing only text files that
    can be split by lines.
    """

    # Iterate over all files in the input directory
    for filename in os.listdir(input_folder):
        filepath = os.path.join(input_folder, filename)

        # Skip if it's a directory
        if os.path.isdir(filepath):
            continue

        # Load all lines from the file
        with open(filepath, 'r') as file:
            lines = file.readlines()

        # Split the lines into halves and quarters
        half_lines = lines[:len(lines) // 2]
        quarter_lines = lines[:len(lines) // 4]

        # Save the halves and quarters to new files
        base, ext = os.path.splitext(filename)
        with open(os.path.join(input_folder, f'{base}_half{ext}'), 'w') as file:
            file.writelines(half_lines)

        with open(os.path.join(input_folder, f'{base}_quarter{ext}'), 'w') as file:
            file.writelines(quarter_lines)


if __name__ == '__main__':
    # split_file_lines(os.path.join('../timeSeriesImputerParameterizer', '..', 'Datasets', 'bafu', 'raw_matrices'))
    # Define the output directory
    # output_dir = os.path.join('../timeSeriesImputerParameterizer', '..', 'Datasets', 'bafu', 'obfuscated')
    # Define the input directory
    # input_directory = os.path.join('../timeSeriesImputerParameterizer', '..', 'Datasets', 'bafu', 'raw_matrices')
    # automate_obfuscate(input_directory, output_dir)
    # Define the root directories
    root_input_directory = os.path.join('../timeSeriesImputerParameterizer', '..', 'Datasets')
    root_output_directory = os.path.join('../timeSeriesImputerParameterizer', '..', 'Datasets')

    # Run the automation
    automate_obfuscate(root_input_directory, root_output_directory)


def find_obfuscated_file(target_dir: str, start_string: str) -> Optional[str]:
    """
    Searches a specified directory and its sub-directories named "obfuscated" for a file
    that starts with the specified string and also contains "obfuscated",
    and returns the absolute path of the first match.

    Parameters
    ----------
    target_dir : str
        The path to the directory where the search should start.
    start_string : str
        The string that the beginning of the filename should match.

    Returns
    -------
    str or None
        The absolute path to the first file that matches the start_string and contains "obfuscated",
        or None if no matching file is found.

    Examples
    --------
    >>> find_obfuscated_file('/path/to/your/folder', 'obfuscated')
    '/path/to/your/folder/obfuscated/obfuscated_example.txt'
    """
    for dirpath, dirs, files in os.walk(target_dir):
        if 'obfuscated' in dirpath:
            for filename in fnmatch.filter(files, start_string + '*.txt'):
                return os.path.abspath(os.path.join(dirpath, filename))

    return None


def find_non_obfuscated_file(target_dir: str, start_string: str) -> Optional[str]:
    """
    Searches a specified directory and its sub-directories not named "obfuscated" for a file
    that starts with the specified string and does not contain "NaN",
    and returns the absolute path of the first match.

    Parameters
    ----------
    target_dir : str
        The path to the directory where the search should start.
    start_string : str
        The string that the beginning of the filename should match.

    Returns
    -------
    str or None
        The absolute path to the first file that matches the start_string and does not contain "NaN",
        or None if no matching file is found.

    Examples
    --------
    >>> find_non_obfuscated_file('/path/to/your/folder', 'your_string')
    '/path/to/your/folder/your_string_example.txt'
    """
    for dirpath, dirs, files in os.walk(target_dir):
        if 'obfuscated' not in dirpath:
            for filename in fnmatch.filter(files, start_string + '*'):
                if 'NaN' not in filename:
                    return os.path.abspath(os.path.join(dirpath, filename))

    return None
