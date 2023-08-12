from Utils_Thesis import utils, statistics
import os
import json
import re
import Wrapper.algo_collection
import time
import numpy as np
from typing import Tuple
import algorithm_parameters

# Define the path to the folder
FOLDER_PATH = './metric_specific'

# Define the filename pattern
OPTIMIZATION_RESULTS_PATTERN = re.compile(r"optimization_results_(cdrec|iim|mrnn|stmvl)_(bayesian_optimization|pso|successive_halving)_(rmse|mae|mi|corr|rmse_mae|mi_corr).json")

# All datasets
DATASETS = ['bafu', 'chlorine', 'climate', 'drift', 'meteo']


def get_best_params_by_dataset():
    """
    Get the best parameters for each dataset and algorithm, categorized by dataset

    Returns
    -------
    best_params: dict
        A dictionary with the best parameters for each dataset and algorithm
    """
    # Define the best parameters storage
    best_params = {}
    # Iterate over all files in the folder
    for filename in os.listdir(FOLDER_PATH):
        # If the file matches the pattern
        if OPTIMIZATION_RESULTS_PATTERN.match(filename):
            with open(os.path.join(FOLDER_PATH, filename), 'r') as f:
                data = json.load(f)
                # Extract the algorithm and metric from the filename
                algorithm, optimization_method, metric = OPTIMIZATION_RESULTS_PATTERN.findall(filename)[0]

                for dataset, values in data.items():
                    # If the dataset is not in best_params, add it
                    if dataset not in best_params:
                        best_params[dataset] = {}

                    # By dataset
                    # If the algorithm is not in best_params for the dataset, add it
                    if algorithm not in best_params[dataset]:
                        best_params[dataset][algorithm] = {}

                    if metric not in best_params[dataset][algorithm]:
                        best_params[dataset][algorithm][metric] = {
                            "metric": metric,
                            "best_score": float('inf'),  # set it to infinity initially
                            "best_params": {},
                            "time": float('inf'),  # set it to infinity initially
                            "optimization_method": ""  # initializing with an empty string
                        }

                    # If the current metric's best score is better than the stored one, update it
                    if values["best_score"] < best_params[dataset][algorithm][metric]["best_score"]:
                        best_params[dataset][algorithm][metric]["best_score"] = values["best_score"]
                        best_params[dataset][algorithm][metric]["time"] = values["time"]
                        best_params[dataset][algorithm][metric]["best_params"] = values["best_params"]
                        best_params[dataset][algorithm][metric]["optimization_method"] = optimization_method

    # Save the best_params to a JSON file
    output_file = os.path.join("results", 'best_params_dataset_by_metric.json')
    with open(output_file, 'w') as outfile:
        json.dump(best_params, outfile, indent=4)

    return best_params


def get_best_params_by_algorithm():
    """
    Get the best parameters for each dataset and algorithm, categorized by algorithm

    Returns
    -------
    best_params: dict
        A dictionary with the best parameters for each dataset and algorithm
    """
    # Define the best parameters storage
    best_params = {}

    # Iterate over all files in the folder
    for filename in os.listdir(FOLDER_PATH):
        # If the file matches the pattern
        if OPTIMIZATION_RESULTS_PATTERN.match(filename):
            with open(os.path.join(FOLDER_PATH, filename), 'r') as f:
                data = json.load(f)
                # Extract the algorithm, optimization method, and metric from the filename
                algorithm, optimization_method, metric = OPTIMIZATION_RESULTS_PATTERN.findall(filename)[0]

                # If the algorithm is not in best_params, add it
                if algorithm not in best_params:
                    best_params[algorithm] = {}

                for dataset, values in data.items():
                    # If the dataset is not in best_params for the algorithm, add it
                    if dataset not in best_params[algorithm]:
                        best_params[algorithm][dataset] = {}

                    # Create or update the metric data
                    if metric not in best_params[algorithm][dataset]:
                        best_params[algorithm][dataset][metric] = {
                            "metric": metric,
                            "best_score": float('inf'),  # set it to infinity initially
                            "best_params": {},
                            "time": float('inf'),  # set it to infinity initially
                            "optimization_method": ""  # initializing with an empty string
                        }

                    # If the current metric's best score is better than stored one, update it
                    if values["best_score"] < best_params[algorithm][dataset][metric]["best_score"]:
                        best_params[algorithm][dataset][metric]["best_score"] = values["best_score"]
                        best_params[algorithm][dataset][metric]["time"] = values["time"]
                        best_params[algorithm][dataset][metric]["best_params"] = values["best_params"]
                        best_params[algorithm][dataset][metric]["optimization_method"] = optimization_method

    # Save the best_params to a JSON file
    output_file = os.path.join('results', 'best_params_algorithm_by_metric.json')
    with open(output_file, 'w') as outfile:
        json.dump(best_params, outfile, indent=4)

    return best_params


