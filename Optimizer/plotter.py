import json
import matplotlib.pyplot as plt


def compare_results(default_file_path: str, optimized_file_path: str, algorithm: str):
    """
    Compare the metrics and time taken for the 'cdrec' algorithm in the default settings
    versus the optimized settings and plot the results.

    Parameters
    ----------
    default_file_path : str
        Path to the JSON file containing the default settings results.
    optimized_file_path : str
        Path to the JSON file containing the optimized settings results.
    algorithm : str
        The used algorithm. This is used to name the output files.

    Returns
    -------
    None
        The function will plot the results, save them as PNG in the "figures" directory,
        and does not return any value.
    """

    # Load the JSON files
    with open(default_file_path, "r") as file:
        default_results = json.load(file)

    with open(optimized_file_path, "r") as file:
        optimized_results = json.load(file)

    # Prepare data for plotting
    metrics = ['rmse', 'mae', 'mi', 'corr', 'time_taken']
    default_values = {}
    optimized_values = {}

    for key, value in default_results.items():
        if key not in default_values:
            default_values[key] = {}
        for metric in metrics:
            default_values[key][metric] = value[metric]

    for key, value in optimized_results.items():
        prefix = key.rsplit('_', 1)[0]  # extract the prefix e.g. 'bafu' from 'bafu_corr'
        if prefix not in optimized_values:
            optimized_values[prefix] = {}
        for metric in metrics:
            # Take the mean of the metrics for different optimization settings
            if metric not in optimized_values[prefix]:
                optimized_values[prefix][metric] = []
            optimized_values[prefix][metric].append(value[metric])

    # Plot the results
    for metric in metrics:
        plt.figure(figsize=(10, 5))
        labels = list(default_values.keys())
        default_metric_values = [default_values[label][metric] for label in labels]
        optimized_metric_values = [sum(optimized_values[label][metric]) / len(optimized_values[label][metric]) for label
                                   in labels]
        # Check if it's time_taken and adjust label and units accordingly
        if metric == "time_taken":
            metric_display = "Time"
            ylabel = "Time [s]"
        else:
            metric_display = metric.upper()
            ylabel = metric_display

        width = 0.35

        fig, ax = plt.subplots()
        rects1 = ax.bar(labels, default_metric_values, width, label='Default')
        rects2 = ax.bar([label for label in labels], optimized_metric_values, width, bottom=default_metric_values,
                        label='Optimized')

        ax.set_ylabel(ylabel)
        ax.set_title(f'{algorithm}: Comparison of {metric_display} between Default and Optimized Settings')
        ax.legend()
        plt.tight_layout()

        # Save the figure to the 'figures' folder with a descriptive name
        file_name = f"figures/{algorithm}_comparison_of_{metric}_default_vs_optimized.png"
        plt.savefig(file_name)
        plt.show()


if __name__ == '__main__':
    # compare_results("./results/cdrec/cdrec_default_summary_results.json",
    #                 "./results/cdrec/cdrec_optimized_summary_results.json",
    #                 "CDRec")
    # compare_results("./results/stmvl/stmvl_default_summary_results.json",
    #                 "./results/stmvl/stmvl_optimized_summary_results.json",
    #                 "ST-MVL")
    algorithm_names = ["CDRec",
                       # "M-RNN",
                       # "IIM",
                       "ST-MVL"]
    filename_patterns = ["cdrec",
                         # "mrnn",
                         # "iim",
                         "stmvl"]

    for algo, pattern in zip(algorithm_names, filename_patterns):
        default_path = f"./results/{pattern}/{pattern}_default_summary_results.json"
        optimized_path = f"./results/{pattern}/{pattern}_optimized_summary_results.json"

        compare_results(default_path, optimized_path, algo)

