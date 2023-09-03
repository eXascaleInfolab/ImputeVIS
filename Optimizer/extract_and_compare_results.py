import M_RNN
import M_RNN.testerMRNN
import M_RNN.Data_Loader
from Optimizer import util
from Utils_Thesis import utils, statistics
import os
import json
import re
import Wrapper.algo_collection
import time
import numpy as np
from typing import Tuple
import algorithm_parameters
import IIM.iim as iim_alg
import glob

# Define the path to the folder
FOLDER_PATH = './metric_specific'

# Define the filename pattern
OPTIMIZATION_RESULTS_PATTERN = re.compile(
    r"optimization_results_(cdrec|iim|mrnn|stmvl)_(bayesian_optimization|pso|succesive_halving)_(rmse_mae|mi_corr|rmse|mae|mi|corr).json")

# All datasets
DATASETS = ['bafu', 'chlorine', 'climate', 'drift', 'meteo']

HIGHER_IS_BETTER = {"mi", "corr"}


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
                        if metric in HIGHER_IS_BETTER:
                            initial_best_score = float('-inf')
                        else:
                            initial_best_score = float('inf')
                        best_params[dataset][algorithm][metric] = {
                            "metric": metric,
                            "best_score": initial_best_score,  # set it to infinity initially
                            "best_params": {},
                            "time": float('inf'),  # set it to infinity initially
                            "optimization_method": ""  # initializing with an empty string
                        }

                    is_better = False
                    if metric in HIGHER_IS_BETTER:
                        if values["best_score"] > best_params[dataset][algorithm][metric]["best_score"]:
                            is_better = True
                    else:
                        if values["best_score"] < best_params[dataset][algorithm][metric]["best_score"]:
                            is_better = True

                    if is_better:
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
                        if metric in HIGHER_IS_BETTER:
                            initial_best_score = float('-inf')
                        else:
                            initial_best_score = float('inf')
                        best_params[algorithm][dataset][metric] = {
                            "metric": metric,
                            "best_score": initial_best_score,  # set it to infinity initially
                            "best_params": {},
                            "time": float('inf'),  # set it to infinity initially
                            "optimization_method": ""  # initializing with an empty string
                        }

                    is_better = False
                    if metric in HIGHER_IS_BETTER:
                        if values["best_score"] > best_params[algorithm][dataset][metric]["best_score"]:
                            is_better = True
                    else:
                        if values["best_score"] < best_params[algorithm][dataset][metric]["best_score"]:
                            is_better = True

                    if is_better:
                        best_params[algorithm][dataset][metric]["best_score"] = values["best_score"]
                        best_params[algorithm][dataset][metric]["time"] = values["time"]
                        best_params[algorithm][dataset][metric]["best_params"] = values["best_params"]
                        best_params[algorithm][dataset][metric]["optimization_method"] = optimization_method
    # Save the best_params to a JSON file
    output_file = os.path.join('results', 'best_params_algorithm_by_metric.json')
    with open(output_file, 'w') as outfile:
        json.dump(best_params, outfile, indent=4)

    return best_params


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
    best_params = get_best_params()

    # Define storage for metrics and configuration details
    results_summary = {}

    # Extract 'cdrec' configurations
    configs = best_params.get("cdrec", {})

    # Iterate through algorithms and datasets
    for dataset, metrics in configs.items():
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


