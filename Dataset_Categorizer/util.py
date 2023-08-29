import numpy as np
from typing import Dict

from Dataset_Categorizer import catch

CATEGORIES = {
    'Geometry': [
        'SB_BinaryStats_mean_longstretch1',
        'SB_BinaryStats_diff_longstretch0',
        'SB_TransitionMatrix_3ac_sumdiagcov',
        'MD_hrv_classic_pnn40',
        'DN_HistogramMode_5',
        'DN_HistogramMode_10',
        'DN_OutlierInclude_p_001_mdrmd',
        'DN_OutlierInclude_n_001_mdrmd',
        'CO_Embed2_Dist_tau_d_expfit_meandiff',
        'SC_FluctAnal_2_dfa_50_1_2_logi_prop_r1',
        'SC_FluctAnal_2_rsrangefit_50_1_logi_prop_r1'
    ],
    'Correlation': [
        'CO_f1ecac',
        'CO_FirstMin_ac',
        'CO_trev_1_num',
        'CO_HistogramAMI_even_2_5',
        'IN_AutoMutualInfoStats_40_gaussian_fmmi',
        'FC_LocalSimple_mean1_tauresrat'
    ],
    'Transformation': [
        'SP_Summaries_welch_rect_area_5_1',
        'SP_Summaries_welch_rect_centroid'
    ],
    'Trend': [
        'PD_PeriodicityWang_th0_01',
        'FC_LocalSimple_mean3_stderr',
        'SB_MotifThree_quantile_hh'
    ]
}

feature_description_mapper = {
    "DN_HistogramMode_5": "5-bin histogram mode",
    "DN_HistogramMode_10": "10-bin histogram mode",
    "DN_OutlierInclude_p_001_mdrmd": "Positive outlier timing",
    "DN_OutlierInclude_n_001_mdrmd": "Negative outlier timing",
    "ﬁrst1e_acf_tau": "First 1/e crossing of the ACF",
    "ﬁrstMin_acf": "First minimum of the ACF",
    "SP_Summaries_welch_rect_area_5_1": "Power in lowest 20% frequencies",
    "SP_Summaries_welch_rect_centroid": "Centroid frequency",
    "FC_LocalSimple_mean3_stderr": "Error of 3-point rolling mean forecast",
    "FC_LocalSimple_mean1_tauresrat": "Change in autocorrelation timescale after incremental differencing",
    "MD_hrv_classic_pnn40": "Proportion of high incremental changes in the series",
    "SB_BinaryStats_mean_longstretch1": "Longest stretch of above-mean values",
    "SB_BinaryStats_diff_longstretch0": "Longest stretch of decreasing values",
    "SB_MotifThree_quantile_hh": "Entropy of successive pairs in symbolized series",
    "CO_HistogramAMI_even_2_5": "Histogram-based automutual information (lag 2, 5 bins)",
    "CO_trev_1_num": "Time reversibility",
    "IN_AutoMutualInfoStats_40_gaussian_fmmi": "First minimum of the AMI function",
    "SB_TransitionMatrix_3ac_sumdiagcov": "Transition matrix column variance",
    "PD_PeriodicityWang_th001": "Wang's periodicity metric",
    "CO_Embed2_Dist_tau_d_expfit_meandiff": "Goodness of exponential fit to embedding distance distribution",
    "SC_FluctAnal_2_rsrangeﬁt_50_1_logi_prop_r1": "Rescaled range fluctuation analysis (low-scale scaling)",
    "SC_FluctAnal_2_dfa_50_1_2_logi_prop_r1": "Detrended fluctuation analysis (low-scale scaling)",
    "mean": "Mean",
    "DN_Spread_Std": "Standard deviation"
}


def replace_feature_name_with_description(input_string: str, mapper: Dict[str, str]) -> str:
    """
    Replaces occurrences of feature names with their descriptions in the provided string.

    Parameters
    ----------
    input_string : str
        The string where replacements need to be made.
    mapper : Dict[str, str]
        The dictionary mapping feature names to their descriptions.

    Returns
    -------
    str
        The modified string with feature names replaced by descriptions.

    Example
    -------
    >>> replace_feature_name_with_description("This is a DN_HistogramMode_5 and DN_HistogramMode_10.", feature_description_mapper)
    'This is a 5-bin histogram mode and 10-bin histogram mode.'
    """

    for feature_name, description in mapper.items():
        input_string = input_string.replace(feature_name, description)
    return input_string


