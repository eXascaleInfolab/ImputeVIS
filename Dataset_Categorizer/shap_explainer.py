import json
import math
from builtins import tuple

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
except ImportError as e:
    print(f"ImportError: {e}")
    print("Make sure the directory structure is correct and the module is accessible.")
    print("Updated Python path:", sys.path)
# Rest of your code



def load_config(json_path: str, algorithm: str, dataset_name: str) -> tuple:
    """
    Load the best_params for a given algorithm and dataset name from a JSON file.

    Parameters
    ----------
    json_path : str
        Path to the JSON file containing the parameters.
    algorithm : str
        The algorithm name. E.g., "cdrec".
    dataset_name : str
        The name of the dataset. E.g., "bafu", "chlorine".

    Returns
    -------
    tuple
        A tuple containing the best_params in order.
    """

    with open(json_path, 'r') as file:
        data = json.load(file)

    params_dict = data[algorithm][dataset_name]["best_params"]

    # Extract values dynamically from the params_dict and convert them into a tuple
    return tuple(params_dict.values())


def shap_tester(dataset_path: str, obfuscated_dataset_path: str, dataset: str, algorithmsList, featuresList, cross_validation:int):
    # Initialize a list to store results
    results = []

    # Call shap_tester_unity 10 times
    for i in range(cross_validation):
        result = shap_tester_unity(dataset_path, obfuscated_dataset_path, dataset, algorithmsList, featuresList)
        results.append(result)

    # Calculate average array
    average_array = [sum(x) / len(results) for x in zip(*results)]

    return average_array


