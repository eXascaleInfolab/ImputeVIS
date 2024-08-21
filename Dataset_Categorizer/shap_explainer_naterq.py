import math
import numpy as np
import shap
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor

import sys
import os



# Add the parent directory to the Python path
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
sys.path.append(parent_directory)

# Now you can import the module
try:
    import Optimizer
    from Optimizer import evaluate_params
    from Dataset_Categorizer import catch
    from parameterizer import views
    import Wrapper.algo_collection
except ImportError as e:
    print(f"ImportError: {e}")
    print("Make sure the directory structure is correct and the module is accessible.")
    print("Updated Python path:", sys.path)

CATEGORIES = {
  "Geometry": [
    "SB_BinaryStats_mean_longstretch1",
    "SB_BinaryStats_diff_longstretch0",
    "SB_TransitionMatrix_3ac_sumdiagcov",
    "MD_hrv_classic_pnn40",
    "DN_HistogramMode_5",
    "DN_HistogramMode_10",
    "DN_OutlierInclude_p_001_mdrmd",
    "DN_OutlierInclude_n_001_mdrmd",
    "CO_Embed2_Dist_tau_d_expfit_meandiff",
    "SC_FluctAnal_2_dfa_50_1_2_logi_prop_r1",
    "SC_FluctAnal_2_rsrangefit_50_1_logi_prop_r1"
  ],
  "Correlation": [
    "CO_f1ecac",
    "CO_FirstMin_ac",
    "CO_trev_1_num",
    "CO_HistogramAMI_even_2_5",
    "IN_AutoMutualInfoStats_40_gaussian_fmmi",
    "FC_LocalSimple_mean1_tauresrat"
  ],
  "Transformation": [
    "SP_Summaries_welch_rect_area_5_1",
    "SP_Summaries_welch_rect_centroid"
  ],
  "Trend": [
    "PD_PeriodicityWang_th0_01",
    "FC_LocalSimple_mean3_stderr",
    "SB_MotifThree_quantile_hh"
  ]
}

FEATURES = {"SB_BinaryStats_mean_longstretch1" : "Longest stretch of above-mean values",
                "SB_BinaryStats_diff_longstretch0":"Longest stretch of decreasing values",
                "SB_TransitionMatrix_3ac_sumdiagcov":"Transition matrix column variance",
                "MD_hrv_classic_pnn40" : "Proportion of high incremental changes in the series",
                "DN_HistogramMode_5":"5-bin histogram mode",
                "DN_HistogramMode_10":"10-bin histogram mode",
                "DN_OutlierInclude_p_001_mdrmd":"Positive outlier timing",
                "DN_OutlierInclude_n_001_mdrmd":"Negative outlier timing",
                "CO_Embed2_Dist_tau_d_expfit_meandiff":"Goodness of exponential fit to embedding distance distribution",
                "SC_FluctAnal_2_dfa_50_1_2_logi_prop_r1":"Detrended fluctuation analysis (low-scale scaling)",
                "SC_FluctAnal_2_rsrangefit_50_1_logi_prop_r1":"Rescaled range fluctuation analysis (low-scale scaling)",
                "CO_f1ecac":"First 1/e crossing of the ACF",
                "CO_FirstMin_ac" :"First minimum of the ACF",
                "CO_trev_1_num":"Time reversibility",
                "CO_HistogramAMI_even_2_5":"Histogram-based automutual information (lag 2, 5 bins)",
                "IN_AutoMutualInfoStats_40_gaussian_fmmi":"First minimum of the AMI function",
                "FC_LocalSimple_mean1_tauresrat":"Change in autocorrelation timescale after incremental differencing",
                "SP_Summaries_welch_rect_area_5_1":"Power in the lowest 20% of frequencies",
                "SP_Summaries_welch_rect_centroid":"Centroid frequency",
                "PD_PeriodicityWang_th0_01":"Wangs periodicity metric",
                "FC_LocalSimple_mean3_stderr":"Error of 3-point rolling mean forecast",
                "SB_MotifThree_quantile_hh":"Entropy of successive pairs in symbolized series"}


def convert_results(tmp, file, algo, descriptions, features, categories, mean_features):

    print("\n\n----------CONVERT : ", tmp)
    print("\n\n----------CONVERT : ", np.array(tmp).shape)

    result_display, display_details, result_shap = [], [], []
    for x, rate in enumerate(tmp):
        if math.isnan(rate) == False:
            rate = float(round(rate, 2))

        result_display.append((x, algo, rate, descriptions[0][x], features[0][x], categories[0][x], mean_features[x]))

    result_display = sorted(result_display, key=lambda tup: (tup[1], tup[2]), reverse=True)

    for (x, algo, rate, description, feature, categorie, mean_features) in result_display:
        print(x, " : ", algo, " with a score of ", rate, "  (", description, " / ", feature, " / ", categorie, ")\n")
        result_shap.append([file, algo, rate, description, feature, categorie, mean_features])

    print("----------CONVERT : ", np.array(result_shap).shape)

    return result_shap