def cdrec_optimization_results(input_folder: str, results_path: str, metric: str = "rmse_mae") -> dict:
    """
    Run imputation using the best parameters for each optimization method and save the results.

    Parameters
    ----------
    input_folder : str
        Path to the folder containing the parameters resulting from optimization.
    results_path : str
        Path to the folder to save the imputation results.
    metric : str
        Metric used for optimization. Default is "rmse_mae".
    """
    # Define storage for metrics and configuration details
    results_summary = {}

    # Iterate through each file matching the pattern in the input_folder
    for file_path in glob.glob(os.path.join(input_folder, "optimization_results_cdrec_*" + metric + ".json")):
        # Extracting optimization method from the file name
        optimization_method = util.extract_file_info(file_path)

        # Load the optimization parameters from the file
        with open(file_path, 'r') as file:
            optimization_params = json.load(file)

        # Iterate through algorithms and datasets
        for dataset in DATASETS:
            # Get paths for the dataset using the helper function
            raw_file_path, obf_file_path = get_dataset_paths(dataset)

            # Load matrices for the dataset
            ground_truth_matrix = utils.load_and_trim_matrix(raw_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obf_file_path)

            # Run the imputation (using the loaded parameters from the file)
            start_time = time.time()
            imputed_matrix = Wrapper.algo_collection.native_cdrec_param(
                __py_matrix=obfuscated_matrix,
                __py_rank=optimization_params[dataset]["best_params"]["rank"],
                __py_eps=optimization_params[dataset]["best_params"]["eps"],
                __py_iters=optimization_params[dataset]["best_params"]["iters"]
            )
            end_time = time.time()

            corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

            # Check if the optimization method is already in the results_summary.
            if optimization_method not in results_summary:
                results_summary[optimization_method] = {}

            # Store results
            results_summary[optimization_method][dataset] = {
                "algorithm": "cdrec",
                "metric_used_for_optimization": metric,
                "optimization_method": optimization_method,
                "best_params": {
                    "rank": optimization_params[dataset]["best_params"]["rank"],
                    "eps": optimization_params[dataset]["best_params"]["eps"],
                    "iters": optimization_params[dataset]["best_params"]["iters"]
                },
                "rmse": rmse,
                "mae": mae,
                "mi": mi,
                "corr": corr,
                "time_taken": end_time - start_time
            }
            print(results_summary[optimization_method][dataset])

            # Save the imputed matrix to a separate file
            np.save(os.path.join(results_path, f"cdrec_{dataset}_{optimization_method}_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'cdrec_optimization_results_summary.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def get_best_params() -> dict:
    """
    Load the best_params from the saved JSON file.

    Parameters
    ----------
    None

    Returns
    -------
    dict
        A dictionary containing the best_params for each algorithm and dataset.
    """
    # Load best_params from the saved JSON file
    with open(os.path.join('results', 'best_params_algorithm_by_metric.json')) as infile:
        best_params = json.load(infile)
    return best_params


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

        rank = algorithm_parameters.DEFAULT_PARAMS["cdrec"][0]
        eps = algorithm_parameters.DEFAULT_PARAMS["cdrec"][1]
        iters = algorithm_parameters.DEFAULT_PARAMS["cdrec"][2]

        # Run the imputation (using CDRec as an example)
        start_time = time.time()
        imputed_matrix = Wrapper.algo_collection.native_cdrec_param(
            __py_matrix=obfuscated_matrix,
            __py_rank=rank,
            __py_eps=eps,
            __py_iters=iters
        )
        end_time = time.time()

        corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

        # Store results
        results_summary[dataset] = {
            "algorithm": "cdrec",
            "metric_used_for_optimization": "N/A",
            "optimization_method": "N/A",
            "best_params": {
                "rank": rank,
                "eps": eps,
                "iters": iters
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


def iim_optimal_results(results_path: str) -> dict:
    """
    Run imputation using the optimal parameters and save the results.

    Parameters
    ----------
    results_path : str
        Path to the folder containing the saved 'best_params_output.json'.

    Returns
    -------
    dict
        A dictionary containing the results summary for each dataset and algorithm.

    """
    best_params = get_best_params()

    # Define storage for metrics and configuration details
    results_summary = {}

    # Extract 'iim' configurations
    configs = best_params.get("iim", {})

    # Iterate through datasets
    for dataset, metrics in configs.items():
        for metric_name, config in metrics.items():
            # Get paths for the dataset using the helper function
            raw_file_path, obf_file_path = get_dataset_paths(dataset)

            # Load matrices for the dataset
            ground_truth_matrix = utils.load_and_trim_matrix(raw_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obf_file_path)
            obfuscated_matrix_copy = np.copy(obfuscated_matrix)

            # Extract the best parameters
            learning_neighbours = config["best_params"]["learning_neighbours"]
            alg_code = "iim " + re.sub(r'[\W_]', '', str(learning_neighbours))

            # Run the imputation (using IIM as an example)
            start_time = time.time()
            imputed_matrix = iim_alg.impute_with_algorithm(alg_code, obfuscated_matrix_copy)
            end_time = time.time()

            corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

            # Create a unique key for results_summary combining dataset and metric_name
            key = f"{dataset}_{metric_name}"

            # Store results
            results_summary[key] = {
                "algorithm": "iim",
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
            np.save(os.path.join(results_path, f"iim_{dataset}_{metric_name}_imputed.npy"), imputed_matrix)

    with open(os.path.join(results_path, 'iim_optimized_summary_results.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def iim_optimization_results(input_folder: str, results_path: str, metric: str = "rmse_mae") -> dict:
    """
    Run imputation using the best parameters for each optimization method and save the results.

    Parameters
    ----------
    input_folder : str
        Path to the folder containing the parameters resulting from optimization.
    results_path : str
        Path to the folder to save the imputation results.
    metric : str
        Metric used for optimization. Default is "rmse_mae".
    """
    # Define storage for metrics and configuration details
    results_summary = {}

    # Iterate through each file matching the pattern in the input_folder
    for file_path in glob.glob(os.path.join(input_folder, "optimization_results_iim_*" + metric + ".json")):
        # Extracting optimization method from the file name
        optimization_method = util.extract_file_info(file_path)

        # Load the optimization parameters from the file
        with open(file_path, 'r') as file:
            optimization_params = json.load(file)

        # Iterate through algorithms and datasets
        for dataset in DATASETS:
            # Get paths for the dataset using the helper function
            raw_file_path, obf_file_path = get_dataset_paths(dataset)

            # Load matrices for the dataset
            ground_truth_matrix = utils.load_and_trim_matrix(raw_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obf_file_path)
            obfuscated_matrix_copy = np.copy(obfuscated_matrix)

            # Extract the best parameters
            learning_neighbours = optimization_params[dataset]["best_params"]["learning_neighbours"]
            alg_code = "iim " + re.sub(r'[\W_]', '', str(learning_neighbours))

            # Run the imputation (using IIM as an example)
            start_time = time.time()
            imputed_matrix = iim_alg.impute_with_algorithm(alg_code, obfuscated_matrix_copy)
            end_time = time.time()

            corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

            # Check if the optimization method is already in the results_summary.
            if optimization_method not in results_summary:
                results_summary[optimization_method] = {}

            # Store results
            results_summary[optimization_method][dataset] = {
                "algorithm": "iim",
                "metric_used_for_optimization": metric,
                "optimization_method": optimization_method,
                "best_params": {
                    "learning_neighbours": optimization_params[dataset]["best_params"]["learning_neighbours"]
                },
                "rmse": rmse,
                "mae": mae,
                "mi": mi,
                "corr": corr,
                "time_taken": end_time - start_time
            }
            print(results_summary[optimization_method][dataset])

            # Save the imputed matrix to a separate file
            np.save(os.path.join(results_path, f"iim_{dataset}_{optimization_method}_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'iim_optimization_results_summary.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def iim_default_results(results_path: str) -> dict:
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
        obfuscated_matrix_copy = np.copy(obfuscated_matrix)
        alg_code = "iim " + re.sub(r'[\W_]', '', str(algorithm_parameters.DEFAULT_PARAMS["iim"][0]))

        # Run the imputation (using IIM as an example)
        start_time = time.time()
        imputed_matrix = iim_alg.impute_with_algorithm(alg_code, obfuscated_matrix_copy)
        end_time = time.time()

        corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

        # Store results
        results_summary[dataset] = {
            "algorithm": "iim",
            "metric_used_for_optimization": "N/A",
            "optimization_method": "N/A",
            "best_params": {
                "learning_neighbours": algorithm_parameters.DEFAULT_PARAMS["iim"][0]
            },
            "rmse": rmse,
            "mae": mae,
            "mi": mi,
            "corr": corr,
            "time_taken": end_time - start_time
        }
        print(results_summary[dataset])

        # Save the imputed matrix to a separate file (using numpy as an example)
        np.save(os.path.join(results_path, f"iim_{dataset}_default_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'iim_default_summary_results.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def mrnn_optimal_results(results_path: str) -> dict:
    """
    Run imputation using the optimal parameters and save the results.

    Parameters
    ----------
    results_path : str
        Path to the folder containing the saved 'best_params_output.json'.

    Returns
    -------
    dict
        A dictionary containing the results summary for each dataset and algorithm.

    """
    best_params = get_best_params()

    # Define storage for metrics and configuration details
    results_summary = {}

    # Extract 'mrnn' configurations
    configs = best_params.get("mrnn", {})

    # Iterate through datasets
    for dataset, metrics in configs.items():
        for metric_name, config in metrics.items():
            # Get paths for the dataset using the helper function
            raw_file_path, obf_file_path = get_dataset_paths(dataset)

            # Load matrices for the dataset
            ground_truth_matrix = utils.load_and_trim_matrix(raw_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obf_file_path)
            obfuscated_matrix_copy = np.copy(obfuscated_matrix)

            # Extract the best parameters
            hidden_dim = config["best_params"]["hidden_dim"]
            learning_rate = config["best_params"]["learning_rate"]
            iterations = config["best_params"]["iterations"]
            keep_prob = config["best_params"]["keep_prob"]

            # Run the imputation (using MRNN as an example)
            start_time = time.time()
            imputed_matrix = M_RNN.testerMRNN.mrnn_recov_with_data(obfuscated_matrix_copy,
                                                                   runtime=-1,
                                                                   hidden_dim=hidden_dim,
                                                                   learning_rate=learning_rate,
                                                                   iterations=iterations,
                                                                   keep_prob=keep_prob,
                                                                   )
            end_time = time.time()

            corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

            # Create a unique key for results_summary combining dataset and metric_name
            key = f"{dataset}_{metric_name}"

            # Store results
            results_summary[key] = {
                "algorithm": "mrnn",
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
            np.save(os.path.join(results_path, f"mrnn_{dataset}_{metric_name}_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'mrnn_optimized_summary_results.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def mrnn_default_results(results_path: str) -> dict:
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
        obfuscated_matrix_copy = np.copy(obfuscated_matrix)

        # Extract the best parameters
        hidden_dim = algorithm_parameters.DEFAULT_PARAMS["mrnn"][0]
        learning_rate = algorithm_parameters.DEFAULT_PARAMS["mrnn"][1]
        iterations = algorithm_parameters.DEFAULT_PARAMS["mrnn"][2]
        keep_prob = algorithm_parameters.DEFAULT_PARAMS["mrnn"][3]

        # Run the imputation (using MRNN as an example)
        start_time = time.time()
        imputed_matrix = M_RNN.testerMRNN.mrnn_recov_with_data(obfuscated_matrix_copy,
                                                               runtime=-1,
                                                               hidden_dim=hidden_dim,
                                                               learning_rate=learning_rate,
                                                               iterations=iterations,
                                                               keep_prob=keep_prob,
                                                               )
        end_time = time.time()

        corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

        # Store results
        results_summary[dataset] = {
            "algorithm": "mrnn",
            "metric_used_for_optimization": "N/A",
            "optimization_method": "N/A",
            "best_params": {
                "hidden_dim": hidden_dim,
                "learning_rate": learning_rate,
                "iterations": iterations,
                "keep_prob": keep_prob
            },
            "rmse": rmse,
            "mae": mae,
            "mi": mi,
            "corr": corr,
            "time_taken": end_time - start_time
        }
        print(results_summary[dataset])

        # Save the imputed matrix to a separate file (using numpy as an example)
        np.save(os.path.join(results_path, f"mrnn_{dataset}_default_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'mrnn_default_summary_results.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def mrnn_optimization_results(input_folder: str, results_path: str, metric: str = "rmse_mae") -> dict:
    """
    Run imputation using the best parameters for each optimization method and save the results.

    Parameters
    ----------
    input_folder : str
        Path to the folder containing the parameters resulting from optimization.
    results_path : str
        Path to the folder to save the imputation results.
    metric : str
        Metric used for optimization. Default is "rmse_mae".
    """
    # Define storage for metrics and configuration details
    results_summary = {}

    # Iterate through each file matching the pattern in the input_folder
    for file_path in glob.glob(os.path.join(input_folder, "optimization_results_mrnn_*" + metric + ".json")):
        # Extracting optimization method from the file name
        optimization_method = util.extract_file_info(file_path)

        # Load the optimization parameters from the file
        with open(file_path, 'r') as file:
            optimization_params = json.load(file)

        # Iterate through algorithms and datasets
        for dataset in DATASETS:
            # Get paths for the dataset using the helper function
            raw_file_path, obf_file_path = get_dataset_paths(dataset)

            # Load matrices for the dataset
            ground_truth_matrix = utils.load_and_trim_matrix(raw_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obf_file_path)
            obfuscated_matrix_copy = np.copy(obfuscated_matrix)

            # Extract the best parameters
            hidden_dim = optimization_params[dataset]["best_params"]["hidden_dim"]
            learning_rate = optimization_params[dataset]["best_params"]["learning_rate"]
            iterations = optimization_params[dataset]["best_params"]["iterations"]
            keep_prob = optimization_params[dataset]["best_params"]["keep_prob"]

            # Run the imputation (using MRNN as an example)
            start_time = time.time()
            imputed_matrix = M_RNN.testerMRNN.mrnn_recov_with_data(obfuscated_matrix_copy,
                                                                   runtime=-1,
                                                                   hidden_dim=hidden_dim,
                                                                   learning_rate=learning_rate,
                                                                   iterations=iterations,
                                                                   keep_prob=keep_prob,
                                                                   )
            end_time = time.time()

            corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

            # Check if the optimization method is already in the results_summary.
            if optimization_method not in results_summary:
                results_summary[optimization_method] = {}

            # Store results
            results_summary[optimization_method][dataset] = {
                "algorithm": "mrnn",
                "metric_used_for_optimization": metric,
                "optimization_method": optimization_method,
                "best_params": {
                    "hidden_dim": hidden_dim,
                    "learning_rate": learning_rate,
                    "iterations": iterations,
                    "keep_prob": keep_prob
                },
                "rmse": rmse,
                "mae": mae,
                "mi": mi,
                "corr": corr,
                "time_taken": end_time - start_time
            }
            print(results_summary[optimization_method][dataset])

            # Save the imputed matrix to a separate file
            np.save(os.path.join(results_path, f"mrnn_{dataset}_{optimization_method}_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'mrnn_optimization_results_summary.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def stmvl_optimal_results(results_path: str) -> dict:
    """
    Run imputation using the optimal parameters and save the results.

    Parameters
    ----------
    results_path : str
        Path to the folder containing the saved 'best_params_output.json'.

    Returns
    -------
    dict
        A dictionary containing the results summary for each dataset and algorithm.

    """
    best_params = get_best_params()

    # Define storage for metrics and configuration details
    results_summary = {}

    # Extract 'stmvl' configurations
    configs = best_params.get("stmvl", {})

    # Iterate through datasets
    for dataset, metrics in configs.items():
        for metric_name, config in metrics.items():
            # Get paths for the dataset using the helper function
            raw_file_path, obf_file_path = get_dataset_paths(dataset)

            # Load matrices for the dataset
            ground_truth_matrix = utils.load_and_trim_matrix(raw_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obf_file_path)

            # Extract the best parameters
            window_size = config["best_params"]["window_size"]
            gamma = config["best_params"]["gamma"]
            alpha = config["best_params"]["alpha"]

            # Run the imputation (using CDRec as an example)
            start_time = time.time()
            imputed_matrix = Wrapper.algo_collection.native_stmvl_param(
                __py_matrix=obfuscated_matrix,
                __py_window=int(window_size),
                __py_gamma=float(gamma),
                __py_alpha=int(alpha)
            )
            end_time = time.time()

            corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

            # Create a unique key for results_summary combining dataset and metric_name
            key = f"{dataset}_{metric_name}"

            # Store results
            results_summary[key] = {
                "algorithm": "stmvl",
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
            np.save(os.path.join(results_path, f"stmvl_{dataset}_{metric_name}_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'stmvl_optimized_summary_results.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def stmvl_default_results(results_path: str) -> dict:
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

        window = algorithm_parameters.DEFAULT_PARAMS["stmvl"][0]
        gamma = algorithm_parameters.DEFAULT_PARAMS["stmvl"][1]
        alpha = algorithm_parameters.DEFAULT_PARAMS["stmvl"][2]

        # Run the imputation (using CDRec as an example)
        start_time = time.time()
        imputed_matrix = Wrapper.algo_collection.native_stmvl_param(
            __py_matrix=obfuscated_matrix,
            __py_window=window,
            __py_gamma=gamma,
            __py_alpha=alpha
        )
        end_time = time.time()

        corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

        # Store results
        results_summary[dataset] = {
            "algorithm": "stmvl",
            "metric_used_for_optimization": "N/A",
            "optimization_method": "N/A",
            "best_params": {
                "window_size": window,
                "gamma": gamma,
                "alpha": alpha
            },
            "rmse": rmse,
            "mae": mae,
            "mi": mi,
            "corr": corr,
            "time_taken": end_time - start_time
        }
        print(results_summary[dataset])

        # Save the imputed matrix to a separate file (using numpy as an example)
        np.save(os.path.join(results_path, f"stmvl_{dataset}_default_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'stmvl_default_summary_results.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def stmvl_optimization_results(input_folder: str, results_path: str, metric: str = "rmse_mae") -> dict:
    """
    Run imputation using the best parameters for each optimization method and save the results.

    Parameters
    ----------
    input_folder : str
        Path to the folder containing the parameters resulting from optimization.
    results_path : str
        Path to the folder to save the imputation results.
    metric : str
        Metric used for optimization. Default is "rmse_mae".
    """
    # Define storage for metrics and configuration details
    results_summary = {}

    # Iterate through each file matching the pattern in the input_folder
    for file_path in glob.glob(os.path.join(input_folder, "optimization_results_stmvl_*" + metric + ".json")):
        # Extracting optimization method from the file name
        optimization_method = util.extract_file_info(file_path)

        # Load the optimization parameters from the file
        with open(file_path, 'r') as file:
            optimization_params = json.load(file)

        # Iterate through algorithms and datasets
        for dataset in DATASETS:
            # Get paths for the dataset using the helper function
            raw_file_path, obf_file_path = get_dataset_paths(dataset)

            # Load matrices for the dataset
            ground_truth_matrix = utils.load_and_trim_matrix(raw_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obf_file_path)

            # Extract the best parameters
            window = optimization_params[dataset]["best_params"]["window_size"]
            gamma = optimization_params[dataset]["best_params"]["gamma"]
            alpha = optimization_params[dataset]["best_params"]["alpha"]

            # Run the imputation (using CDRec as an example)
            start_time = time.time()
            imputed_matrix = Wrapper.algo_collection.native_stmvl_param(
                __py_matrix=obfuscated_matrix,
                __py_window=int(window),
                __py_gamma=float(gamma),
                __py_alpha=int(alpha)
            )
            end_time = time.time()

            corr, mae, mi, rmse = determine_metrics(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

            # Check if the optimization method is already in the results_summary.
            if optimization_method not in results_summary:
                results_summary[optimization_method] = {}

            # Store results
            results_summary[optimization_method][dataset] = {
                "algorithm": "stmvl",
                "metric_used_for_optimization": metric,
                "optimization_method": optimization_method,
                "best_params": {
                    "window_size": window,
                    "gamma": gamma,
                    "alpha": alpha
                },
                "rmse": rmse,
                "mae": mae,
                "mi": mi,
                "corr": corr,
                "time_taken": end_time - start_time
            }
            print(results_summary[optimization_method][dataset])

            # Save the imputed matrix to a separate file
            np.save(os.path.join(results_path, f"stmvl_{dataset}_{optimization_method}_imputed.npy"), imputed_matrix)

    # Save the summary results to a separate JSON file
    with open(os.path.join(results_path, 'stmvl_optimization_results_summary.json'), 'w') as outfile:
        json.dump(results_summary, outfile, indent=4)

    return results_summary


def determine_metrics(ground_truth_matrix: np.array, imputed_matrix: np.array, obfuscated_matrix: np.array) -> Tuple[
    float, float, float, float]:
    """
    Given the ground truth, imputed and obfuscated matrices, compute the metrics.

    Parameters
    ----------
    ground_truth_matrix : np.array
        Ground truth matrix.
    imputed_matrix : np.array
        Imputed matrix.
    obfuscated_matrix : np.array
        Obfuscated matrix.

    Returns
    -------
    tuple
        Tuple containing the correlation, MAE, MI and RMSE.

    Notes
    -----
    The imputed matrix is converted to a numpy array to ensure compatibility with the metrics functions.
    """
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
    # get_best_params_by_dataset()
    # Get the best params by algorithm
    # get_best_params_by_algorithm()

    # Print the best_params
    # print(json.dumps(best_params, indent=4))
    ####

    ##### Step 2: Run imputation using the best params
    # cdrec_optimal_results(results_path="results/cdrec")
    # iim_optimal_results(results_path="results/iim")
    # mrnn_optimal_results(results_path="results/mrnn")
    # stmvl_optimal_results(results_path="results/stmvl")

    #### Step 2.1: Run imputation for each optimization method's best result
    #cdrec_optimization_results(input_folder="metric_specific", results_path="results/cdrec/optimization")
    # TODO Completely test IIM, M-RNN, ST-MVL
    #iim_optimization_results(input_folder="metric_specific", results_path="results/iim/optimization")
    mrnn_optimization_results(input_folder="metric_specific", results_path="results/mrnn/optimization")
    #stmvl_optimization_results(input_folder="metric_specific", results_path="results/stmvl/optimization")

    ##### Step 3: Run imputation using the default params
    # cdrec_default_results(results_path="results/cdrec")
    # iim_default_results(results_path="results/iim")
    # mrnn_default_results(results_path="results/mrnn")
    # stmvl_default_results(results_path="results/stmvl")

    ##### Step 4: Save and plot the results for each optimization method

# Load the best_params from the saved JSON file
# with open(output_file, 'r') as infile:
#     loaded_best_params = json.load(infile)

# Use the loaded_best_params as needed. For instance:
# some_function(loaded_best_params["bafu"]["cdrec"]["best_params"])
