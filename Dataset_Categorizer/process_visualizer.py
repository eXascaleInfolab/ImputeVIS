import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf
from scipy.signal import find_peaks


def detrend_spline_and_peak(y, knot_position=0.5, plot=False):
    """
    Detrend a time series using a single-knot cubic regression spline and find the
    first peak in the auto-correlation function of the detrended series.

    Parameters
    ----------
    y : array-like
        The input time series.
    knot_position : float, optional
        The relative position of the knot in the range [0, 1]. Default is 0.5 (middle).
    plot : bool, optional
        If True, plot the original series, predicted trend, detrended series, and ACF with peak. Default is False.

    Returns
    -------
    detrended_y : ndarray
        The detrended time series.
    first_peak : int
        The lag at which the first peak in the ACF is observed.

    Notes
    -----
    This function uses `statsmodels` for OLS regression and ACF computation. The time variable
    is automatically generated based on the length of `y`.

    Examples
    --------
    >>> y = np.sin(np.linspace(0, 10, 100)) + np.random.normal(0, 0.1, 100)
    >>> detrended_y, first_peak = detrend_spline_and_peak(y)
    """

    # Generate time variable
    time = np.linspace(0, len(y) - 1, len(y))

    # Calculate absolute knot position
    knot = time[0] + knot_position * (time[-1] - time[0])

    # Create spline basis functions
    time_before = np.where(time <= knot, time, 0)
    time_after = np.where(time > knot, time - knot, 0)

    X = np.column_stack([
        np.ones_like(time),
        time_before, time_before ** 2, time_before ** 3,
        time_after, time_after ** 2, time_after ** 3
    ])

    # Fit the model
    model = sm.OLS(y, X).fit()
    predicted_trend = model.predict(X)

    # Detrend the series
    detrended_y = y - predicted_trend
    detrended_y_to_plot = detrended_y.copy()[:,1]
    y_to_plot = y.copy()[:,1]

    if plot:
        plt.figure(figsize=(10, 6))
        plt.plot(time, y_to_plot, label='Original Series')
        #plt.plot(time, predicted_trend, label='Predicted Trend', linestyle='--')
        plt.plot(time, detrended_y_to_plot, label='Detrended Series')
        plt.axvline(x=knot, color='red', linestyle=':', label='Knot')
        plt.legend()
        file_name = f"results/meteo_detrended_series.png"
        plt.savefig(file_name)
        plt.show()

    # Compute the ACF of the detrended series
    acf_values = acf(detrended_y_to_plot, fft=True, nlags=len(y_to_plot) - 1)

    # Find peaks in the ACF
    peaks, _ = find_peaks(acf_values)

    # Get the first peak if exists, else set to None
    first_peak = peaks[0] if peaks.size else None

    if plot:

        plt.figure(figsize=(10, 6))
        plt.stem(acf_values, use_line_collection=True, basefmt=" ", linefmt="-b", markerfmt="ob")
        #plt.set_title('Auto-correlation Function')
        if first_peak is not None:
            plt.plot(first_peak, acf_values[first_peak], 'or', markersize=10, label='First Peak')
            plt.legend()


        # Plotting the series and trend
        #fig, axs = plt.subplots(2, 1, figsize=(10, 8))

        # Original, trend, detrended
#         axs[0].plot(y_to_plot, label='Original Series')
# #        axs[0].plot(detrended_y_to_plot + predicted_trend, label='Predicted Trend', linestyle='--')
#         axs[0].plot(detrended_y_to_plot, label='Detrended Series')
#         axs[0].axvline(x=knot, color='red', linestyle=':', label='Knot')
#         axs[0].legend()

        # ACF
        # axs[1].stem(acf_values, use_line_collection=True, basefmt=" ", linefmt="-b", markerfmt="ob")
        # axs[1].set_title('Auto-correlation Function')
        # if first_peak is not None:
        #     axs[1].plot(first_peak, acf_values[first_peak], 'or', markersize=10, label='First Peak')
        #     axs[1].legend()

        plt.tight_layout()
        file_name = f"results/meteo_acf_first_peak.png"
        plt.savefig(file_name)
        plt.show()

    return detrended_y, first_peak


def main():
    # Sample usage
    np.random.seed(42)
    y_sample = np.sin(np.linspace(0, 10, 100)) + np.random.normal(0, 0.1, 100)
    y_sample = np.loadtxt("../Datasets/meteo/raw_matrices/meteo_normal_full_eighth.txt", delimiter=" ", )
    detrended_y_sample, first_peak_sample = detrend_spline_and_peak(y_sample[4000:6000,], plot=True)

    print(f"First ACF Peak at lag: {first_peak_sample}")

if __name__ == "__main__":
    main()