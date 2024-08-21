from typing import Tuple, Dict, Any

import pandas
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import sys
import numpy as np

import Wrapper.algo_collection
from Dataset_Categorizer.shap_explainer import shap_runner
from Dataset_Categorizer.shap_explainer_naterq import shap_runner_naterq

sys.path.insert(0, os.path.abspath(".."))
from Utils_Thesis import utils, statistics
from Contamination import contamination_naterq

from Optimizer import bayesian_optimization, particle_swarm_optimization, successive_halving

import IIM.iim as iim_alg
import M_RNN.testerMRNN
import M_RNN.Data_Loader

import Dataset_Categorizer.catch as catch


def run_contamination(path, missing_rate, pattern, selected_series, normalization, limit_series=5, limit_values=800):

    print("=CONTAMINATION=========================================================================================")
    obfuscated_matrix, ground_truth_matrix = None, None
    display = False

    if str(missing_rate) == '0':
        display = True

    selection_ids = []
    for s in selected_series:
        my_ids, _ = s.split(':')

        if str(my_ids) == "-2":     # select all series within the limit
            for i in range(0, limit_series):
                selection_ids.append(int(i))
            print(">> #CONTAMINATION NATERQ ALL SERIES (", limit_series,") selected with ", *selection_ids, "\n")
            break
        elif str(my_ids) == "-3":     # select all series within the limit
            for i in range(0, limit_series-2):
                selection_ids.append(int(i))
            print(">> #CONTAMINATION NATERQ ALL SERIES (", limit_series,") selected with ", *selection_ids, "\n")
            break

        selection_ids.append(int(my_ids))

    missing_rate = float(missing_rate) / 100

    print(">> #CONTAMINATION NATERQ  path: ", path, "\n")
    print(">> #CONTAMINATION NATERQ  display: ", display, "\n")
    print(">> #CONTAMINATION NATERQ  scenario: ", pattern, "\n")
    print(">> #CONTAMINATION NATERQ  normalization: ", normalization, "\n")
    print(">> #CONTAMINATION NATERQ  missing_rate: ", missing_rate, "\n")
    print(">> #CONTAMINATION NATERQ  selection_ids: ", *selection_ids, "\n")

    if path is not None:
        ground_truth_matrix = contamination_naterq.load_timeseries_trim(path, limit_series, limit_values)

        if not display:
            if pattern == "mcar":
                _, obfuscated_matrix = contamination_naterq.introduce_mcar(ground_truth_matrix, missing_rate, selection_ids, True)
            elif pattern == "blackout":
                _, obfuscated_matrix = contamination_naterq.introduce_blackout(ground_truth_matrix, missing_rate, selection_ids, True)
            elif pattern == "overlap":
                _, obfuscated_matrix = contamination_naterq.introduce_overlap(ground_truth_matrix, missing_rate, selection_ids, 0.05, True)
            elif pattern == "disjoint":
                _, obfuscated_matrix = contamination_naterq.introduce_disjoint(ground_truth_matrix, missing_rate, selection_ids, True)

            obfuscated_matrix = process_matrix(obfuscated_matrix, normalization)

    ground_truth_matrix = np.array(ground_truth_matrix)
    ground_truth_matrix = process_matrix(ground_truth_matrix, normalization)

    if display:
        obfuscated_matrix = ground_truth_matrix

    print(">> #CONTAMINATION NATERQ DONE SUCCESSFULLY !")
    print("=CONTAMINATION=========================================================================================\n")

    return ground_truth_matrix, obfuscated_matrix



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
    print(">> #OPTIMIAZATION NATERQ  LOGS START\n")

    metrics = data.get('metrics', ['rmse', 'mae', 'mi', 'corr'])
    algo = data.get('algorithm', 'cdrec')
    optimizer = str(data.get('optimization'))

    print(">> #OPTIMIAZATION NATERQ  metrics : ", *metrics, "\n")
    print(">> #OPTIMIAZATION NATERQ  algo : ", algo, "\n")
    print(">> #OPTIMIAZATION NATERQ  optimizer : ", optimizer, "\n")


    if optimizer == 'bayesianOptimization':
        n_calls = data.get('n_calls', 10)
        n_random_starts = data.get('n_random_starts', 5)
        acq_func = data.get('acq_func', 'gp_hedge')

        print(">> #OPTIMIAZATION NATERQ  bayesianOptimization/n_calls(",n_calls,")/n_random_starts(",n_random_starts,")/acq_func(",acq_func,")\n")

        best_params, best_score = bayesian_optimization.bayesian_optimization(
            ground_truth_matrix=raw_matrix,
            obfuscated_matrix=obf_matrix,
            selected_metrics=metrics,
            algorithm=algo,
            n_calls=n_calls,
            n_random_starts=n_random_starts,
            acq_func=acq_func)

        print("\n\n\n\n\n\n>> #OPTIMIAZATION NATERQ best_params", best_params)
        print(">> #OPTIMIAZATION NATERQ  best_score", best_score, "\n\n\n\n\n\n")

        return best_params, best_score

    elif optimizer == 'particleSwarmOptimization':
        print(">> #OPTIMIAZATION NATERQ  particleSwarmOptimization \n")

        pso_params = {
            'c1': data.get('c1', 1.5),
            'c2': data.get('c2', 1.5),
            'w': data.get('w', 0.7),
            'n_particles': data.get('n_particles', 10)
        }

        print(">> #OPTIMIAZATION NATERQ  particleSwarmOptimization/pso_params(",*pso_params,")\n")

        best_params, best_score = particle_swarm_optimization.pso_optimization(
            ground_truth_matrix=raw_matrix,
            obfuscated_matrix=obf_matrix,
            selected_metrics=metrics,
            algorithm=algo,
            pso_params=pso_params)

        print("\n\n\n\n\n\n>> #OPTIMIAZATION NATERQ best_params", best_params)
        print(">> #OPTIMIAZATION NATERQ  best_score", best_score, "\n\n\n\n\n\n")

        return best_params, best_score

    elif optimizer == 'successiveHalving':
        print(">> #OPTIMIAZATION NATERQ  successiveHalving \n")

        num_configs = data.get('num_configs', 10)
        num_iterations = data.get('num_iterations', 5)
        reduction_factor = data.get('reduction_factor', 2)

        print(">> #OPTIMIAZATION NATERQ  successiveHalving/num_configs(",num_configs,")/num_iterations(",num_iterations,")/reduction_factor(",reduction_factor,")\n")

        best_params, best_score = successive_halving.successive_halving(
            ground_truth_matrix=raw_matrix,
            obfuscated_matrix=obf_matrix,
            selected_metrics=metrics,
            algorithm=algo,
            num_configs=num_configs,
            num_iterations=num_iterations,
            reduction_factor=reduction_factor)

        print("\n\n\n\n\n\n>> #OPTIMIAZATION NATERQ best_params", best_params)
        print(">> #OPTIMIAZATION NATERQ  best_score", best_score, "\n\n\n\n\n\n")

        return best_params, best_score

    else:
        print('No matching optimization found for path: ', data_set)
        return None, None