def launch_shap_model(x_dataset, x_information, y_dataset, file, algorithm, splitter=10):
    print("\n\n======= SHAP >> MODEL ======= shape set : ", np.array(x_information).shape, "======= ======= ======= ======= ======= ======= ======= ======= ======= ")

    x_features, x_categories, x_descriptions = [], [], []
    x_fs, x_cs, x_ds = [], [], []

    for current_time_series in x_information:
        x_fs.clear()
        x_cs.clear()
        x_ds.clear()
        for feature_name, category_value, feature_description in current_time_series:
            x_fs.append(feature_name)
            x_cs.append(category_value)
            x_ds.append(feature_description)
        x_features.append(x_fs)
        x_categories.append(x_cs)
        x_descriptions.append(x_ds)

    x_dataset = np.array(x_dataset)
    y_dataset = np.array(y_dataset)

    x_features = np.array(x_features)
    x_categories = np.array(x_categories)
    x_descriptions = np.array(x_descriptions)


    # NORMALIZATION ! ========================================
    #x_min = np.min(x_dataset)
    #x_max = np.max(x_dataset)
    #x_dataset = (x_dataset - x_min) / (x_max - x_min)

    # Split the data
    x_train, x_test = x_dataset[:splitter], x_dataset[splitter:]
    y_train, y_test = y_dataset[:splitter], y_dataset[splitter:]

    # Print shapes to verify
    print("\t SHAP_MODEL >> NATERQ x_train shape:", x_train.shape)
    print("\t SHAP_MODEL >> NATERQ y_train shape:", y_train.shape)
    print("\t SHAP_MODEL >> NATERQ x_test shape:", x_test.shape)
    print("\t SHAP_MODEL >> NATERQ y_test shape:", y_test.shape, "\n")
    print("\t SHAP_MODEL >> NATERQ x_features shape:", x_features.shape)
    print("\t SHAP_MODEL >> NATERQ x_categories shape:", x_categories.shape)
    print("\t SHAP_MODEL >> NATERQ x_descriptions shape:", x_descriptions.shape, "\n")
    print("\t SHAP_MODEL >> NATERQ FEATURES OK:", np.all(np.all(x_features == x_features[0,:], axis=1)))
    print("\t SHAP_MODEL >> NATERQ x_categories OK:", np.all(np.all(x_categories == x_categories[0,:], axis=1)))
    print("\t SHAP_MODEL >> NATERQ x_descriptions OK:", np.all(np.all(x_descriptions == x_descriptions[0,:], axis=1)), "\n\n")

    model = RandomForestRegressor()
    model.fit(x_train, y_train)

    exp = shap.KernelExplainer(model.predict, x_test)
    shval = exp.shap_values(x_test)

    print("\t\t SHAP_MODEL >>  NATERQ shval selected : ", np.array(shval).shape, "************************************")
    print("\t\t SHAP_MODEL >>  NATERQ shval selected : \t", *shval)

    optimal_display = []
    for desc, group in zip(x_descriptions[0], x_categories[0]):
        optimal_display.append(desc + " (" + group + ")")

    shap.summary_plot(shval, x_test, plot_size=(25, 10), feature_names=optimal_display)
    alpha = "parameterizer_frontend/src/assets_naterq/" + file + "_" + algorithm + "_shap_plot.png"
    plt.title("SHAP Details Results")
    plt.savefig(alpha)
    plt.close()

    print("\n\n\t\t\tSHAP_BUILD_____________________________________________________________________")
    total_weights_for_all_algorithms = []

    t_shval = np.array(shval).T
    t_Xtest = np.array(x_test).T

    # NORMALIZATION ! ========================================
    #x_min = np.min(t_shval)
    #x_max = np.max(t_shval)
    #t_shval = (t_shval - x_min) / (x_max - x_min)

    aggregation_features, aggregation_test = [], []

    print("\t\t\tSHAP_BUILD >>  NATERQ t_shval shape : ", np.array(t_shval).shape, "************************************")
    print("\t\t\tSHAP_BUILD >>  NATERQ t_Xtest shape : ", np.array(t_Xtest).shape)

    geometry, correlation, transformation, trend = [], [], [], []
    geometryDesc, correlationDesc, transformationDesc, trendDesc = [], [], [], []

    for index, feat in enumerate(t_shval):
        if x_categories[0][index] == "Geometry":
            geometry.append(feat)
            geometryDesc.append(x_descriptions[0][index])
        elif x_categories[0][index] == "Correlation":
            correlation.append(feat)
            correlationDesc.append(x_descriptions[0][index])
        elif x_categories[0][index] == "Transformation":
            transformation.append(feat)
            transformationDesc.append(x_descriptions[0][index])
        elif x_categories[0][index] == "Trend":
            trend.append(feat)
            trendDesc.append(x_descriptions[0][index])

    geometryT, correlationT, transformationT, trendT = [], [], [], []
    for index, feat in enumerate(t_Xtest):
        if x_categories[0][index] == "Geometry":
            geometryT.append(feat)
        elif x_categories[0][index] == "Correlation":
            correlationT.append(feat)
        elif x_categories[0][index] == "Transformation":
            transformationT.append(feat)
        elif x_categories[0][index] == "Trend":
            trendT.append(feat)

    mean_features = []
    for feat in t_Xtest:
        mean_features.append(np.mean(feat, axis=0))

    geometry = np.array(geometry)
    correlation = np.array(correlation)
    transformation = np.array(transformation)
    trend = np.array(trend)
    geometryT = np.array(geometryT)
    correlationT = np.array(correlationT)
    transformationT = np.array(transformationT)
    trendT = np.array(trendT)
    mean_features = np.array(mean_features)

    print("\n\t\t\tSHAP_BUILD geometry:", geometry.shape)
    print("\n\t\t\tSHAP_BUILD geometryT:", geometryT.shape)
    print("\n\t\t\tSHAP_BUILD transformation:", transformation.shape)
    print("\n\t\t\tSHAP_BUILD transformationT:", transformationT.shape)
    print("\n\t\t\tSHAP_BUILD correlation:", correlation.shape)
    print("\n\t\t\tSHAP_BUILD correlationT:", correlationT.shape)
    print("\n\t\t\tSHAP_BUILD trend':", trend.shape)
    print("\n\t\t\tSHAP_BUILD trendT:", trendT.shape)
    print("\n\t\t\tSHAP_BUILD mean_features:", mean_features.shape)

    shap.summary_plot(np.array(geometry).T, np.array(geometryT).T, plot_size=(20, 10), feature_names=geometryDesc)
    alpha = "parameterizer_frontend/src/assets_naterq/" + file + "_" + algorithm + "_shap_geometry_plot.png"
    plt.title("SHAP details of geometry")
    plt.savefig(alpha)
    plt.close()

    shap.summary_plot(np.array(transformation).T, np.array(transformationT).T, plot_size=(20, 10), feature_names=transformationDesc)
    alpha = "parameterizer_frontend/src/assets_naterq/" + file + "_" + algorithm + "_shap_transformation_plot.png"
    plt.title("SHAP details of transformation")
    plt.savefig(alpha)
    plt.close()

    shap.summary_plot(np.array(correlation).T, np.array(correlationT).T, plot_size=(20, 10), feature_names=correlationDesc)
    alpha = "parameterizer_frontend/src/assets_naterq/" + file + "_" + algorithm + "_shap_correlation_plot.png"
    plt.title("SHAP details of correlation")
    plt.savefig(alpha)
    plt.close()

    shap.summary_plot(np.array(trend).T, np.array(trendT).T, plot_size=(20, 8), feature_names=trendDesc)
    alpha = "parameterizer_frontend/src/assets_naterq/" + file + "_" + algorithm + "_shap_trend_plot.png"
    plt.title("SHAP details of Trend")
    plt.savefig(alpha)
    plt.close()


    aggregation_features.append(np.mean(geometry, axis=0))
    aggregation_features.append(np.mean(correlation, axis=0))
    aggregation_features.append(np.mean(transformation, axis=0))
    aggregation_features.append(np.mean(trend, axis=0))

    aggregation_test.append(np.mean(geometryT, axis=0))
    aggregation_test.append(np.mean(correlationT, axis=0))
    aggregation_test.append(np.mean(transformationT, axis=0))
    aggregation_test.append(np.mean(trendT, axis=0))

    aggregation_features = np.array(aggregation_features).T
    aggregation_test = np.array(aggregation_test).T

    shap.summary_plot(aggregation_features, aggregation_test, feature_names=['Geometry', 'Correlation', 'Transformation', 'Trend'])
    alpha = "parameterizer_frontend/src/assets_naterq/" + file + "_" + algorithm + "_shap_aggregate_plot.png"
    plt.title("SHAP Aggregation Results")
    plt.gca().axes.get_xaxis().set_visible(False)

    plt.savefig(alpha)
    plt.close()

    # Aggregate shapely values per element of X_test
    total_weights = [np.abs(shval.T[i]).mean(0) for i in range(len(shval[0]))]

    # Convert to percentages
    total_sum = np.sum(total_weights)
    total_weights_percent = [(weight / total_sum * 100) for weight in total_weights]

    total_weights_for_all_algorithms = np.append(total_weights_for_all_algorithms, total_weights_percent)

    results_shap = convert_results(total_weights_for_all_algorithms, file, algorithm, x_descriptions, x_features, x_categories, mean_features)

    return results_shap



