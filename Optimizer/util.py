import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple, Union, Any
from collections import defaultdict
import json
from typing import Dict, Any, List
import os


def load_json_files(file_names: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Load multiple JSON files into a dictionary.

    Parameters
    ----------
    file_names : List[str]
        List of file names to be loaded.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        Dictionary where keys are algorithm names and values are data from JSON.
    """
    data = {}
    for file_name in file_names:
        load_json_file(data, file_name)
    return data


def load_json_file(data, file_name):
    with open(file_name, 'r') as f:
        algorithm_name = file_name.split("_")[0]
        data[algorithm_name] = json.load(f)
        return data


def extract_table_data(data: Dict[str, Dict[str, Any]], datasets: List[str], metrics: List[str]) -> Dict[
    str, Dict[str, Dict[str, Any]]]:
    """
    Extract table data from the JSON data.

    Parameters
    ----------
    data : Dict[str, Dict[str, Any]]
        Dictionary containing loaded JSON data.
    datasets : List[str]
        List of dataset names.
    metrics : List[str]
        List of metric names.

    Returns
    -------
    Dict[str, Dict[str, Dict[str, Any]]]
        Nested dictionary containing table data.
    """
    table_data = {}
    for dataset in datasets:
        for metric in metrics:
            key = f"{dataset}_{metric}"
            for algorithm, algorithm_data in data.items():
                if key in algorithm_data:
                    params = algorithm_data[key]["best_params"]
                    optimization_method = algorithm_data[key]["optimization_method"]
                    if key not in table_data:
                        table_data[key] = {}
                    table_data[key][algorithm] = {"params": params, "optimization_method": optimization_method}
    return table_data


def mapper(input_string: str):
    input_string = input_string.lower()
    if input_string == "cdrec":
        return "CDRec"
    elif input_string == "iim":
        return "IIM"
    elif input_string == "mrnn":
        return "M-RNN"
    elif input_string == "stmvl":
        return "ST-MVL"
    elif input_string == "bayesian optimization" or input_string == "bayesian_optimization":
        return "BO"
    elif input_string == "pso":
        return "PSO"
    elif input_string == "succesive halving" or input_string == "succesive_halving":
        return "SH"
    elif input_string == "eps":
        return "Epsilon"
    elif input_string == "iters":
        return "Iterations"
    elif input_string == "mi_corr":
        return "NMI_CORR"
    else:
        return input_string.capitalize()


def extract_table_data_single(json_data: Dict[str, Any], datasets: List[str], metrics: List[str]) -> Dict[
    str, Dict[str, Dict[str, Any]]]:
    """
    Extract the required table data from the provided JSON data for a single algorithm.

    Parameters
    ----------
    json_data : Dict[str, Any]
        JSON data containing results.
    datasets : List[str]
        List of datasets to consider.
    metrics : List[str]
        List of metrics to consider.

    Returns
    -------
    Dict[str, Dict[str, Dict[str, Any]]]
        Nested dictionary containing extracted table data.
    """
    table_data = {}

    # Get the first key (it should represent the algorithm path like 'results/cdrec/cdrec')
    algorithm_key = list(json_data.keys())[0]
    algorithm_data = json_data[algorithm_key]

    for dataset in datasets:
        for metric in metrics:
            key = f"{dataset}_{metric}"
            if key in algorithm_data:
                entry = algorithm_data[key]
                algorithm = entry["algorithm"].split('/')[-1].upper()  # Get the last part after the '/'
                params = entry["best_params"]
                optimization_method = entry["optimization_method"]
                metric_used_for_optimization = entry["metric_used_for_optimization"]
                rmse = entry["rmse"]
                mae = entry["mae"]
                mi = entry["mi"]
                corr = entry["corr"]

                if key not in table_data:
                    table_data[key] = {}

                table_data[key][algorithm] = {
                    "params": params,
                    "optimization_method": optimization_method,
                    "metric_used_for_optimization": metric_used_for_optimization,
                    "rmse": rmse,
                    "mae": mae,
                    "mi": mi,
                    "corr": corr
                }

    return table_data


def process_for_algorithm(file_name: str, algorithm_name: str, datasets: List[str], metrics: List[str]) -> str:
    """
    Process the provided file for a specific algorithm and generate the LaTeX table.

    Parameters
    ----------
    file_name : str
        Path to the JSON file containing the results.
    algorithm_name : str
        Algorithm name to be used in the LaTeX table caption.
    datasets : List[str]
        List of datasets to consider.
    metrics : List[str]
        List of metrics to consider.

    Returns
    -------
    str
        LaTeX formatted table as a string for the specific algorithm.
    """
    data = {}
    data = load_json_file(data, file_name)
    table_data = extract_table_data_single(data, datasets, metrics)
    if metrics == ["rmse_mae", "mi_corr"]:
        return create_latex_table_per_algorithm_extended(table_data, algorithm_name)
    else:
        create_plots_per_algorithm(table_data, algorithm_name)
        return create_latex_table_per_algorithm(table_data, algorithm_name)


def create_latex_table_per_algorithm(table_data: Dict[str, Dict[str, Dict[str, Any]]], algorithm: str) -> str:
    """
    Create a LaTeX table for a specific algorithm from the extracted data.

    Parameters
    ----------
    table_data : Dict[str, Dict[str, Dict[str, Any]]]
        Nested dictionary containing table data.
    algorithm : str
        Algorithm name to filter the data.

    Returns
    -------
    str
        LaTeX formatted table as a string for the specific algorithm.
    """

    # 1. Identify unique parameters
    unique_params = set()
    for _, algorithm_data in table_data.items():
        algorithm_upper = algorithm.upper().replace("-", "")  # Caps case and remove hyphens
        if algorithm_upper in algorithm_data:
            params = algorithm_data[algorithm_upper]["params"]
            for param in params:
                unique_params.add(param)
    unique_params = sorted(list(unique_params))

    # 2. Modify table header
    table_columns = "|c|c|c|" + "|c|" * len(
        unique_params)  # columns for Dataset, Metric, Optimization method, and each unique parameter
    header = "Data Set & Optimized On & Method & " + " & ".join(
        [replace_underscores(p).title() for p in unique_params]) + " \\\\ \\hline\n"

    latex_table = "\\begin{table}\n\\centering\n"
    latex_table += "\\begin{tabular}{" + table_columns + "}\n\\hline\n"
    latex_table += header

    # 3. Populate table rows
    for key, algorithm_data in table_data.items():
        dataset, optimized_on_metric = key.split("_", 1)
        dataset = replace_underscores(dataset)
        optimized_on_metric = replace_underscores(optimized_on_metric)

        algorithm_upper = algorithm.upper().replace("-", "")  # Caps case and remove hyphens
        if algorithm_upper in algorithm_data:
            details = algorithm_data[algorithm_upper]
            optimization_method = replace_underscores(details["optimization_method"])
            param_values = [
                f"{round(details['params'].get(param, 0), 5)}" if isinstance(details['params'].get(param), (int, float))
                else details['params'].get(param, '-')
                for param in unique_params
            ]

            latex_table += f"{dataset.title()} & {optimized_on_metric.upper()} & {mapper(optimization_method)} & " + " & ".join(
                param_values) + " \\\\ \\hline\n"

    latex_table += "\\end{tabular}\n\\caption{" + f"Results for {algorithm}" + "}\n\\end{table}"
    return latex_table


def create_latex_table_per_algorithm_extended(table_data: Dict[str, Dict[str, Dict[str, Any]]], algorithm: str) -> str:
    """
    Create a LaTeX table for a specific algorithm from the extracted data.

    Parameters
    ----------
    table_data : Dict[str, Dict[str, Dict[str, Any]]]
        Nested dictionary containing table data.
    algorithm : str
        Algorithm name to filter the data.

    Returns
    -------
    str
        LaTeX formatted table as a string for the specific algorithm.
    """

    # 1. Identify unique parameters
    unique_params = set()
    for _, algorithm_data in table_data.items():
        algorithm_upper = algorithm.upper().replace("-", "")  # Caps case and remove hyphens
        if algorithm_upper in algorithm_data:
            params = algorithm_data[algorithm_upper]["params"]
            for param in params:
                unique_params.add(param)
    unique_params = sorted(list(unique_params))

    # 2. Modify table header
    table_columns = "|c|c|c|c|c|c|" + "|c|" * len(unique_params)  # columns for metrics + unique parameters
    header = ("Data Set & Configuration & RMSE & MAE & MI & CORR & " +
              " & ".join([replace_underscores(p).title() for p in unique_params]) + " \\\\ \\hline\n")

    latex_table = "\\begin{table}\n\\centering\n"
    latex_table += "\\begin{tabular}{" + table_columns + "}\n\\hline\n"
    latex_table += header

    # 3. Populate table rows
    for key, algorithm_data in table_data.items():
        dataset, optimized_on_metric = key.split("_", 1)
        dataset = replace_underscores(dataset)
        optimized_on_metric = replace_underscores(optimized_on_metric)

        algorithm_upper = algorithm.upper().replace("-", "")  # Caps case and remove hyphens
        if algorithm_upper in algorithm_data:
            details = algorithm_data[algorithm_upper]
            optimization_method = replace_underscores(details["optimization_method"])

            # Parameters
            param_values = [
                f"{round(details['params'].get(param, 0), 5)}" if isinstance(details['params'].get(param), (int, float))
                else details['params'].get(param, '-')
                for param in unique_params
            ]

            # Metrics
            rmse = round(details.get('rmse', 0), 3)
            mae = round(details.get('mae', 0), 3)
            mi = round(details.get('mi', 0), 3)
            corr = round(details.get('corr', 0), 3)

            latex_table += (f"{dataset.title()} & {optimized_on_metric.upper()} & "
                            f"{rmse} & {mae} & {mi} & {corr} & " + " & ".join(param_values) + " \\\\ \\hline\n")

    latex_table += "\\end{tabular}\n\\caption{" + f"Results for {algorithm}" + "}\n\\end{table}"
    return latex_table


def create_plots_per_algorithm(table_data: Dict[str, Dict[str, Dict[str, Any]]], algorithm: str):
    """
    Create a plot for a specific algorithm from the extracted data.

    Parameters
    ----------
    table_data : Dict[str, Dict[str, Dict[str, Any]]]
        Nested dictionary containing table data.
    algorithm : str
        Algorithm name to filter the data.
    """
    # Assuming bar_width is the width of each bar
    spacing_between_datasets = 0.15
    # Width of the bars
    bar_width = 0.95

    # 1. Identify unique parameters
    unique_params = set()
    for _, algorithm_data in table_data.items():
        algorithm_upper = algorithm.upper().replace("-", "")
        if algorithm_upper in algorithm_data:
            params = algorithm_data[algorithm_upper]["params"]
            for param in params:
                unique_params.add(param)
    unique_params = sorted(list(unique_params))

    # 2. For each parameter, plot its values and annotate them
    for param in unique_params:

        # Data for plotting
        datasets = []
        values = []
        optimization_methods = []

        for key, algorithm_data in table_data.items():
            dataset, _ = key.split("_", 1)

            algorithm_upper = algorithm.upper().replace("-", "")
            if algorithm_upper in algorithm_data:
                details = algorithm_data[algorithm_upper]

                # Extract optimization methods and their values
                for optimization_method in [details["metric_used_for_optimization"]]:
                    datasets.append(mapper(dataset))
                    values.append(details['params'].get(param, 0))
                    optimization_methods.append(optimization_method)

        # Determine number of optimization methods for bar positions
        num_methods = len(set(optimization_methods))
        num_datasets = len(datasets) // num_methods
        positions = list(range(num_datasets))
        # Adjusted width based on the number of optimization methods
        adjusted_bar_width = bar_width / num_methods

        # Create plot
        fig, ax = plt.subplots()

        unique_optimization_methods = []
        for opt_method in optimization_methods:
            if opt_method not in unique_optimization_methods:
                unique_optimization_methods.append(opt_method)

        print("Datasets:", datasets)
        print("Opt Methods:", optimization_methods)
        print("Values:", values)
        # Plot bars for each optimization method
        for i, method in enumerate(unique_optimization_methods):
            bars = ax.bar(
                [p + i * adjusted_bar_width + p * spacing_between_datasets for p in positions[:num_datasets]],
                values[i * num_datasets:(i + 1) * num_datasets],
                adjusted_bar_width,
                label=method.upper(),
            )

            # Annotate bars with rounded values and optimization methods
            for j, bar in enumerate(bars):
                height = bar.get_height()
                annotation_text = str(round(height, 3)).rstrip('0').rstrip('.') if isinstance(height, float) else str(
                    height)
                ax.annotate(annotation_text,
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 0.5),  # vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', rotation=45)

        plt.xlabel('Dataset')
        plt.ylabel('Value')
        plt.title(f'{mapper(param)} values for {algorithm}')

        tick_positions = [p + bar_width * (num_methods / 2) for p in range(num_datasets)]
        tick_positions = [p + adjusted_bar_width * (num_methods / 2) + p * spacing_between_datasets for p in
                          range(num_datasets)]

        tick_labels = [datasets[i * num_methods] for i in range(num_datasets)]

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')

        plt.legend(loc='best', fontsize='x-small')
        plt.tight_layout()

        # Save to /figures/
        plt.savefig(f'figures/{algorithm}_{param}.png', dpi=400)
        plt.close()

    print(f"Plots for {algorithm} saved under /figures/.")


def round_params_values(params: dict) -> dict:
    """
    Recursively round float values in the dictionary to 5 decimal points.

    Parameters:
    - params (dict): A dictionary containing parameters.

    Returns:
    - dict: The modified dictionary with rounded float values.
    """
    for key, value in params.items():
        if isinstance(value, float):
            params[key] = round(value, 5)
        elif isinstance(value, dict):
            params[key] = round_params_values(value)
    return params


def json_serializable(item: Any) -> Union[int, float, list, dict, tuple, str]:
    """
    Convert objects, especially numpy objects, to native Python objects for JSON serialization.

    Parameters
    ----------
    item : Any
        The item or object to be converted to a JSON serializable format.

    Returns
    -------
    Union[int, float, list, dict, tuple, str]
        The item converted to a Python native format suitable for JSON serialization.

    Raises
    ------
    TypeError
        If the item is of a type that is not serializable.
    """

    if isinstance(item, (np.integer, np.int64)):  # Added np.int64 for clarity
        return int(item)
    elif isinstance(item, (np.floating, float)):
        return float(item)
    elif isinstance(item, np.ndarray):
        return item.tolist()
    elif isinstance(item, tuple):
        return tuple(json_serializable(i) for i in item)
    elif isinstance(item, list):
        return [json_serializable(i) for i in item]
    elif isinstance(item, dict):
        return {k: json_serializable(v) for k, v in item.items()}
    elif isinstance(item, (str, int)):  # Allow native Python str and int types
        return item
    else:
        raise TypeError(f"Type {type(item)} not serializable")


def replace_underscores(text: str) -> str:
    """
    Replace underscores in a given string with spaces.

    Parameters
    ----------
    text : str
        The input text that needs its underscores replaced.

    Returns
    -------
    str
        The text with underscores replaced by spaces.
    """
    return text.replace("_", " ")


def escape_underscores(text: str) -> str:
    """
    Escape underscores in a given string to make it LaTeX-compatible.

    Parameters
    ----------
    text : str
        The input text that needs to be escaped.

    Returns
    -------
    str
        The text with underscores escaped for LaTeX.
    """
    return text.replace("_", "\\_")


def extract_file_info(file_path: str) -> str:
    """
    Extract optimization method from the file name.

    Parameters
    ----------
    file_path : str
        Path to the file.

    Returns
    -------
    str
        The optimization method used for the file.
    """
    file_name = os.path.basename(file_path)
    optimizations = ["bayesian_optimization", "pso", "succesive_halving"]

    for opt in optimizations:
        if opt in file_name:
            return opt

    raise ValueError(f"Unexpected file name format: {file_name}")


if __name__ == "__main__":
    # file_names = ["results/iim/iim_optimized_summary_results.json",
    #               "results/cdrec/cdrec_optimized_summary_results.json",
    #               "results/stmvl/stmvl_optimized_summary_results.json"]
    datasets = ["bafu", "chlorine", "climate", "drift", "meteo"]
    metrics = ["rmse_mae", "mi_corr", "rmse", "mae", "mi", "corr"]
    metrics_for_table = ["rmse_mae", "mi_corr"]

    file_name_cdrec = "results/cdrec/cdrec_optimized_summary_results.json"
    latex_cdrec = process_for_algorithm(file_name_cdrec, "CDRec", datasets, metrics)
    with open("latex_table_cdrec.txt", 'w') as f:
        f.write(latex_cdrec)
    # latex_cdrec_extended = process_for_algorithm(file_name_cdrec, "CDRec", datasets, metrics_for_table)
    # with open("latex_table_cdrec_extended.txt", 'w') as f:
    #     f.write(latex_cdrec_extended)

    file_name_iim = "results/iim/iim_optimized_summary_results.json"
    latex_iim = process_for_algorithm(file_name_iim, "IIM", datasets, metrics)
    # with open("latex_table_iim.txt", 'w') as f:
    #     f.write(latex_iim)
    # latex_iim_extended = process_for_algorithm(file_name_iim, "IIM", datasets, metrics_for_table)
    # with open("latex_table_iim_extended.txt", 'w') as f:
    #     f.write(latex_iim_extended)
    file_name_mrnn = "results/mrnn/mrnn_optimized_summary_results.json"
    latex_mrnn = process_for_algorithm(file_name_mrnn, "M-RNN", datasets, metrics)
    # with open("latex_table_mrnn.txt", 'w') as f:
    #     f.write(latex_mrnn)
    # latex_mrnn_extended = process_for_algorithm(file_name_mrnn, "M-RNN", datasets, metrics_for_table)
    # with open("latex_table_mrnn_extended.txt", 'w') as f:
    #     f.write(latex_mrnn_extended)
    file_name_stmvl = "results/stmvl/stmvl_optimized_summary_results.json"
    latex_stmvl = process_for_algorithm(file_name_stmvl, "ST-MVL", datasets, metrics)
    # with open("latex_table_stmvl.txt", 'w') as f:
    #     f.write(latex_stmvl)
    # latex_stmvl_extended = process_for_algorithm(file_name_stmvl, "ST-MVL", datasets, metrics_for_table)
    # with open("latex_table_stmvl_extended.txt", 'w') as f:
    #     f.write(latex_stmvl_extended)