def convert_matrix(ground_truth_matrix, obfuscated_matrix):
    obfuscated_matrix = np.array(obfuscated_matrix)
    ground_truth_matrix = np.array(ground_truth_matrix)
    obfuscated_matrix = pandas.DataFrame(obfuscated_matrix).apply(pandas.to_numeric, errors='coerce').values

    return ground_truth_matrix, obfuscated_matrix


def metric_generator(ground_truth_matrix, imputed_matrix, obfuscated_matrix):

    rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
    mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
    mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
    corr = statistics.determine_correlation(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)

    return [rmse, mae, mi, corr]


def cdrec_algo(ground_truth_matrix, obfuscated_matrix, truncation_rank, epsilon, iterations):

    print("CDREC COMPUTATION >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    ground_truth_matrix, obfuscated_matrix = convert_matrix(ground_truth_matrix, obfuscated_matrix)

    imputed_matrix = Wrapper.algo_collection.native_cdrec_param(__py_matrix=obfuscated_matrix,
                                                                __py_rank=int(truncation_rank),
                                                                __py_eps=float("1" + epsilon),
                                                                __py_iters=int(iterations))

    metrics = metric_generator(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

    print(">> #CDREC NATERQ  FINISHED CDRec! RMSE ", metrics[0], "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    return imputed_matrix, metrics


@csrf_exempt
def cdrec(request):

    print(">> #CDREC NATERQ  LOGS START\n")

    if request.method == 'POST':
        data, data_set = load_from_request(request)

        print(">> #CDREC NATERQ  data: ", data, "\n")

        clean_file_path, obfuscated_file_path = get_file_paths(data.get('dataset'))

        truncation_rank = data.get('truncation_rank', 10)  # Truncation rank used (0 = detect truncation automatically)
        epsilon = data.get('epsilon', 0.01)  # Threshold for difference during recovery
        if not isinstance(epsilon, str):
            epsilon = str(epsilon)
        iterations = data.get('iterations', 100)  # Maximum number of allowed iterations for the algorithm

        print(">> #CDREC NATERQ  truncation_rank: ", truncation_rank, "\n")
        print(">> #CDREC NATERQ  epsilon: ", epsilon, "\n")
        print(">> #CDREC NATERQ  iterations: ", iterations, "\n")

        ground_truth_matrix, obfuscated_matrix = run_contamination(clean_file_path,
                                               int(data.get('missing_rate')),
                                               data.get('scenario'),
                                               data.get('selected_series'),
                                               data.get('normalization'))

        imputed_matrix, metrics = cdrec_algo(ground_truth_matrix, obfuscated_matrix, truncation_rank, epsilon, iterations)

        return JsonResponse({'rmse': metrics[0], 'mae': metrics[1], 'mi': metrics[2], 'corr': metrics[3],
                             'matrix_imputed': np.asarray(imputed_matrix).tolist()}
                            , status=200)
    else:
        print('No matching datasets found for path')

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def cdrec_optimization(request):

    print(">> #OPTI_CDREC NATERQ - CDREC OPTIMIZATION ###\n")

    if request.method == 'POST':

        data, data_set = load_from_request(request)
        clean_file_path, _ = get_file_paths(data.get('dataset'))

        print(">> #OPTI_CDREC NATERQ - CDREC clean_file_path ### ", clean_file_path, "\n")

        if clean_file_path is not None :

            ground_truth_matrix, obfuscated_matrix = run_contamination(clean_file_path,
                                                                       int(data.get('missing_rate')),
                                                                       data.get('scenario'),
                                                                       data.get('selected_series'),
                                                                       data.get('normalization'))

            ground_truth_matrix, obfuscated_matrix = convert_matrix(ground_truth_matrix, obfuscated_matrix)

            best_params, best_score = optimization(data, data_set, np.array(obfuscated_matrix), np.array(ground_truth_matrix))

            if best_params is not None and best_score is not None:
                best_params = {k: int(v) if isinstance(v, np.int64) else v for k, v in best_params.items()}
                return JsonResponse({'best_params': best_params, 'best_score': float(best_score)}, status=200)
            else:
                return JsonResponse({'message': 'Invalid request'}, status=400)



def stmvl_algo(ground_truth_matrix, obfuscated_matrix, window_size, gamma, alpha):

    print("STMVL COMPUTATION >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    ground_truth_matrix, obfuscated_matrix = convert_matrix(ground_truth_matrix, obfuscated_matrix)

    imputed_matrix = Wrapper.algo_collection.native_stmvl_param(
        __py_matrix=obfuscated_matrix,
        __py_window=int(window_size),
        __py_gamma=float(gamma),
        __py_alpha=int(alpha)
    )

    metrics = metric_generator(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

    print(">> #STMVL NATERQ  FINISHED STMVL! RMSE ", metrics[0], "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    return imputed_matrix, metrics

@csrf_exempt
def stmvl(request):

    print(">> #STMVL NATERQ  LOGS START\n")

    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data.get('dataset'))

        window_size = data.get('window_size', 10)  # window size for temporal component
        gamma = data.get('gamma', 0.01)  # smoothing parameter for temporal weight
        alpha = data.get('alpha', 100)  # power for spatial weight

        ground_truth_matrix, obfuscated_matrix = run_contamination(clean_file_path,
                                                                   int(data.get('missing_rate')),
                                                                   data.get('scenario'),
                                                                   data.get('selected_series'),
                                                                   data.get('normalization'))

        imputed_matrix, metrics = stmvl_algo(ground_truth_matrix, obfuscated_matrix, window_size, gamma, alpha)

        return JsonResponse({'rmse': metrics[0], 'mae': metrics[1], 'mi': metrics[2], 'corr': metrics[3],
                             'matrix_imputed': np.asarray(imputed_matrix).tolist()}
                            , status=200)
    else:
        print('No matching datasets found for path')

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def stmvl_optimization(request):

    print(">> #OPTI_STMVL NATERQ  LOGS START\n")

    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, _ = get_file_paths(data.get('dataset'))

        print(">> #OPTI_STMVL NATERQ - CDREC clean_file_path ### ", clean_file_path, "\n")

        if clean_file_path is not None:

            ground_truth_matrix, obfuscated_matrix = run_contamination(clean_file_path,
                                                                       int(data.get('missing_rate')),
                                                                       data.get('scenario'),
                                                                       data.get('selected_series'),
                                                                       data.get('normalization'))

            ground_truth_matrix, obfuscated_matrix = convert_matrix(ground_truth_matrix, obfuscated_matrix)

            best_params, best_score = optimization(data, data_set, obfuscated_matrix, ground_truth_matrix)

            if best_params is not None and best_score is not None:
                best_params = {k: int(v) if isinstance(v, np.int64) else v for k, v in best_params.items()}
                return JsonResponse({'best_params': best_params, 'best_score': float(best_score)}, status=200)
            else:
                return JsonResponse({'message': 'Invalid request'}, status=400)


def iim_algo(ground_truth_matrix, obfuscated_matrix, alg_code):

    print("IIM COMPUTATION >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    ground_truth_matrix, obfuscated_matrix = convert_matrix(ground_truth_matrix, obfuscated_matrix)

    imputed_matrix = iim_alg.impute_with_algorithm(alg_code, obfuscated_matrix.copy())

    metrics = metric_generator(ground_truth_matrix, imputed_matrix, obfuscated_matrix)

    print(">> #IIM NATERQ  FINISHED IIM ! RMSE ", metrics[0], "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    return imputed_matrix, metrics


@csrf_exempt
def iim(request):

    print(">> #IIM NATERQ  LOGS START\n")

    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data.get('dataset'))

        # Call the main function with parameters from the request
        alg_code = data.get('alg_code', 'iim 2')

        ground_truth_matrix, obfuscated_matrix = run_contamination(clean_file_path,
                                                                   int(data.get('missing_rate')),
                                                                   data.get('scenario'),
                                                                   data.get('selected_series'),
                                                                   data.get('normalization'))

        imputed_matrix, metrics = iim_algo(ground_truth_matrix, obfuscated_matrix, alg_code)

        return JsonResponse({'rmse': metrics[0], 'mae': metrics[1], 'mi': metrics[2], 'corr': metrics[3],
                             'matrix_imputed': np.asarray(imputed_matrix).tolist()}
                            , status=200)

    else:
        print('No matching datasets found for path')

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def iim_optimization(request):

    print(">> #OPTI_IIM NATERQ  LOGS START\n")

    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, _ = get_file_paths(data.get('dataset'))

        print(">> #OPTI_IIM NATERQ - CDREC clean_file_path ### ", clean_file_path, "\n")

        if clean_file_path is not None:

            ground_truth_matrix, obfuscated_matrix = run_contamination(clean_file_path,
                                                                       int(data.get('missing_rate')),
                                                                       data.get('scenario'),
                                                                       data.get('selected_series'),
                                                                       data.get('normalization'))

            ground_truth_matrix, obfuscated_matrix = convert_matrix(ground_truth_matrix, obfuscated_matrix)

            best_params, best_score = optimization(data, data_set, obfuscated_matrix, ground_truth_matrix)

            if best_params is not None and best_score is not None:
                best_params = {k: int(v) if isinstance(v, np.int64) else v for k, v in best_params.items()}
                return JsonResponse({'best_params': best_params, 'best_score': float(best_score)}, status=200)
            else:
                return JsonResponse({'message': 'Invalid request'}, status=400)


def mrnn_algo(ground_truth_matrix, obfuscated_matrix, hidden_dim, learning_rate, iterations, keep_prob):
    print("MRNN COMPUTATION >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    ground_truth_matrix, obfuscated_matrix = convert_matrix(ground_truth_matrix, obfuscated_matrix)

    print(">> #MRNN NATERQ  obfuscated_matrix: ", obfuscated_matrix, "\n")
    print(">> #MRNN NATERQ  ground_truth_matrix: ", ground_truth_matrix, "\n")

    obfuscated_matrix = np.transpose(obfuscated_matrix).tolist()

    imputed_matrix = M_RNN.testerMRNN.mrnn_recov_with_data(obfuscated_matrix,
                                                           runtime=-1,
                                                           hidden_dim=hidden_dim,
                                                           learning_rate=learning_rate,
                                                           iterations=iterations,
                                                           keep_prob=keep_prob)

    ground_truth_matrix = np.array(ground_truth_matrix)
    obfuscated_matrix = np.transpose(np.array(obfuscated_matrix))

    metrics = metric_generator(ground_truth_matrix, np.asarray(imputed_matrix).transpose(), obfuscated_matrix)

    print(">> #MRNN NATERQ  FINISHED MRNN ! RMSE ", metrics[0], "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    return imputed_matrix, metrics


@csrf_exempt
def mrnn(request):
    print(">> #MRNN NATERQ  LOGS START\n")

    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data.get('dataset'))

        hidden_dim = data.get('hidden_dim', 10)
        learning_rate = data.get('learning_rate', 0.01)
        iterations = data.get('iterations', 100)
        keep_prob = data.get('keep_prob', 1.0)

        print(">> #MRNN NATERQ  data.get('dataset'): ", data.get('dataset'), "\n")
        print(">> #MRNN NATERQ  hidden_dim: ", hidden_dim, "\n")
        print(">> #MRNN NATERQ  learning_rate: ", learning_rate, "\n")
        print(">> #MRNN NATERQ  iterations: ", iterations, "\n")
        print(">> #MRNN NATERQ  keep_prob: ", keep_prob, "\n")

        ground_truth_matrix, obfuscated_matrix = run_contamination(clean_file_path,
                                                                   int(data.get('missing_rate')),
                                                                   data.get('scenario'),
                                                                   data.get('selected_series'),
                                                                   data.get('normalization'))

        imputed_matrix, metrics = mrnn_algo(ground_truth_matrix, obfuscated_matrix, hidden_dim, learning_rate, iterations, keep_prob)

        print(">> #MRNN NATERQ  FINISHED MRNN ! RMSE ", metrics[0], "\n")

        return JsonResponse({'rmse': metrics[0], 'mae': metrics[1], 'mi': metrics[2], 'corr': metrics[3],
                             'matrix_imputed': np.asarray(imputed_matrix).transpose().tolist()},
                            status=200)
    else:
        print('No matching datasets found for path')

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def mrnn_optimization(request):

    print(">> #OPTI_MRNN NATERQ  LOGS START\n")

    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, _ = get_file_paths(data.get('dataset'))

        print(">> #OPTI_MRNN NATERQ - CDREC clean_file_path ### ", clean_file_path, "\n")

        if clean_file_path is not None:

            ground_truth_matrix, obfuscated_matrix = run_contamination(clean_file_path,
                                                                       int(data.get('missing_rate')),
                                                                       data.get('scenario'),
                                                                       data.get('selected_series'),
                                                                       data.get('normalization'))

            ground_truth_matrix, obfuscated_matrix = convert_matrix(ground_truth_matrix, obfuscated_matrix)

            print(">> #MRNN NATERQ  obfuscated_matrix: ", obfuscated_matrix, "\n")
            print(">> #MRNN NATERQ  ground_truth_matrix: ", ground_truth_matrix, "\n")

            ground_truth_matrix = np.transpose(np.array(ground_truth_matrix))
            obfuscated_matrix = np.transpose(obfuscated_matrix).tolist()

            best_params, best_score = optimization(data, data_set, obfuscated_matrix, ground_truth_matrix)

            if best_params is not None and best_score is not None:
                best_params = {k: int(v) if isinstance(v, np.int64) else v for k, v in best_params.items()}
                return JsonResponse({'best_params': best_params, 'best_score': float(best_score)}, status=200)
            else:
                return JsonResponse({'message': 'Invalid request'}, status=400)



@csrf_exempt
def fetch_data(request):
    if request.method == 'POST':

        print(">> #DATA_FETCH NATERQ NEW CONTAMINATION CALLED\n")

        data, data_set = load_from_request(request)

        print(">> #DATA_FETCH NATERQ LOGS : data - ", data, "\n")
        print(">> #DATA_FETCH NATERQ LOGS : data_set - ", data_set, "\n")

        clean_file_path, obfuscated_file_path = get_file_paths(data.get('dataset'))

        ground_truth_matrix, obfuscated_matrix = run_contamination(clean_file_path,
                                               int(data.get('missing_rate')),
                                               data.get('scenario'),
                                               data.get('selected_series'),
                                               data.get('normalization'))


        response_data = {}
        response_data['matrix'] = obfuscated_matrix
        response_data['groundtruth'] = ground_truth_matrix

        if response_data:
            return JsonResponse(response_data, status=200)
        else:
            # Handle case where neither matrix is available (you can change this to your desired error response)
            return JsonResponse({'error': 'No matrices found'}, status=400)


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
    elif data_set.lower().startswith("cl2fullLarge") or data_set.lower().startswith("chlorine"):
        return "chlorine"
    elif data_set.lower().startswith("climate"):
        return "climate"
    elif data_set.lower().startswith("batch") or data_set.lower().startswith("drift"):
        return "drift"
    elif data_set.lower().startswith("meteo"):
        return "meteo"
    else:
        return "climate"  # Default


# Then, in your `fetch_params` function, you can use:
# data_abbreviation = handle_data_set(data_set)


@csrf_exempt
def fetch_params(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        data_abbreviation = handle_data_set(data_set)

        print(">> #FETCH NATERQ  LOGS : data", data, "\n")
        print(">> #FETCH NATERQ  LOGS : data_abbreviation", data_abbreviation, "\n")

        optimal_metrics = "rmse_mae"  # Determined via thesis' experiments, holds for most cases

        if not data_abbreviation:
            return JsonResponse({'message': 'Invalid request'}, status=400)

        optimization_method = data.get("param_options")

        print(">> #FETCH NATERQ  LOGS : optimization_method", optimization_method, "\n")


        if not optimization_method:
            return JsonResponse({'message': 'param_options not provided'}, status=400)

        optimizer_dir = '../Optimizer/metric_specific'

        # If "recommended" is selected, check all optimization methods, otherwise stick with the provided one
        optimization_methods = [f.split('_')[-1].split('.json')[0] for f in os.listdir(optimizer_dir) if
                                f.startswith("optimization_results_") and f.endswith(
                                    ".json")] if optimization_method == "recommended" else [optimization_method]


        print(">> #FETCH NATERQ  LOGS : optimization_methods", optimization_methods, "\n")

        best_scores = {}  # this will keep track of the best score for each algo
        results = {}

        print(">> #FETCH NATERQ  LOGS : LOOPS\n")


        for method in optimization_methods:
            # file_pattern = f"optimization_results_{{algo_code}}_{method}.json"
            all_files = os.listdir(optimizer_dir)
            if optimization_method != "recommended":
                matching_files = [f for f in all_files if
                                  f.startswith("optimization_results_")
                                  and optimization_method in f
                                  and optimal_metrics in f
                                  ]
            else:
                matching_files = [f for f in all_files if
                                  f.startswith("optimization_results_")
                                  and "bayesian_optimization" in f
                                  and optimal_metrics in f
                                  ]

            for file in matching_files:
                algo_code = file.split('_')[2]
                with open(os.path.join(optimizer_dir, file), 'r') as json_file:
                    file_content = json_file.read()

                    # Check if the file is empty
                    if not file_content.strip():
                        print(f"File {file} is empty.")
                        continue


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
    print(f"#REQUEST Received data: {data}")
    data_set = data.get('data_set')
    print(f"#REQUEST Received dataset: {data_set}")
    return data, data_set


def get_file_paths(search_string: str = 'bafu') -> Tuple[str, str]:
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

    print("## NATERQ SEARCH:", search_string)

    if "drift" in search_string :
        folder_path = '../Datasets/drift/drift10_normal.txt'
    elif "bafu" in search_string:
        folder_path = '../Datasets/bafu/bafu_10_normal.txt'
    elif "chlorine" in search_string:
        folder_path = '../Datasets/chlorine/chlorine_normal.txt'
    elif "climate" in search_string:
        folder_path = '../Datasets/climate/climate_normal.txt'
    elif "meteo" in search_string:
        folder_path = '../Datasets/meteo/meteo_normal.txt'

    print("## NATERQ SEARCH DIR SELECTED:", folder_path)


    return folder_path, folder_path


def get_file_paths_simple(search_string: str = 'BAFU_small') -> Tuple[str, str]:
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

    if clean_file_path is None :
        clean_file_path = utils.find_non_obfuscated_file(folder_path, search_string.split('_missingpourcentage')[0])

    print(f'Found clean file at: {clean_file_path}')


    obfuscated_file_path = utils.find_obfuscated_file(folder_path, search_string)
    print(f'Found obfuscated file at: {obfuscated_file_path}')
    return clean_file_path, obfuscated_file_path


def process_matrix(matrix, normalizing):
    """Process matrix by normalizing, transposing, and replacing NaN."""
    # Check if normalization is required
    if 'Normalized' in normalizing:
        print(">> #NORMA NATERQ  LOGS : Z_SCORE\n")
        matrix = statistics.zscore_normalization(matrix)
    elif 'MinMax' in normalizing:
        print(">> #NORMA NATERQ  LOGS : MIN_MAX\n")
        _, matrix = contamination_naterq.normalize_min_max(matrix)
        contamination_naterq.print_load(matrix)

    #transposed_list = np.transpose(matrix).tolist()
    transposed_list = matrix.tolist()

    # Replace NaN values with None in the list
    for i in range(len(transposed_list)):
        for j in range(len(transposed_list[i])):
            if np.isnan(transposed_list[i][j]):
                transposed_list[i][j] = None

    return transposed_list


@csrf_exempt
def shap_call_explainer(request):
    if request.method == 'POST':
        print("#SHAP NATERQ PRINT request:", request)

        data = load_from_request(request)
        print("#SHAP NATERQ PRINT :", data)

        data_value = data[0]['data']
        data_set_value = data[0]['data_set']

        print("#SHAP NATERQ PRINT data_value:", data_value)
        print("#SHAP NATERQ PRINT data_set_value:", data_set_value)

        shap_values = shap_runner([data_value], [data_set_value], ["cdrec"])
        
        print("#SHAP NATERQ PRINT data_set_value: /||||||||||||||||||||||||||||||||||||||||||||||||||||", shap_values)

        if shap_values is not None:
            # Convert shap_values to dictionary
            shap_values_dict = {"shap_values": shap_values}
            # Serialize dictionary to JSON and set safe=False
            return JsonResponse(shap_values_dict, status=200, safe=False)
        else:
            return JsonResponse({'message': 'Invalid request'}, status=400)

@csrf_exempt
def shap_call_explainers(request):
    if request.method == 'POST':
        print("\n\n\n\n\n=======================================================================================================================")
        print("#SHAP > NATERQ PRINT request:", request)

        data, data_set = load_from_request(request)

        print("#SHAP > NATERQ PRINT :", data)

        algorithm_chosen = data.get("algorithm")
        if algorithm_chosen == "cdrec":
            algo_params = data.get('cdrec_params')
        elif algorithm_chosen == "stmvl":
            algo_params = data.get('stmvl_params')
        elif algorithm_chosen == "iim":
            algo_params = data.get('iim_params')
        elif algorithm_chosen == "mrnn":
            algo_params = data.get('mrnn_params')

        print("#SHAP > NATERQ PRINT algo_params for ",  algorithm_chosen, " : ", *algo_params)

        ground_truth_matrixes, obfuscated_matrixes, output_metrics, input_params, shap_values = shap_runner_naterq(data.get("dataset"),
                                         data.get("algorithm"),
                                         int(data.get('missing_values')),
                                         data.get('scenario'),
                                         data.get('selected_series'),
                                         data.get('normalization'),
                                         int(data.get('limitation')),
                                         int(data.get('splitter')),
                                         algo_params)

        if output_metrics is not None:
            shap_values_dict = {"shap_values":  shap_values}

            return JsonResponse(shap_values_dict, status=200, safe=False)
        else:
            return JsonResponse({'message': 'Invalid request'}, status=400)