def shap_tester_unity(dataset_path: str, obfuscated_dataset_path: str, dataset: str, algorithmsList, featuresList):
    """
    Test SHAP on a given dataset and algorithm.

    Parameters
    ----------
    dataset_path : str
        Path to the original dataset.
    obfuscated_dataset_path : str
        Path to the obfuscated dataset.
    dataset : str
        The name of the dataset. E.g., "bafu", "chlorine".

    Returns
    -------
    list
        A list of total weights which correspond to the importance of each feature.
    """

    # Load datasets
    obfuscated_matrix = np.loadtxt(obfuscated_dataset_path, delimiter=' ')
    ground_truth_matrix = np.loadtxt(dataset_path)

    #print("\t\t\tNATERQ obfuscated_matrix Shape: ", obfuscated_matrix.shape)
    #for o in obfuscated_matrix :
    #    print("\t\t\tNATERQ o Shape: ", o.shape)
    #    print("\t\t\tNATERQ o : ", o)
    #    print("\t\t\tNATERQ o : 166 is the number of time series")
    #    break
    #print("=======================================\n\n")

    #print("\t\t\tNATERQ ground_truth_matrix Shape: ", ground_truth_matrix.shape)
    #for g in ground_truth_matrix :
    #    print("\t\t\tNATERQ g Shape: ", g.shape)
    #    print("\t\t\tNATERQ g : ", g)
    #    break
    #print("=======================================\n\n")

    #print("=GET EACH SERIES==================================\n\n")
    t_obfuscated_matrix = obfuscated_matrix.T
    t_ground_truth_matrix = ground_truth_matrix.T

    #print("\t\t\tNATERQ TRANSPOSE obfuscated_matrix Shape: ", t_obfuscated_matrix.shape)
    #print("\t\t\tNATERQ TRANSPOSE ground_truth_matrix Shape: ", t_ground_truth_matrix.shape)
    #print("=======================================\n\n")

    #print("=GET EACH FEATURES BY SERIES==================================\n\n")
    X_train = []

    for current_series in ground_truth_matrix.T :
        X_train.append(np.array(list(catch.extract_features(current_series, False).values())))

    X_train = np.array(X_train)

    #print("\nX_train : ", X_train.shape)
    #for x in X_train:
    #    print("FEATURES : ", len(x), " = ", x)
    #    break
    #print("=======================================\n\n")

    #print("=PREPARE TEST SET==================================\n\n")
    # Sample X_test from X_train; could optionally remove those samples from X_train to avoid overfitting

    test_samples_limit = t_obfuscated_matrix.shape[0]//10

    if test_samples_limit < 3:
        test_samples_limit = 3

    #print("\ntest_samples_limit : ", test_samples_limit)

    sample_indices = np.random.choice(X_train.shape[0], size=test_samples_limit, replace=False)  # Sample size of 3 is used as an example. Adjust as desired???
    X_test = X_train[sample_indices]

    #print("\t\t", X_test.shape)
    #for x in X_test:
    #    print("TEST FEATURES : ", len(x), " = ", x)
    #    break

    X_train = np.delete(X_train, sample_indices, axis=0)
    #print("=======================================\n\n")

    total_weights_for_all_algorithms = []

    for algorithm in algorithmsList:
        #print("\n\n\t\t===== LOOP ALGO ##############", algorithm, "####################")

        #print("\t\t===== LOOP ALGO ### COMPUTE RMSE BY SERIES ==================================\n\n")
        config = load_config("../Optimizer/results/best_params_algorithm.json", algorithm, dataset)

        rmse_errors = []  # Assuming evaluate_params provides RMSE as per its signature.

        for i in range(0, t_ground_truth_matrix.shape[0]):
            #print("\t\t\t\t# INNER LOOP ALGO ", i, " ### COMPUTE RMSE BY SERIES ==================================")

            ground_truth_series, obfuscated_series = [], []

            ground_truth_series.append(t_ground_truth_matrix[i])
            obfuscated_series.append(t_obfuscated_matrix[i])

            obfuscated_series = np.array(obfuscated_series)
            ground_truth_series = np.array(ground_truth_series)

            #print("\t\t\t\t# INNER LOOP ALGO ### ground_truth_series :", ground_truth_series.shape)
            #print("\t\t\t\t# INNER LOOP ALGO ### obfuscated_series :", obfuscated_series.shape)

            rmse_errors.append(Optimizer.evaluate_params.evaluate_params(ground_truth_series,
                                                                        obfuscated_series,
                                                                        algorithm, config,
                                                                        selected_metrics=["rmse"]))

        rmse_errors = np.array(rmse_errors)

        #print("\n\t\trmse_errors  : ", rmse_errors.shape)
        #for e in rmse_errors:
        #    print("\n\t\trmse_errors  : ", e)
        #    break


        #print("\t\t===== LOOP ALGO ### SET LABEL TRAIN (RMSE) BY SERIES ==================================\n\n")

        y_train = []

        for e in rmse_errors:
            y_train.append(e["rmse"])
        y_train = np.array(y_train)

        #print("\n\t\ty_train  : ", y_train.shape)


        y_train = np.delete(y_train, sample_indices, axis=0)
        #print("\t\t=======================================\n\n")

        #print("\t\t===== LOOP ALGO ### COMPUTE THE REGRESSION MODEL ==================================\n\n")

        #print("\n\t\tX_train  : ", X_train.shape)
        #print("\n\t\tX_test  : ", X_test.shape)
        #print("\n\t\ty_train  : ", y_train.shape)

        # Train a random forest regressor
        model = RandomForestRegressor()
        model.fit(X_train, y_train) #np.repeat(y_train, 22))
        # or model.fit(X_train.reshape(1, -1), [y_train])
        #print("\t\t=======================================\n\n")

        #print("\t\t===== LOOP ALGO ### COMPUTE SHAP VALUES ==================================\n\n")
        # Use SHAP to explain the test set
        exp = shap.KernelExplainer(model.predict, X_test)
        #exp = shap.Explainer(model)
        shval = exp.shap_values(X_test)
        #shap_values = exp(X_test)

        #print("shval", *shval, "\n\n")
        #print("\t\t=======================================\n\n")



        #print("\t\t===== LOOP ALGO ### COMPUTE PLOTS ==================================\n\n")
        shap.summary_plot(shval, X_test, plot_size=(25, 10), feature_names=featuresList)
        alpha = "parameterizer_frontend/src/assets/"+dataset+"_"+algorithm+"_shap_plot.png"
        #alpha = "./figs/"+dataset+"_"+algorithm+"_shap_plot.png"
        plt.savefig(alpha)
        plt.close()


        t_shval = np.array(shval).T
        t_Xtest = np.array(X_test).T

        aggregation_features = []
        aggregation_test = []

        geometry = t_shval[:11]  # First 11 features
        correlation = t_shval[11:17]  # Next 6 features
        transformation = t_shval[17:19]  # Next 2 features
        trend = t_shval[19:]  # Last 3 features

        geometryT = t_Xtest[:11]  # First 11 features
        correlationT = t_Xtest[11:17]  # Next 6 features
        transformationT = t_Xtest[17:19]  # Next 2 features
        trendT = t_Xtest[19:]  # Last 3 features

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

        #print("aggregation feature : ", *aggregation_features)
        #print("aggregation feature : ", np.array(aggregation_features).shape, "\n\n")
        #print("X_test : ", np.array(X_test).shape, "\n\n")
        #print("aggregation_test : ", np.array(aggregation_test).shape, "\n\n")


        shap.summary_plot(aggregation_features, aggregation_test, feature_names=['Geometry', 'Correlation', 'Transformation', 'Trend'])


        alpha = "parameterizer_frontend/src/assets/"+dataset+"_"+algorithm+"_shap_aggregate_plot.png"
        #alpha = "./figs/"+dataset+"_"+algorithm+"_shap_aggregate_plot.png"
        plt.savefig(alpha)
        plt.close()


        #shap.plots.beeswarm(shap_values, plot_size=(25,10), order=shap_values.abs.max(0))
        #beta = "./figs/"+dataset+"_"+algorithm+"_shap_beeswarm_plot.png"
        #plt.savefig(beta)

        #shap.plots.bar(shap_values, max_display=12)
        #gamma = "./figs/"+dataset+"_"+algorithm+"_shap_bar_plot.png"
        #plt.savefig(gamma)

        #shap.plots.waterfall(shap_values[0])
        #delta = "./figs/"+dataset+"_"+algorithm+"_shap_waterfall_plot.png"
        #plt.savefig(delta)
        #print("\t\t=======================================\n\n")


        #print("\t\t# LOOP ALGO ### COMPUTE THE TOTAL WEIGHTS ==================================\n\n")
        # Aggregate shapely values per element of X_test
        total_weights = [np.abs(shval.T[i]).mean(0) for i in range(len(shval[0]))]

        # Convert to percentages
        total_sum = np.sum(total_weights)
        total_weights_percent = [(weight / total_sum) for weight in total_weights]

        total_weights_for_all_algorithms = np.append(total_weights_for_all_algorithms, total_weights_percent)

    return total_weights_for_all_algorithms



