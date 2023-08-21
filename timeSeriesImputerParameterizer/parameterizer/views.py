from typing import Tuple, Dict, Any

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import sys
import numpy as np

import Wrapper.algo_collection

sys.path.insert(0, os.path.abspath(".."))
from Utils_Thesis import utils, statistics
from Optimizer import bayesian_optimization, particle_swarm_optimization, successive_halving

import IIM.iim as iim_alg
import M_RNN.testerMRNN
import M_RNN.Data_Loader

import Dataset_Categorizer.catch as catch



@csrf_exempt
def cdrec(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)
        truncation_rank = data.get('truncation_rank', 10)  # Truncation rank used (0 = detect truncation automatically)
        epsilon = data.get('epsilon', 0.01)  # Threshold for difference during recovery
        if not isinstance(epsilon, str):
            epsilon = str(epsilon)
        iterations = data.get('iterations', 100)  # Maximum number of allowed iterations for the algorithm

        if clean_file_path is not None and obfuscated_file_path is not None:
            ground_truth_matrix = utils.load_and_trim_matrix(clean_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obfuscated_file_path)
            # Call the main function with parameters from the request
            imputed_matrix = Wrapper.algo_collection.native_cdrec_param(
                __py_matrix=obfuscated_matrix,
                __py_rank=int(truncation_rank),
                __py_eps=float("1" + epsilon),
                __py_iters=int(iterations)
            )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            corr = statistics.determine_correlation(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished CDRec! RMSE: ", rmse)
            # Check if normalization is required
            if data.get('normalization') == 'Normalized':
                imputed_matrix = statistics.zscore_normalization(imputed_matrix)
            return JsonResponse({'rmse': rmse, 'mae': mae, 'mi': mi, 'corr': corr,
                                 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()}
                                , status=200)
        else:
            print('No matching datasets found for path: ', data_set)

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def cdrec_optimization(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)
        if clean_file_path is not None and obfuscated_file_path is not None:
            raw_matrix = utils.load_and_trim_matrix(clean_file_path)
            obf_matrix = utils.load_and_trim_matrix(obfuscated_file_path)
            best_params, best_score = optimization(data, data_set, obf_matrix, raw_matrix)
            if best_params is not None and best_score is not None:
                best_params = {k: int(v) if isinstance(v, np.int64) else v for k, v in best_params.items()}
                return JsonResponse({'best_params': best_params, 'best_score': float(best_score)}, status=200)
            else:
                return JsonResponse({'message': 'Invalid request'}, status=400)


def optimization(data: Dict[str, Any], data_set: str, obf_matrix: np.ndarray, raw_matrix: np.ndarray) \
        -> Tuple[Dict[str, Any], float]:
    """
    Perform the optimization based on the given data and matrices.

    Parameters
    ----------
    data : dict
        A dictionary that contains the parameters for the optimization.
    data_set : str
        The data set used for the optimization.
    obf_matrix : np.ndarray
        The obfuscated matrix used for the optimization.
    raw_matrix : np.ndarray
        The raw matrix used for the optimization.

    Returns
    -------
    tuple
        A tuple of two elements:
        - A dictionary that contains the best parameters found in the optimization.
        - A float that represents the best score obtained in the optimization.
    """
    metrics = data.get('metrics', ['rmse', 'mae', 'mi', 'corr'])
    algo = data.get('algorithm', 'cdrec')
    if data.get('optimization') == 'bayesianOptimization':
        n_calls = data.get('n_calls', 10)
        n_random_starts = data.get('n_random_starts', 5)
        acq_func = data.get('acq_func', 'gp_hedge')
        best_params, best_score = bayesian_optimization.bayesian_optimization(
            ground_truth_matrix=raw_matrix,
            obfuscated_matrix=obf_matrix,
            selected_metrics=metrics,
            algorithm=algo,
            n_calls=n_calls,
            n_random_starts=n_random_starts,
            acq_func=acq_func)
        return best_params, best_score
    elif data.get('optimization') == 'particleSwarmOptimization':
        pso_params = {
            'c1': data.get('c1', 1.5),
            'c2': data.get('c2', 1.5),
            'w': data.get('w', 0.7),
            'n_particles': data.get('n_particles', 10)
        }
        best_params, best_score = particle_swarm_optimization.pso_optimization(
            ground_truth_matrix=raw_matrix,
            obfuscated_matrix=obf_matrix,
            selected_metrics=metrics,
            algorithm=algo,
            pso_params=pso_params)
        return best_params, best_score
    elif data.get('optimization') == 'successiveHalving':
        num_configs = data.get('num_configs', 10)
        num_iterations = data.get('num_iterations', 5)
        reduction_factor = data.get('reduction_factor', 2)
        best_params, best_score = successive_halving.successive_halving(
            ground_truth_matrix=raw_matrix,
            obfuscated_matrix=obf_matrix,
            selected_metrics=metrics,
            algorithm=algo,
            num_configs=num_configs,
            num_iterations=num_iterations,
            reduction_factor=reduction_factor)
        return best_params, best_score
    else:
        print('No matching optimization found for path: ', data_set)
        return None, None


@csrf_exempt
def iim(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)

        # Call the main function with parameters from the request
        alg_code = data.get('alg_code', 'iim 2')

        if clean_file_path is not None and obfuscated_file_path is not None:
            imputed_matrix = iim_alg.main(alg_code, obfuscated_file_path)
            ground_truth_matrix = utils.load_and_trim_matrix(clean_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obfuscated_file_path)
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            corr = statistics.determine_correlation(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished IIM! RMSE: ", rmse)
            # Check if normalization is required
            if data.get('normalization') == 'Normalized':
                imputed_matrix = statistics.zscore_normalization(imputed_matrix)
            return JsonResponse({'rmse': rmse, 'mae': mae, 'mi': mi, 'corr': corr,
                                 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()},
                                status=200)
        else:
            print('No matching datasets found for path: ', data_set)

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def iim_optimization(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)

        if clean_file_path is not None and obfuscated_file_path is not None:
            raw_matrix = utils.load_and_trim_matrix(clean_file_path)
            obf_matrix = utils.load_and_trim_matrix(obfuscated_file_path)
            best_params, best_score = optimization(data, data_set, obf_matrix, raw_matrix)
            if best_params is not None and best_score is not None:
                best_params = {k: int(v) if isinstance(v, np.int64) else v for k, v in best_params.items()}
                return JsonResponse({'best_params': best_params, 'best_score': float(best_score)}, status=200)
            else:
                return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def mrnn(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)
        hidden_dim = data.get('hidden_dim', 10)
        learning_rate = data.get('learning_rate', 0.01)
        iterations = data.get('iterations', 100)
        keep_prob = data.get('keep_prob', 1.0)
        # seq_len = data.get('seq_len', 7)

        # filename_input = data.get('filename_input', '../Datasets/bafu/raw_matrices/BAFU_small_with_NaN.txt')
        # filename_output = data.get('filename_output', '../Results/')
        # runtime = data.get('runtime', 0)

        if clean_file_path is not None and obfuscated_file_path is not None:
            ground_truth_matrix = utils.load_and_trim_matrix(clean_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obfuscated_file_path)
            # Call the main function with parameters from the request
            imputed_matrix = M_RNN.testerMRNN.mrnn_recov_with_data(obfuscated_matrix,
                                                                   runtime=-1,
                                                                   hidden_dim=hidden_dim,
                                                                   learning_rate=learning_rate,
                                                                   iterations=iterations,
                                                                   keep_prob=keep_prob,
                                                                   # seq_length=seq_len,
                                                                   )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            corr = statistics.determine_correlation(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished M-RNN! RMSE: ", rmse)
            # Check if normalization is required
            if data.get('normalization') == 'Normalized':
                imputed_matrix = statistics.zscore_normalization(imputed_matrix)
            return JsonResponse({'rmse': rmse, 'mae': mae, 'mi': mi, 'corr': corr,
                                 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()},
                                status=200)
        else:
            print('No matching datasets found for path: ', data_set)

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def mrnn_optimization(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)

        if clean_file_path is not None and obfuscated_file_path is not None:
            raw_matrix = utils.load_and_trim_matrix(clean_file_path)
            obf_matrix = utils.load_and_trim_matrix(obfuscated_file_path)
            best_params, best_score = optimization(data, data_set, obf_matrix, raw_matrix)
            if best_params is not None and best_score is not None:
                best_params = {k: int(v) if isinstance(v, np.int64) else v for k, v in best_params.items()}
                return JsonResponse({'best_params': best_params, 'best_score': float(best_score)}, status=200)
            else:
                return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def stmvl(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)
        window_size = data.get('window_size', 10)  # window size for temporal component
        gamma = data.get('gamma', 0.01)  # smoothing parameter for temporal weight
        alpha = data.get('alpha', 100)  # power for spatial weight

        if clean_file_path is not None and obfuscated_file_path is not None:
            ground_truth_matrix = utils.load_and_trim_matrix(clean_file_path)
            obfuscated_matrix = utils.load_and_trim_matrix(obfuscated_file_path)
            # Call the main function with parameters from the request
            imputed_matrix = Wrapper.algo_collection.native_stmvl_param(
                __py_matrix=obfuscated_matrix,
                __py_window=int(window_size),
                __py_gamma=float(gamma),
                __py_alpha=int(alpha)
            )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            corr = statistics.determine_correlation(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished STMVL! RMSE: ", rmse)
            # Check if normalization is required
            if data.get('normalization') == 'Normalized':
                imputed_matrix = statistics.zscore_normalization(imputed_matrix)
            return JsonResponse({'rmse': rmse, 'mae': mae, 'mi': mi, 'corr': corr,
                                 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()}
                                , status=200)
        else:
            print('No matching datasets found for path: ', data_set)

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def stmvl_optimization(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)
        if clean_file_path is not None and obfuscated_file_path is not None:
            raw_matrix = utils.load_and_trim_matrix(clean_file_path)
            obf_matrix = np.loadtxt(obfuscated_file_path, delimiter=" ", )
            best_params, best_score = optimization(data, data_set, obf_matrix, raw_matrix)
            if best_params is not None and best_score is not None:
                best_params = {k: int(v) if isinstance(v, np.int64) else v for k, v in best_params.items()}
                return JsonResponse({'best_params': best_params, 'best_score': float(best_score)}, status=200)
            else:
                return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def fetch_data(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)

        matrix_to_return = None

        if obfuscated_file_path is not None:
            obfuscated_matrix = utils.load_and_trim_matrix(obfuscated_file_path)
            matrix_to_return = obfuscated_matrix
        elif clean_file_path is not None:
            ground_truth_matrix = utils.load_and_trim_matrix(clean_file_path)
            matrix_to_return = ground_truth_matrix

        if matrix_to_return is not None:
            # Check if normalization is required
            if data.get('normalization') == 'Normalized':
                matrix_to_return = statistics.zscore_normalization(matrix_to_return)

            # Transpose the matrix and convert to a list
            transposed_list = np.transpose(matrix_to_return).tolist()

            # Replace NaN values with None in the list
            for i in range(len(transposed_list)):
                for j in range(len(transposed_list[i])):
                    if np.isnan(transposed_list[i][j]):
                        transposed_list[i][j] = None

            return JsonResponse({'matrix': transposed_list}, status=200)

    return JsonResponse({'message': 'Invalid request'}, status=400)


def handle_data_set(data_set: str) -> str:
    """
    Determines the abbreviation based on the provided data set string.

    Parameters
    ----------
    data_set : str
        The string identifier for the data series.

    Returns
    -------
    str
        The abbreviation corresponding to the data_set value.
    """

    if data_set.lower().startswith("bafu"):
        return "bafu"
    elif data_set.lower().startswith("cl2fullLarge"):
        return "chlorine"
    elif data_set.lower().startswith("climate"):
        return "climate"
    elif data_set.lower().startswith("batch10"):
        return "drift"
    elif data_set.lower().startswith("meteo"):
        return "meteo"
    else:
        return ""


# Then, in your `fetch_params` function, you can use:
# data_abbreviation = handle_data_set(data_set)


@csrf_exempt
def fetch_params(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        data_abbreviation = handle_data_set(data_set)

        if not data_abbreviation:
            return JsonResponse({'message': 'Invalid request'}, status=400)

        optimization_method = data.get("param_options")

        if not optimization_method:
            return JsonResponse({'message': 'param_options not provided'}, status=400)

        optimizer_dir = '../Optimizer'

        # If "recommended" is selected, check all optimization methods, otherwise stick with the provided one
        optimization_methods = [f.split('_')[-1].split('.json')[0] for f in os.listdir(optimizer_dir) if
                                f.startswith("optimization_results_") and f.endswith(
                                    ".json")] if optimization_method == "recommended" else [optimization_method]

        best_scores = {}  # this will keep track of the best score for each algo
        results = {}

        for method in optimization_methods:
            # file_pattern = f"optimization_results_{{algo_code}}_{method}.json"
            all_files = os.listdir(optimizer_dir)
            if optimization_method != "recommended":
                matching_files = [f for f in all_files if
                                  f.startswith("optimization_results_")
                                  and f.endswith(f".json")
                                  ]
            else:
                matching_files = [f for f in all_files if
                                  f.startswith("optimization_results_")
                                  and f.endswith(f"_{method}.json")
                                  ]

            for file in matching_files:
                algo_code = file.split('_')[2]
                with open(os.path.join(optimizer_dir, file), 'r') as json_file:
                    file_content = json_file.read()

                    # Check if the file is empty
                    if not file_content.strip():
                        print(f"File {file} is empty.")
                        continue

                    # print(f"Content of {file}:")
                    # print(file_content)

                    try:
                        data = json.loads(file_content)
                        # TODO Fix key error for best_score
                        if algo_code not in best_scores or data[data_abbreviation]['best_score'] < best_scores[algo_code]['best_score']:
                            best_scores[algo_code] = data[data_abbreviation]
                            results[algo_code] = data

                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file}: {e}")
                        print(f"Error position: {e.pos}")

        return JsonResponse({'params': results}, status=200)

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def categorize_data(request):
    if request.method == 'POST':
        _, data_set = load_from_request(request)
        clean_file_path, _ = get_file_paths(data_set)
        if clean_file_path is not None:
            ground_truth_matrix = utils.load_and_trim_matrix(clean_file_path)
            extracted_features = catch.extract_features(ground_truth_matrix, True)
            return JsonResponse(extracted_features, status=200)
    return JsonResponse({'message': 'Invalid request'}, status=400)


def load_from_request(request: WSGIRequest) -> Tuple[Dict[str, Any], str]:
    """
    Load data and data set from HTTP request body.

    Parameters
    ----------
    request : WSGIRequest
        An HTTP request object.

    Returns
    -------
    tuple
        A tuple of two elements:
        - A dictionary that contains the data loaded from the request body.
        - A string that represents the data set.
    """
    data = json.loads(request.body)
    print(f"Received data: {data}")
    data_set = data.get('data_set')
    print(f"Received dataset: {data_set}")
    return data, data_set


def get_file_paths(search_string: str = 'BAFU_small') -> Tuple[str, str]:
    """
    Get the file paths of the clean and obfuscated files.

    Parameters
    ----------
    search_string : str, optional
        The search string to find the files. The default is 'BAFU_small'.

    Returns
    -------
    tuple
        A tuple of two strings that represent the file paths of the clean and obfuscated files, respectively.
    """
    folder_path = '../Datasets'
    clean_file_path = utils.find_non_obfuscated_file(folder_path, search_string.split('_obfuscate')[0])
    print(f'Found clean file at: {clean_file_path}')
    obfuscated_file_path = utils.find_obfuscated_file(folder_path, search_string)
    print(f'Found obfuscated file at: {obfuscated_file_path}')
    return clean_file_path, obfuscated_file_path