def results_to_latex(extracted_features: dict) -> str:
    """
    Transforms results into LaTeX table format.

    Parameters
    ----------
    extracted_features : dict
        Dictionary containing extracted features.

    Returns
    -------
    str
        The resulting LaTeX formatted string.
    """

    latex_output = '\\begin{table}[!h]\n'
    latex_output += '\\centering\n'
    latex_output += '\\caption{Features from different categories}\n'
    latex_output += '\\begin{tabular}{|c|c|}\n'
    latex_output += '\\hline\n'
    latex_output += '\\textbf{Feature Name} & \\textbf{Value} \\\\ \\hline\n'
    # Loop through categories and add each as a section to the table
    for category, features in CATEGORIES.items():
        latex_output += category_to_latex_section(category, features, extracted_features)

    # End the table
    latex_output += '\\end{tabular}\n'
    latex_output += '\\end{table}\n'
    return latex_output


def category_to_latex_section(category, features, category_data):
    latex_section = '\\textbf{%s} & \\\\ \n' % category
    for feature in features:
        latex_section += '%s & %s \\\\ \n' % (
            escape_underscores(feature), format(round(category_data.get(feature, 0), 4), '.3g'))
    latex_section += '\\midrule\n'
    return latex_section


def category_to_latex_table(category, features, category_data):
    # Start the table
    latex_output = '\\begin{table}[!h]\n'
    latex_output += '\\centering\n'
    latex_output += '\\caption{Features from different categories}\n'
    latex_output += '\\begin{tabular}{cc}\n'
    latex_output += '\\toprule\n'
    latex_output += 'Feature Name & Value \\\\ \n'
    latex_output += '\\midrule\n'

    # Loop through categories and add each as a section to the table
    for category, features in CATEGORIES.items():
        latex_output += category_to_latex_section(category, features, category_data)

    # End the table
    latex_output = latex_output.rstrip('\\midrule\n')  # Remove the last midrule
    latex_output += '\\bottomrule\n'
    latex_output += '\\end{tabular}\n'
    latex_output += '\\end{table}\n'
    return latex_output


def results_to_latex_in_one(all_extracted_features: dict) -> str:
    """
    Transforms results from multiple datasets into a single LaTeX table format.

    Parameters
    ----------
    all_extracted_features : dict
        Dictionary containing extracted features for each dataset.

    Returns
    -------
    str
        The resulting LaTeX formatted string.
    """

    # Table header
    datasets = list(all_extracted_features.keys())
    header = '\\textbf{Feature Name} & ' + ' & '.join(
        ['\\textbf{%s}' % ds.capitalize() for ds in datasets]) + ' \\\\ \\hline\n'

    # Generate table content based on categories
    content = ''
    for category, features in CATEGORIES.items():
        content += '\\textbf{%s} & \\\\ \\midrule\n' % category
        for feature in features:
            content += escape_underscores(feature) + ' & '
            content += ' & '.join(
                [format(round(all_extracted_features[dataset].get(feature, 0), 4), '.3g') for dataset in
                 datasets]) + ' \\\\ \n'
        content += '\\midrule\n'

    # Combine header and content into the table
    latex_output = '''\\begin{table}[!h]
\\centering
\\caption{Features from different categories}
\\begin{tabular}{l''' + 'c' * len(datasets) + '''}
\\toprule
''' + header + content.rstrip('\\midrule\n') + '''\\bottomrule
\\end{tabular}
\\end{table}'''

    return latex_output


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