# TODO Description and know what you want!
def cdrec_optimal_results(results_path: str) -> dict:
    """
    Run imputation using the best parameters and save the results.

    Parameters
    ----------
    results_path : str
        Path to the folder containing the saved 'best_params_output.json'.

    Returns
    -------
    dict
        A dictionary containing the results summary for each dataset and algorithm.
    """
    # Load best_params from the saved JSON file
    with open(os.path.join('results', 'best_params_algorithm_by_metric.json')) as infile:
        best_params = json.load(infile)

    # Define storage for metrics and configuration details
    results_summary = {}

    # Extract 'cdrec' configurations
    cdrec_configs = best_params.get("cdrec", {})

    # Iterate through algorithms and datasets
    for dataset, metrics in cdrec_configs.items():
        for metric_name, config in metrics.items():
            # Get paths for the dataset using the helper function
            raw_file_path, obf_file_path = get_dataset_paths(dataset)

            # Load matrices for the dataset
            ground_truth_matrix = utils.load_and_trim_matrix(raw_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obf_file_path)

            # Extract the best parameters
            rank = config["best_params"]["rank"]
            eps = config["best_params"]["eps"]
            iters = config["best_params"]["iters"]

            # Run the imputation (using CDRec as an example)
            start_time = time.time()
            imputed_matrix = Wrapper.algo_collection.native_cdrec_param(
                __py_matrix=obfuscated_matrix,
                __py_rank=rank,
                __py_eps=float("1" + str(eps)),
                __py_iters=iters
            )
            end_time = time.time()

            corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

            # Create a unique key for results_summary combining dataset and metric_name
            key = f"{dataset}_{metric_name}"

            # Store results
            results_summary[key] = {
                "algorithm": "cdrec",
                "metric_used_for_optimization": config["metric"],
                "optimization_method": config["optimization_method"],
                "best_params": config["best_params"],
                "rmse": rmse,
                "mae": mae,
                "mi": mi,
                "corr": corr,
                "time_taken": end_time - start_time
            }
            print(results_summary[key])

            # Save the imputed matrix to a separate file (using numpy as an example)
            np.save(os.path.join(results_path, f"cdrec_{dataset}_{metric_name}_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'cdrec_optimized_summary_results.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def cdrec_default_results(results_path: str) -> dict:
    """
    Run imputation using the default parameters and save the results.

    Parameters
    ----------
    results_path : str
        Path to the folder containing the saved 'best_params_output.json'.

    Returns
    -------
    dict
        A dictionary containing the results summary for each dataset and algorithm.

    """
    # Define storage for metrics and configuration details
    results_summary = {}

    # Iterate through datasets
    for dataset in DATASETS:
        # Get paths for the dataset using the helper function
        raw_file_path, obf_file_path = get_dataset_paths(dataset)

        # Load matrices for the dataset
        ground_truth_matrix = utils.load_and_trim_matrix(raw_file_path)
        obfuscated_matrix = utils.load_and_trim_matrix(obf_file_path)

        # Run the imputation (using CDRec as an example)
        start_time = time.time()
        imputed_matrix = Wrapper.algo_collection.native_cdrec_param(
            __py_matrix=obfuscated_matrix,
            __py_rank=algorithm_parameters.DEFAULT_PARAMS["cdrec"][0],
            __py_eps=algorithm_parameters.DEFAULT_PARAMS["cdrec"][1],
            __py_iters=algorithm_parameters.DEFAULT_PARAMS["cdrec"][2]
        )
        end_time = time.time()

        corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

        # Store results
        results_summary[dataset] = {
            "algorithm": "cdrec",
            "metric_used_for_optimization": "N/A",
            "optimization_method": "N/A",
            "best_params": {
                "rank": -1,
                "eps": 1.0001,
                "iters": 100
            },
            "rmse": rmse,
            "mae": mae,
            "mi": mi,
            "corr": corr,
            "time_taken": end_time - start_time
        }
        print(results_summary[dataset])

        # Save the imputed matrix to a separate file (using numpy as an example)
        np.save(os.path.join(results_path, f"cdrec_{dataset}_default_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'cdrec_default_summary_results.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary

def determine_metrics(ground_truth_matrix: np.array, imputed_matrix: np.array, obfuscated_matrix: np.array) -> Tuple[float, float, float, float]:
    # Compute metrics
    rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
    mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
    mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix),
                                          obfuscated_matrix)
    corr = statistics.determine_correlation(ground_truth_matrix, np.asarray(imputed_matrix),
                                            obfuscated_matrix)
    return corr, mae, mi, rmse


def get_dataset_paths(dataset: str) -> Tuple[str, str]:
    """
    Given a dataset name, retrieve the paths for raw and obfuscated files.

    Parameters
    ----------
    dataset : str
        Name of the dataset.

    Returns
    -------
    tuple
        Paths for raw and obfuscated files.

    Raises
    ------
    ValueError
        If the provided dataset is not recognized.
    """
    datasets = ['bafu', 'chlorine', 'climate', 'meteo', 'drift']  # Added 'drift' as it was mentioned in your code
    dataset_files = ['BAFU', 'cl2fullLarge', 'climate', 'meteo_total',
                     'batch10']  # Replace 'drift_file' with correct name

    if dataset not in datasets:
        raise ValueError(f"Dataset '{dataset}' not recognized.")

    data_file = dataset_files[datasets.index(dataset)]
    raw_file_path = f"../Datasets/{dataset}/raw_matrices/{data_file}_eighth.txt"
    obf_file_path = f"../Datasets/{dataset}/obfuscated/{data_file}_eighth_obfuscated_10.txt"

    if dataset == 'drift':
        raw_file_path = f"../Datasets/{dataset}/drift10/raw_matrices/{data_file}_eighth.txt"
        obf_file_path = f"../Datasets/{dataset}/obfuscated/{data_file}_eighth_obfuscated_10.txt"

    return raw_file_path, obf_file_path


if __name__ == '__main__':
    #### Step 1: Determine optimal results
    # Get the best params by dataset
    # best_params = get_best_params_by_dataset()
    # Get the best params by algorithm
    # best_params = get_best_params_by_algorithm()

    # Print the best_params
    # print(json.dumps(best_params, indent=4))
    ####

    ##### Step 2: Run imputation using the best params
    cdrec_optimal_results(results_path="results/cdrec")
    cdrec_default_results(results_path="results/cdrec")

    #####




# Load the best_params from the saved JSON file
# with open(output_file, 'r') as infile:
#     loaded_best_params = json.load(infile)

# Use the loaded_best_params as needed. For instance:
# some_function(loaded_best_params["bafu"]["cdrec"]["best_params"])