def shap_runner_naterq(dataset, algorithm, missing_values, scenario, selected_series, normalization, limitation, splitter, params, nbr_values=800):

    path, _ = views.get_file_paths(dataset)

    print("°°°°°SHAP >> NATERQ SEARCH DIR SELECTED:", path, "for ", dataset, "\n")
    print("°°°°°SHAP >> NATERQ params : missing_values (", missing_values, ") / scenario (", scenario,") / selected_series(", *selected_series,") / normalization (", normalization, ") / limitation (", limitation, ") with splitter (", splitter, ")\n")
    print("°°°°°SHAP >> NATERQ params : algo (", algorithm, ") / params (", *params, ")\n")

    if dataset == "bafu" and (limitation > 12 or splitter > 10):
        limitation = 12
        splitter = 9
        print("\n\t\t\t\t\t°°°°°SHAP >> SPLITTER AND LIMITATION REDUCED DUE TO LACKED OF DATA IN ", dataset, " >> (limitation = ", limitation, " and splitter = ", splitter, ")...\n")
    elif dataset == "climate" and (limitation > 10 or splitter > 7):
        limitation = 10
        splitter = 7
        print("\n\t\t\t\t\t°°°°°SHAP >> SPLITTER AND LIMITATION REDUCED DUE TO LACKED OF DATA IN ", dataset, " >> (limitation = ", limitation, " and splitter = ", splitter, ")...\n")

    ground_truth_matrixes, obfuscated_matrixes = [], []
    output_metrics, output_rmse, input_params, input_params_full = [], [], [], []

    for current_series in range(0, limitation):
        used_series = [str(current_series) + ":shap"]
        ground_truth_matrix, obfuscated_matrix = views.run_contamination(path, int(missing_values), scenario, used_series, normalization, limitation, nbr_values)
        ground_truth_matrixes.append(ground_truth_matrix)
        obfuscated_matrixes.append(obfuscated_matrix)

        if algorithm == "cdrec":
            _, imputation_results = views.cdrec_algo(ground_truth_matrix, obfuscated_matrix, params[0], params[1], params[2])
        elif algorithm == "stmvl":
            _, imputation_results = views.stmvl_algo(ground_truth_matrix, obfuscated_matrix, params[0], params[1], params[2])
        elif algorithm == "iim":
            _, imputation_results = views.iim_algo(ground_truth_matrix, obfuscated_matrix, params)
        elif algorithm == "mrnn":
            _, imputation_results = views.mrnn_algo(ground_truth_matrix, obfuscated_matrix, params[0], params[1], params[2], params[3])

        output_metrics.append(imputation_results)
        output_rmse.append(imputation_results[0])

        catch_fct, descriptions = catch.extract_features_naterq(np.array(obfuscated_matrix), False, CATEGORIES, FEATURES)

        extracted_features = np.array(list(catch_fct.values()))

        input_params.append(extracted_features)
        input_params_full.append(descriptions)

        print("°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°")
        print("\t\t°°°°°SHAP >> NATERQ Current series contamination : ", *used_series, " °°°°°°°°°°°°°°°°°°°°°°°°°°°°°")
        print("\t\t°°°°°SHAP >> NATERQ SHAPE TEST : ", np.array(ground_truth_matrix).shape)
        print("\t\t°°°°°SHAP >> NATERQ SHAPE TEST : ", np.array(obfuscated_matrix).shape)
        print("\t\t°°°°°SHAP >> NATERQ Current series ", current_series," contamination done")
        print("\t\t°°°°°SHAP >> NATERQ Current series ", current_series," imputation done")
        print("°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°")

    for read in output_metrics:
        print("°°°°°SHAP >> NATERQ RESULTS_: Metrics RMSE : ", read[0])

    shap_values = launch_shap_model(input_params, input_params_full, output_rmse, dataset, algorithm, splitter)

    print("°°°°°SHAP >> NATERQ SHAP COMPUTED AND ENDED SUCCESSFULLY ! °°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°\n\n\n")

    return ground_truth_matrixes, obfuscated_matrixes, output_metrics, input_params, shap_values


if __name__ == '__main__':
    print("\n\n°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°\n°°°°°SHAP RUNNER\n")