def main():
    # datasets = ['bafu', 'chlorine', 'climate', 'drift', 'meteo']
    # dataset_files = ['BAFU', 'cl2fullLarge', 'climate', 'batch10', 'meteo_total']
    # # Store all extracted features for each dataset
    # all_results = {}
    #
    # for dataset, data_file in zip(datasets, dataset_files):
    #     raw_file_path = f"../Datasets/{dataset}/raw_matrices/{data_file}_eighth.txt"
    #     if dataset == 'drift':
    #         raw_file_path = f"../Datasets/{dataset}/drift10/raw_matrices/{data_file}_eighth.txt"
    #     raw_matrix = np.loadtxt(raw_file_path, delimiter=" ")
    #
    #     # # Extract features
    #     # results = catch.extract_features(raw_matrix)
    #     #
    #     # # Convert to LaTeX format
    #     # latex_format = results_to_latex(results)
    #     # # print(latex_format)
    #     # with open(f"results/latex_table_{dataset}.txt", 'w') as f:
    #     #     f.write(latex_format)
    #
    #     # Extract features and store in the dictionary
    #     all_results[dataset] = catch.extract_features(raw_matrix)
    #
    # # Convert the combined results into LaTeX format
    # latex_format = results_to_latex_in_one(all_results)
    #
    # # Save to a single file
    # with open("results/latex_table_combined.txt", 'w') as f:
    #     f.write(latex_format)

    test_string = """
    \\section*{Geometry}
    Features related to Geometry include statistical properties and characteristics that describe the distribution of the time series data points.
    \\begin{itemize}
        \\item \\texttt{SB_BinaryStats_mean_longstretch1}: The longest period of consecutive values above the mean.
        \\item \\texttt{SB_BinaryStats_diff_longstretch0}: Longest period of successive incremental decreases.
        \\item \\texttt{SB_TransitionMatrix_3ac_sumdiagcov}: Trace of the covariance of the transition matrix between symbols in the 3-letter alphabet.
        \\item \\texttt{MD_hrv_classic_pnn40}: Proportion of successive differences exceeding \\(0.04\\sigma\\).
        \\item \\texttt{DN_HistogramMode_5}: Mode of the z-scored distribution estimated using a 5-bin histogram.
        \\item \\texttt{DN_HistogramMode_10}: Mode of the z-scored distribution estimated using a 10-bin histogram.
        \\item \\texttt{DN_OutlierInclude_p_001_mdrmd}: Time intervals between successive extreme events above the mean.
        \\item \\texttt{DN_OutlierInclude_n_001_mdrmd}: Time intervals between successive extreme events below the mean.
        \\item \\texttt{CO_Embed2_Dist_tau_d_expfit_meandiff}: Exponential fit to successive distances in 2-dimensional embedding space.
        \\item \\texttt{SC_FluctAnal_2_dfa_50_1_2_logi_prop_r1}: Proportion of slower time-scale fluctuations that scale with DFA (50\\% sampling).
        \\item \\texttt{SC_FluctAnal_2_rsrangefit_50_1_logi_prop_r1}: Proportion of slower timescale fluctuations that scale with linearly rescaled range fits.
    \\end{itemize}

    \\section*{Correlation}
    This category contains autocorrelation and partial correlation properties.
    \\begin{itemize}
        \\item \\texttt{CO_f1ecac}: First \\(1/e\\) crossing of the autocorrelation function.
        \\item \\texttt{CO_FirstMin_ac}: First minimum of the autocorrelation function.
        \\item \\texttt{CO_trev_1_num}: Time-reversibility statistic.
        \\item \\texttt{CO_HistogramAMI_even_2_5}: Automutual information, \\(m = 2\\), \\(\\tau = 5\\).
        \\item \\texttt{IN_AutoMutualInfoStats_40_gaussian_fmmi}: First minimum of the automutual information function.
        \\item \\texttt{FC_LocalSimple_mean1_tauresrat}: Change in the length of the correlation after iterative differencing.
    \\end{itemize}

    \\section*{Transformation}
    This category includes features that are derived from transformations of the time series, including transformation coefficients.
    \\begin{itemize}
        \\item \\texttt{SP_Summaries_welch_rect_area_5_1}: Total power in the lowest fifth of frequencies in the Fourier power spectrum.
        \\item \\texttt{SP_Summaries_welch_rect_centroid}: Centroid of the Fourier power spectrum.
    \\end{itemize}

    \\section*{Trend}
    Features that are derived from regression models, explain the trend and seasonality, or are often used for forecasting are included in Trend.
    \\begin{itemize}
        \\item \\texttt{PD_PeriodicityWang_th0_01}: Periodicity measure.
        \\item \\texttt{FC_LocalSimple_mean3_stderr}: Mean error from rolling 3-sample mean forecasting.
        \\item \\texttt{SB_MotifThree_quantile_hh}: Shannon entropy of two successive letters in an equiprobable 3-letter symbolization of the time series.
    \\end{itemize}
    """
    print(replace_feature_name_with_description(test_string, feature_description_mapper))


if __name__ == "__main__":
    main()
