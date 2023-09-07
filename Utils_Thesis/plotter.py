import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta


def plot_time_series(time_series: np.ndarray,
                     name: str,
                     title: str,
                     granularity: str = "daily",
                     year: int = 1975,
                     dpi: int = 400,
                     save: bool = True,
                     rate: int = 0) -> None:
    """
    Plot a time series.

    Parameters
    ----------
    time_series : np.ndarray
        The data of the series.
    name : str
        Name of the series (label for y-axis).
    title : str
        Title of the data set.
    granularity : str, optional
        Granularity of the time series. Could be 'daily', 'hourly', '6-hourly', '30-minutes', '10-minutes', 'monthly',
        'yearly'. Defaults to 'daily'.
    dpi : int, optional
        Dots Per Inch for the plot. Defaults to 400.
    save : bool, optional
        Whether to save the plot to the "Results" directory. Defaults to True.
    rate : int, optional
        The rate of missing values in the time series. Defaults to 0.

    Returns
    -------
    None
        Displays and optionally saves the plotted time series.
    """

    # Arbitrary starting point: start of the current year
    start_date = datetime(year, 1, 1)
    if title == "Bafu":
        start_date = datetime(year, 12, 12)

    # Generate time labels based on granularity
    if granularity == "daily":
        delta = timedelta(days=1)
    elif granularity == "hourly":
        delta = timedelta(hours=1)
    elif granularity == "6-hourly":
        delta = timedelta(hours=6)
    elif granularity == "30-minutes":
        delta = timedelta(minutes=30)
    elif granularity == "10-minutes":
        delta = timedelta(minutes=10)
    elif granularity == "5-minutes":
        delta = timedelta(minutes=5)
    elif granularity == "monthly":
        delta = timedelta(days=30)  # assuming 30 days in a month for simplicity
    elif granularity == "yearly":
        delta = timedelta(days=365)  # assuming 365 days in a year for simplicity
    else:
        raise ValueError(f"Unsupported granularity: {granularity}")

    time_labels = [start_date + i * delta for i in range(len(time_series))]

    plt.figure(dpi=dpi, figsize=(6.4, 4))
    plt.plot(time_labels, time_series, label=name)
    plt.xlabel("Time")
    plt.ylabel(name + " " + "Value")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Handle the x-axis ticks to ensure readability
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=6))  # Adjust as needed
    plt.gcf().autofmt_xdate()  # Beautify the x-labels

    if save:
        # Save the figure in the Results folder
        # filename = os.path.join("Results", f"{title}.png")
        filename = os.path.join("Results", f"{title}_{rate}.png")
        plt.savefig(filename, dpi=dpi)

    # plt.show()
    plt.close()


if __name__ == "__main__":
    datasets = [
        'bafu', 'chlorine', 'climate',
        'drift',
        'meteo'
    ]

    dataset_files = [
        'BAFU', 'cl2fullLarge', 'climate',
        'batch10',
        'meteo_total'
    ]

    granularities = [
        '30-minutes', 'hourly', 'daily',
        '6-hourly',
        '10-minutes'
    ]

    series_names = [
        'Thur-Andelfingen', 'Series 1', 'CLD',
        'DR_1',
        'tde000s0'
    ]

    starting_years = [
        1974, 2000, 1990,
        2007,
        1980
    ]

    for dataset, data_file, granularity, series_name, start_year in zip(datasets, dataset_files, granularities,
                                                                        series_names, starting_years):
        raw_file_path = f"../Datasets/{dataset}/raw_matrices/{data_file}_eighth.txt"

        if dataset == 'drift':
            raw_file_path = f"../Datasets/{dataset}/drift10/raw_matrices/{data_file}_eighth.txt"

        raw_matrix = np.loadtxt(raw_file_path, delimiter=" ")
        plot_time_series(raw_matrix[:, 0], series_name, dataset.title(), granularity=granularity, year=start_year,
                         dpi=400, save=True)

    for dataset, data_file, granularity, series_name, start_year in zip(datasets, dataset_files, granularities,
                                                                        series_names, starting_years):
        for mcar in ["1", "5", "10", "20", "40","80"]:
            obfuscated_file_path = f"../Datasets/{dataset}/obfuscated/{data_file}_eighth_obfuscated_{mcar}.txt"

            raw_matrix = np.loadtxt(obfuscated_file_path, delimiter=" ")
            plot_time_series(raw_matrix[:, 0], series_name, dataset.title(), granularity=granularity, year=start_year,
                             dpi=400, save=True, rate=mcar)

    # Test the plot_time_series function
    # Generate a random time series
    # time_series = np.random.rand(100)
    # plot_time_series(time_series, "Random", "Random time series", granularity="daily", dpi=400, save=True)
