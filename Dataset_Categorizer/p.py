import json

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


def shap_tester(dataset_path: str, obfuscated_dataset_path: str, dataset: str):
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

    print("\t\t\tNATERQ obfuscated_matrix Shape: ", obfuscated_matrix.shape)
    for o in obfuscated_matrix :
        print("\t\t\tNATERQ o Shape: ", o.shape)
        print("\t\t\tNATERQ o : ", o)
        print("\t\t\tNATERQ o : 166 is the number of time series")
        break
    print("=======================================\n\n")

    print("\t\t\tNATERQ ground_truth_matrix Shape: ", ground_truth_matrix.shape)
    for g in ground_truth_matrix :
        print("\t\t\tNATERQ g Shape: ", g.shape)
        print("\t\t\tNATERQ g : ", g)
        break
    print("=======================================\n\n")

    X_train = np.array(list(catch.extract_features(ground_truth_matrix, False).values()))

    # Sample X_test from X_train; could optionally remove those samples from X_train to avoid overfitting
    sample_indices = np.random.choice(X_train.shape[0], size=12, replace=False)  # Sample size of 3 is used as an example. Adjust as desired???
    X_test = X_train[sample_indices]
    total_weights_for_all_algorithms = []

    print("\t\t", len(X_test))

    print("\t\tNbr Algo : ", len(ALGORITHMS))

    for algorithm in ALGORITHMS:

        print("####################", algorithm, "####################")

        config = load_config("../Optimizer/results/best_params_algorithm.json", algorithm, dataset)

        # Assuming evaluate_params provides RMSE as per its signature.
        my_rmse = Optimizer.evaluate_params.evaluate_params(ground_truth_matrix, obfuscated_matrix, algorithm, config, selected_metrics=["rmse"])

        print("\n\t\tmy_rmse****** : ", my_rmse)

        y_train = np.array(my_rmse["rmse"])
        #y_train = X_train

        # X_train = np.delete(X_train, sample_indices, axis=0)
        # y_train = np.delete(y_train, sample_indices, axis=0)

        print("\n\t\tX_train SHAPE : ", X_train.shape)
        print("\n\t\tX_test SHAPE : ", X_test.shape)
        print("\n\t\tX_train : ", *X_train)
        print("\n\t\ty_train : ", y_train, "\n")

        # Train a random forest regressor
        model = RandomForestRegressor()
        model.fit(X_train.reshape(-1, 1), np.repeat(y_train, 22)) #np.repeat(y_train, 22))
        # or model.fit(X_train.reshape(1, -1), [y_train])

        # Use SHAP to explain the test set
        #exp = shap.KernelExplainer(model.predict, X_test.reshape(-1, 1))
        exp = shap.Explainer(model)
        shval = exp.shap_values(X_test.reshape(-1, 1))

        print("shval", *shval, "\n\n")

        shap.summary_plot(shval,
                         X_test.reshape(-1, 1),
                         #plot_type="beeswarm",
                         feature_names=["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5",
                                        "Feature 6", "Feature 7", "Feature 8", "Feature 9", "Feature 10",
                                        "Feature 11", "Feature 12"]
                         )
        # Adjust feature names as needed
        #shap.force_plot(exp.expected_value, shval)
        #shap.plots.beeswarm(shval)
        name = "shape_summary_"+algorithm+"_plot.png"
        plt.savefig(name)

        # Aggregate shapely values per element of X_test
        total_weights = [np.abs(shval.T[i]).mean(0) for i in range(len(shval[0]))]
        total_weights_for_all_algorithms = np.append(total_weights_for_all_algorithms, total_weights)

    return total_weights_for_all_algorithms


def myfunc(a):
    x = a[0]
    y = a[1]
    return x + y;
    #return x * x - y * y * y * y;

def alpha_test ():

    #X_train, X_test, y_train, y_test

    # features, or other "arguments" for the "function" SHAP is studying
    X_train = np.random.rand(200,2)

    # the output of the function
    y_train = np.array([myfunc(x) for x in X_train])

    # same as X_train, can be either subset of X_train or separate
    X_test = np.random.rand(101,2)

    # regression model can be used if the output is a numerical value and cannot be modeled as a standard sklearn classifier/regressor/etc
    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    # launch the explainer of the test set
    #exp = shap.Explainer(model, X_test)
    exp = shap.KernelExplainer(model.predict, X_test)
    # obtain shapely values from the same test set, preferably not too large
    shval = exp.shap_values(X_test)

    print(len(shval))
    print(len(shval[0]))

    #print(shval)

    # aggregate shapely values per element of X_test fed to exp.shap_values() into a single array with just one value per function argument (=feature)
    # use np.abs() to measure impact regardless of the numerical direction of the output (default)
    total_weights = [np.abs(shval.T[i]).mean(0) for i in range(0, len(shval[0]))]

    # SHAP output
    print(total_weights / max(total_weights))

    shap.summary_plot(shval,
                     X_test.reshape(-1, 1),
                     #plot_type="beeswarm",
                     feature_names=["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5",
                                    "Feature 6", "Feature 7", "Feature 8", "Feature 9", "Feature 10",
                                    "Feature 11", "Feature 12"]
                     )
    # Adjust feature names as needed
    #shap.force_plot(exp.expected_value, shval)
    #shap.plots.beeswarm(shval)
    name = "shape_"+algorithm+"_plot.png"
    plt.savefig(name)

    #total_weights = [shval.T[i].mean(0) for i in range(0, len(shval[0]))]

    # SHAP output
    #print(total_weights)


datasets = [
    # 'bafu',
    'chlorine',
    # 'climate',
    # 'drift',
    # 'meteo'
]

dataset_files = [
    # 'BAFU',
    'cl2fullLarge',
    # 'climate',
    # 'batch10',
    # 'meteo_total'
]

ALGORITHMS = ["cdrec",
              "iim",
              # "mrnn",
              "stmvl"
            ]


for dataset, data_file in zip(datasets, dataset_files):
    raw_file_path = f"../Datasets/{dataset}/raw_matrices/{data_file}_eighth.txt"
    obf_file_path = f"../Datasets/{dataset}/obfuscated/{data_file}_eighth_obfuscated_10.txt"

    if dataset == 'drift':
        raw_file_path = f"../Datasets/{dataset}/drift10/raw_matrices/{data_file}_eighth.txt"
        obf_file_path = f"../Datasets/{dataset}/obfuscated/{data_file}_eighth_obfuscated_10.txt"

    shap_values = shap_tester(raw_file_path, obf_file_path, dataset)

    print(dataset + ": ",  len(shap_values), " - ", str(shap_values))

    for i, algorithm in enumerate(ALGORITHMS):
        print()
