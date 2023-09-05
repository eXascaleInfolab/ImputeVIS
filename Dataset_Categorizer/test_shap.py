import numpy as np
import shap
import json
import catch
from sklearn.ensemble import RandomForestRegressor
import Optimizer.evaluate_params


def myfunc(a):
    return a[0] * a[0] - a[1] * a[1] * a[1] * a[1];


def myfunc2(a):
    return a + a * a;


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

def shap_tester(dataset_path: str, obfuscated_dataset_path: str, algorithm: str = "cdrec"):
    """
    Test SHAP on a given dataset and algorithm.

    Parameters
    ----------
    dataset_path : str
        Path to the original dataset.
    obfuscated_dataset_path : str
        Path to the obfuscated dataset.
    algorithm : str, optional
        The algorithm to use. Defaults to "cdrec".
        Valid values: "cdrec", "iim", "mrnn", "stmvl"

    Returns
    -------
    list
        A list of total weights which correspond to the importance of each feature.
    """

    # Load datasets
    obfuscated_matrix = np.loadtxt(obfuscated_dataset_path, delimiter=' ')
    ground_truth_matrix = np.loadtxt(dataset_path)
    X_train = np.array(list(catch.extract_features(ground_truth_matrix).values()))
        # .reshape(-1, 1)
    # Sample X_test from X_train, and then optionally remove those samples from X_train to avoid overfitting
    sample_indices = np.random.choice(X_train.shape[0], size=3,
                                      replace=False)  # Sample size of 10 is used as an example. Adjust as needed.
    X_test = X_train[sample_indices]

    # for algorithm in ALGORITHMS:
    config = load_config("../Optimizer/results/best_params_algorithm.json", algorithm, "bafu")

    # Assuming evaluate_params provides RMSE as per its signature.
    y_train = np.array(Optimizer.evaluate_params.evaluate_params(ground_truth_matrix, obfuscated_matrix, algorithm, config,
                                        selected_metrics=["rmse"])["rmse"])


    # X_train = np.delete(X_train, sample_indices, axis=0)
    # y_train = np.delete(y_train, sample_indices, axis=0)

    # Train a random forest regressor
    model = RandomForestRegressor()
    model.fit(X_train.reshape(-1, 1), np.repeat(y_train, 24))
    # or
    # model.fit(X_train.reshape(1, -1), [y_train])

    # Use SHAP to explain the test set
    exp = shap.KernelExplainer(model.predict, X_test.reshape(-1, 1))
    shval = exp.shap_values(X_test.reshape(-1, 1))

    # Aggregate shapely values per element of X_test
    total_weights = [np.abs(shval.T[i]).mean(0) for i in range(len(shval[0]))]
    # total_weights = np.mean(np.abs(shval[0]), axis=0)
    return total_weights


if __name__ == '__main__':
    # Test SHAP on a given dataset and algorithm
    total_weights = shap_tester("../Datasets/bafu/raw_matrices/BAFU_eighth.txt",
                                "../Datasets/bafu/obfuscated/BAFU_eighth_obfuscated_10.txt", algorithm="cdrec")
    print(total_weights)

# X_train, X_test, y_train, y_test

# features, or other "arguments" for the "function" SHAP is studying
# X_train = np.array(
#     list(catch.extract_features(np.array([[0.2, 0.5], [1, 0.5], [1.2, 1.5], [1.4, 1.0]])).values())).reshape(-1, 1)
#
# # the output of the function
# y_train = np.array([myfunc2(x) for x in X_train])
#
# # same as X_train, can be either subset of X_train or separate
# X_test = np.array([[0.3, 0.6], [1.1, 0.7], [1.3, 1.3]])
#
# # regression model can be used if the output is a numerical value and cannot be modeled as a standard sklearn classifier/regressor/etc
# model = RandomForestRegressor()
# model.fit(X_train, y_train)
#
# # launch the explainer of the test set
# exp = shap.KernelExplainer(model.predict, X_test)
# # obtain shapely values from the same test set, preferably not too large
# shval = exp.shap_values(X_test)
#
# print(len(shval))
# print(len(shval[0]))
#
# # aggregate shapely values per element of X_test fed to exp.shap_values() into a single array with just one value per function argument (=feature)
# # use np.abs() to measure impact regardless of the numerical direction of the output (default)
# total_weights = [np.abs(shval.T[i]).mean(0) for i in range(0, len(shval[0]))]
#
# # final SHAP output
# print(total_weights)
