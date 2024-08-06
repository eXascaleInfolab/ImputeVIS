import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

from matplotlib import MatplotlibDeprecationWarning

warnings.filterwarnings("ignore", category=MatplotlibDeprecationWarning)


def load_timeseries (filename) :
    print("\t\t >> LOAD SERIES " + str(filename))
    return pd.read_csv(filename, delim_whitespace=True, header=None)


def print_load(ts):
    print("\t\t >> NBR Series : " + str(ts.shape[1]))
    print(ts.head())


def normalize_min_max(ts):
    print("\t\t >> NORMALIZATION MIN/MAX")
    data_normalized = (ts - ts.min()) / (ts.max() - ts.min())
    return data_normalized


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

def introduce_mcar(ts, missing_rate, series_selected, keep_other=False):

    print("\t\t\t>> MCAR : RATE ", missing_rate, " / keep other ", keep_other, " / series selected ", *series_selected, "*****\n")

    ts_contaminated = ts.copy()
    n_series, n_values = ts_contaminated.shape

    # protect the 10% before
    start_index = int(math.ceil((n_values * 0.1)))

    if keep_other:
        population = (n_values - start_index) * len(series_selected)
    else:
        population = (n_values - start_index) * n_series

    to_remove = int(math.ceil(population * missing_rate))

    missing_indices = np.random.choice(population, to_remove, replace=False)

    print("missing_indices", missing_indices)

    if keep_other:
        for index in missing_indices:
            row = series_selected[index % len(series_selected)]
            col = (index // len(series_selected)) + start_index
            ts_contaminated.iat[row, col] = np.nan
    else:
        for index in missing_indices:
            row = index % n_series
            col = (index // n_series) + start_index
            ts_contaminated.iat[row, col] = np.nan

    return ts_contaminated



def introduce_blackout(ts, missing_rate, series_selected, keep_other=False):

    print("\t\t\t>> BLACKOUT : RATE ", missing_rate, " / keep other ", keep_other, " / series selected ", *series_selected, "*****\n")

    ts_contaminated = ts.copy()
    n_series, n_values = ts_contaminated.shape

    # protect the 10% before
    start_index = int(math.ceil((n_values * 0.1)))
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

    return ts_contaminated


def introduce_disjoint(ts, missing_rate, series_selected, keep_other = False):

    print("\t\t\t>> DISJOINT : RATE ", missing_rate, " / keep other ", keep_other, " / series selected ", *series_selected, "*****\n")

    ts_contaminated = ts.copy()
    n_series, n_values = ts_contaminated.shape

    # protect the 10% before
    start_index = int(math.ceil((n_values * 0.1)))
    population = (n_values - start_index)
    to_remove = int(math.ceil(population * missing_rate))

    if keep_other:
        for series in range(0, n_series):
            if series in series_selected:
                for index in range (0, to_remove):
                    shift_computation = (index + start_index) + (to_remove * series)
                    if shift_computation >= n_values:
                        shift = shift_computation - n_values
                        shift_computation = start_index + shift
                    ts_contaminated.iat[series, shift_computation] = np.nan
    else:
        for series in range(0, n_series):
            for index in range (0, to_remove):
                shift_computation = (index + start_index) + (to_remove * series)
                if shift_computation >= n_values:
                    shift = shift_computation - n_values
                    shift_computation = start_index + shift
                ts_contaminated.iat[series, shift_computation] = np.nan

    return ts_contaminated


def introduce_overlap(ts, missing_rate, series_selected, factor=0.05, keep_other = False):

    print("\t\t\t>> OVERLAP : RATE ", missing_rate, " / keep other ", keep_other, " / series selected ", *series_selected, "*****\n")

    ts_contaminated = ts.copy()
    n_series, n_values = ts_contaminated.shape

    start_index = int(math.ceil((n_values * 0.1)))
    population = (n_values - start_index)
    to_remove = int(math.ceil(population * missing_rate))

    if keep_other:
        for series in range(0, n_series):
            if series in series_selected:
                for index in range(0, to_remove):
                    shift_computation = (index + start_index) + (to_remove * series) - int(population * factor)
                    if shift_computation >= n_values:
                        shift = shift_computation - n_values
                        shift_computation = start_index + shift
                    ts_contaminated.iat[series, shift_computation] = np.nan
    else:
        for series in range(0, n_series):
            for index in range(0, to_remove):
                shift_computation = (index + start_index) + (to_remove * series) - int(population*factor)
                if shift_computation >= n_values:
                    shift = shift_computation - n_values
                    shift_computation = start_index + shift
                ts_contaminated.iat[series, shift_computation] = np.nan

    return ts_contaminated




load_sets = ["../Datasets/drift/drift10_normal.txt", "./test.txt"]
ts = load_timeseries(load_sets[0])
print_load(ts)
plot_ts(ts)

ts_min_max = normalize_min_max(ts)
print_load(ts_min_max)
plot_ts(ts_min_max)


contamination_rates = [0, 0.05, 0.1, 0.2, 0.4, 0.6]
series_selected = [0, 1, 3]
patterns = ["blackout", "mcar", "disjoint", "overlap"]
keep = False


ts_norm = normalize_min_max(ts)

if not keep:
    time_series_selected = ts.loc[series_selected]
else:
    time_series_selected = ts

for pattern in patterns:
    if pattern == "mcar":
        pattern_ts = introduce_mcar(time_series_selected, contamination_rates[3], series_selected, keep_other=keep)
    elif pattern == "blackout":
        pattern_ts = introduce_blackout(time_series_selected, contamination_rates[3], series_selected, keep_other=keep)
    elif pattern == "disjoint":
        pattern_ts = introduce_disjoint(time_series_selected, contamination_rates[2], series_selected, keep_other=keep)
    elif pattern == "overlap":
        pattern_ts = introduce_overlap(time_series_selected, contamination_rates[2], series_selected, 0.05, keep_other=keep)
    else :
        pattern_ts = time_series_selected

    print_load(pattern_ts)
    plot_ts(pattern_ts, pattern, 10)