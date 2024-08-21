import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

from matplotlib import MatplotlibDeprecationWarning

warnings.filterwarnings("ignore", category=MatplotlibDeprecationWarning)

FACTOR_S = 0.1
SEED = 42
BLOCK_SIZE = 10

def load_timeseries (filename) :
    print("\t\t >> LOAD SERIES " + str(filename))
    sets = pd.read_csv(filename, delim_whitespace=True, header=None)

    sets = sets.transpose()

    return sets


def load_timeseries_trim(filename, limit_series=10, limit_values=800):
    print("\t\t >> LOAD SERIES " + str(filename))
    sets = pd.read_csv(filename, delim_whitespace=True, header=None)
    sets = sets.iloc[:limit_values, :limit_series]

    sets = sets.transpose()
    
    return sets

def print_load(ts):
    if not isinstance(ts, pd.DataFrame):
        ts = pd.DataFrame(ts)

    print("\t\t >> NBR Series : ", ts.shape[0], " x ", ts.shape[1])
    print(ts.head())


def normalize_min_max(ts):
    print("\t\t >> NORMALIZATION MIN/MAX")

    if not isinstance(ts, pd.DataFrame):
        ts = pd.DataFrame(ts)

    data_normalized = (ts - ts.min()) / (ts.max() - ts.min())

    return data_normalized, data_normalized.to_numpy()


def plot_ts(ts, title='Time Series Data', ind=5):
    plt.figure(figsize=(14, 7))
    inc = 0

    for i in range(ts.shape[0]):
        plt.plot(ts.columns, ts.iloc[i], label=f'Series {i + 1}')
        inc += 1

        if inc == ind:
            break

    plt.xlabel('Index')
    plt.ylabel('Values')
    plt.title(title)
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.show()



print(">> STARTING OPERATION : NATERQ CHINA TESTS *****************************")



# =====================================================================================


def converter(ts):
    if isinstance(ts, pd.DataFrame):
        ts.to_numpy()
    return ts

def disconverter(ts):
    if not isinstance(ts, pd.DataFrame):
        ts = pd.DataFrame(ts)
    return ts