def shap_runner(datasets, dataset_files, algorithmsList):


    #datasets = [
    #    'bafu',
    #    'chlorine',
    #    'climate',
    #    #'drift',
    #    'meteo'
    #]

    #dataset_files = [
    #    'BAFU',
    #    'cl2fullLarge',
    #    'climate',
    #    #'batch10',
    #    'meteo_total'
    #]

    #algorithmsList = ["cdrec",
    #              "iim",
    #              #"mrnn",
    #              #"stmvl"
    #           ]

    featuresList = ["Longest stretch of above-mean values",
                "Longest stretch of decreasing values",
                "Transition matrix column variance",
                "Proportion of high incremental changes in the series",
                "5-bin histogram mode",
                "10-bin histogram mode",
                "Positive outlier timing",
                "Negative outlier timing",
                "Goodness of exponential fit to embedding distance distribution",
                "Detrended fluctuation analysis (low-scale scaling)",
                "Rescaled range fluctuation analysis (low-scale scaling)",
                "First 1/e crossing of the ACF",
                "First minimum of the ACF",
                "Time reversibility",
                "Histogram-based automutual information (lag 2, 5 bins)",
                "First minimum of the AMI function",
                "Change in autocorrelation timescale after incremental differencing",
                "Power in the lowest 20% of frequencies",
                "Centroid frequency",
                "Wang's periodicity metric",
                "Error of 3-point rolling mean forecast",
                "Entropy of successive pairs in symbolized series"]


    for dataset, data_file in zip(datasets, dataset_files):
        raw_file_path = f"../Datasets/{dataset}/raw_matrices/{data_file}_eighth.txt"
        obf_file_path = f"../Datasets/{dataset}/obfuscated/{data_file}_eighth_obfuscated_10.txt"

        if dataset == 'drift':
            raw_file_path = f"../Datasets/{dataset}/drift10/raw_matrices/{data_file}_eighth.txt"
            obf_file_path = f"../Datasets/{dataset}/obfuscated/{data_file}_eighth_obfuscated_10.txt"

        shap_values = shap_tester_unity(raw_file_path, obf_file_path, dataset, algorithmsList, featuresList)

        print(dataset + ": ",  len(shap_values), " - ", str(shap_values), "\n\n")

        result_display = []
        for x, sv in enumerate(shap_values):
            if x < 22 :
                result_display.append((x, algorithmsList[0], sv))
            elif 44 > x >= 22:
                result_display.append((x, algorithmsList[1], sv))
            else:
                result_display.append((x, algorithmsList[2], sv))


        result_display = sorted(result_display, key=lambda tup: (tup[1], tup[2]), reverse=True)

        result_shap = []

        inc = 0
        for (id, algo, value) in result_display:
            if math.isnan(value) == False:
                p = int(value*100)
            else:
                p = value
            m = id%22
            inc = inc + 1

            if p < 10:
                if m < 10:
                    print(dataset, " || ", algo, " >> ", p ,"%  of impact for feature (",m, ") : ", featuresList[m])
                else:
                    print(dataset, " || ", algo, " >> ", p ,"%  of impact for feature (",m,"): ", featuresList[m])
            else:
                if m < 10:
                    print(dataset, " || ", algo, " >> ", p, "% of impact for feature (", m, ") : ", featuresList[m])
                else:
                    print(dataset, " || ", algo, " >> ", p, "% of impact for feature (", m,"): ", featuresList[m])
            if inc%22 == 0:
                print("\n")

            result_shap.append([dataset, algo, p, m, featuresList[m]])

        return result_shap


#results = shap_runner(["chlorine"], ["cl2fullLarge"], ["cdrec"])