def introduce_mcar(ts, missing_rate, series_selected, keep_other=False):

    ts = disconverter(ts)

    print("\t\t\t>> MCAR : RATE ", missing_rate, " / keep other ", keep_other, " / series selected ", *series_selected, "*****\n")

    ts_contaminated = ts.copy()
    n_series, n_values = ts_contaminated.shape

    # protect the 10% before
    start_index = int(math.ceil((n_values * FACTOR_S)))

    if keep_other:
        population = (n_values - start_index) * len(series_selected)
    else:
        population = (n_values - start_index) * n_series

    to_remove = int(math.ceil(population * missing_rate))

    print("\t\t\t>> MCAR : population ", population, " / to_remove ", to_remove, "*****\n")

    np.random.seed(SEED)
    missing_indices = np.random.choice(population, int(to_remove/BLOCK_SIZE), replace=False)

    if keep_other:
        for index in missing_indices:
            for i in range(0, BLOCK_SIZE):
                row = series_selected[index % len(series_selected)]
                col = (index // len(series_selected)) + start_index

                if col >= (n_values - BLOCK_SIZE - 1):
                    col = col - (n_values - start_index)

                ts_contaminated.iat[row, col+i] = np.nan
    else:
        for index in missing_indices:
            for i in range(0, BLOCK_SIZE):
                row = index % n_series
                col = (index // n_series) + start_index + i
                if col >= (n_values - start_index):
                    col = col - (n_values - start_index)
                ts_contaminated.iat[row, col] = np.nan

    return ts_contaminated, ts_contaminated.to_numpy()



def introduce_blackout(ts, missing_rate, series_selected, keep_other=False):

    ts = disconverter(ts)

    print("\t\t\t>> BLACKOUT : RATE ", missing_rate, " / keep other ", keep_other, " / series selected ", *series_selected, "*****\n")

    ts_contaminated = ts.copy()
    n_series, n_values = ts_contaminated.shape
    start_index = int(math.ceil((n_values * FACTOR_S)))
    population = (n_values - start_index)
    to_remove = int(math.ceil(population * missing_rate))

    if keep_other:
        for series in range(0, n_series):
            for col in range(population):
                if series in series_selected:
                    if col <= to_remove:
                        ts_contaminated.iat[series, col+start_index] = np.nan
    else:
        for series in range(0, n_series):
            for col in range(population):
                    if col <= to_remove:
                        ts_contaminated.iat[series, col+start_index] = np.nan

    return ts_contaminated, ts_contaminated.to_numpy()


def introduce_disjoint(ts, missing_rate, series_selected, keep_other = False):

    ts = disconverter(ts)

    print("\t\t\t>> DISJOINT : RATE ", missing_rate, " / keep other ", keep_other, " / series selected ", *series_selected, "*****\n")

    ts_contaminated = ts.copy()
    n_series, n_values = ts_contaminated.shape

    # protect the 10% before
    start_index = int(math.ceil((n_values * FACTOR_S)))
    population = (n_values - start_index)
    to_remove = int(math.ceil(population * missing_rate))

    if keep_other:
        for series in range(0, n_series):
            if series in series_selected:
                for index in range (0, to_remove):
                    shift_computation = (index + start_index) + (to_remove * series)
                    while shift_computation >= n_values:
                        shift_computation = shift_computation - population

                    ts_contaminated.iat[series, shift_computation] = np.nan
    else:
        for series in range(0, n_series):
            for index in range (0, to_remove):
                shift_computation = (index + start_index) + (to_remove * series)
                while shift_computation >= n_values:
                    shift_computation = shift_computation - population
                ts_contaminated.iat[series, shift_computation] = np.nan

    return ts_contaminated, ts_contaminated.to_numpy()


def introduce_overlap(ts, missing_rate, series_selected, factor=0.05, keep_other = False):

    ts = disconverter(ts)

    print("\t\t\t>> OVERLAP : RATE ", missing_rate, " / keep other ", keep_other, " / series selected ", *series_selected, "*****\n")

    ts_contaminated = ts.copy()
    n_series, n_values = ts_contaminated.shape

    start_index = int(math.ceil((n_values * (FACTOR_S))))
    population = (n_values - start_index)
    start_index = start_index
    to_remove = int(math.ceil(population * missing_rate))

    if keep_other:
        for series in range(0, n_series):
            if series in series_selected:
                for index in range(0, to_remove):
                    shift_computation = (index + start_index) + (to_remove * series) - (int(population * factor) * series)
                    while shift_computation >= n_values:
                        shift_computation = shift_computation - population
                    ts_contaminated.iat[series, shift_computation] = np.nan
    else:
        for series in range(0, n_series):
            for index in range(0, to_remove):
                shift_computation = (index + start_index) + (to_remove * series) - (int(population * factor) * series)
                while shift_computation >= n_values:
                    shift_computation = shift_computation - population
                ts_contaminated.iat[series, shift_computation] = np.nan

    return ts_contaminated, ts_contaminated.to_numpy()



if __name__ == '__main__':

    load_sets = ["../Datasets/drift/drift10_normal.txt", "./sets/test.txt"]
    ts = load_timeseries_trim(load_sets[0])

    print_load(ts)
    plot_ts(ts, "Plain Time Series")

    ts, _ = normalize_min_max(ts)
    print_load(ts)
    plot_ts(ts, "MIN-MAX Normalization")


    contamination_rates = [0, 0.05, 0.1, 0.2, 0.4, 0.6]
    series_selected = [0,2,9]
    patterns = ["blackout", "mcar", "disjoint", "overlap"]
    keep = False


    ts_norm, _ = normalize_min_max(ts)

    if not keep:
        time_series_selected = ts.loc[series_selected]
    else:
        time_series_selected = ts

    for pattern in patterns:
        if pattern == "mcar":
            pattern_ts, _ = introduce_mcar(time_series_selected, contamination_rates[3], series_selected, keep_other=keep)
        elif pattern == "blackout":
            pattern_ts, _ = introduce_blackout(time_series_selected, contamination_rates[3], series_selected, keep_other=keep)
        elif pattern == "disjoint":
            pattern_ts, _ = introduce_disjoint(time_series_selected, contamination_rates[2], series_selected, keep_other=keep)
        elif pattern == "overlap":
            pattern_ts, _ = introduce_overlap(time_series_selected, contamination_rates[2], series_selected, 0.1, keep_other=keep)
        else :
            pattern_ts = time_series_selected

        #print_load(pattern_ts)
        plot_ts(pattern_ts, pattern, 10)