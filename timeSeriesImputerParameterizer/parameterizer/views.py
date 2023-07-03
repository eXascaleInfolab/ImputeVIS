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

import IIM.iim as iim_alg
import M_RNN.testerMRNN
import M_RNN.Data_Loader


# TODO Can be removed later on
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def cdrec(request):
    if request.method == 'POST':
        """
        Recovers missing values (designated as NaN) in a matrix. Supports additional parameters
        :param __py_matrix: 2D array
        :param __py_rank: truncation rank to be used (0 = detect truncation automatically)
        :param __py_eps: threshold for difference during recovery
        :param __py_iters: maximum number of allowed iterations for the algorithms
        :return: 2D array recovered matrix
        """
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)
        truncation_rank = data.get('truncation_rank', 10)  # Truncation rank used (0 = detect truncation automatically)
        epsilon = data.get('epsilon', 0.01)  # Threshold for difference during recovery
        iterations = data.get('iterations', 100)  # Maximum number of allowed iterations for the algorithm

        if clean_file_path is not None and obfuscated_file_path is not None:
            ground_truth_matrix = np.loadtxt(clean_file_path, delimiter=' ', )
            obfuscated_matrix = np.loadtxt(obfuscated_file_path, delimiter=' ', )
            # Call the main function with parameters from the request
            imputed_matrix = Wrapper.algo_collection.native_cdrec_param(
                __py_matrix=obfuscated_matrix,
                __py_rank=truncation_rank,
                __py_eps=epsilon,
                __py_iters=iterations
            )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished CDRec! RMSE: ", rmse)
            return JsonResponse({'rmse': rmse, 'mae': mae, 'mi': mi,
                                 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()}
                                , status=200)
        else:
            print('No matching datasets found for path: ', data_set)

    return JsonResponse({'message': 'Invalid request'}, status=400)

@csrf_exempt
def iim(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)

        # Call the main function with parameters from the request
        alg_code = data.get('alg_code', 'default_alg_code')

        if clean_file_path is not None and obfuscated_file_path is not None:
            imputed_matrix = iim_alg.main(alg_code, obfuscated_file_path)
            ground_truth_matrix = np.loadtxt(clean_file_path, delimiter=' ', )
            obfuscated_matrix = np.loadtxt(obfuscated_file_path, delimiter=' ', )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished IIM! RMSE: ", rmse)
            return JsonResponse({'rmse': rmse, 'mae': mae, 'mi': mi,
                                 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()},
                                status=200)
        else:
            print('No matching datasets found for path: ', data_set)

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
        seq_len = data.get('seq_len', 7)

        # filename_input = data.get('filename_input', '../Datasets/bafu/raw_matrices/BAFU_small_with_NaN.txt')
        # filename_output = data.get('filename_output', '../Results/')
        # runtime = data.get('runtime', 0)

        if clean_file_path is not None and obfuscated_file_path is not None:

            ground_truth_matrix = np.loadtxt(clean_file_path, delimiter=' ', )
            obfuscated_matrix = np.loadtxt(obfuscated_file_path, delimiter=' ', )
            # Call the main function with parameters from the request
            imputed_matrix = M_RNN.testerMRNN.mrnn_recov(obfuscated_file_path,
                                                         runtime=0,
                                                         hidden_dim=hidden_dim,
                                                         learning_rate=learning_rate,
                                                         iterations=iterations,
                                                         keep_prob=keep_prob,
                                                         seq_length=seq_len,
                                                         )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished M-RNN! RMSE: ", rmse)
            return JsonResponse({'rmse': rmse, 'mae': mae, 'mi': mi,
                                 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()},
                                status=200)
        else:
            print('No matching datasets found for path: ', data_set)

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
            ground_truth_matrix = np.loadtxt(clean_file_path, delimiter=' ', )
            obfuscated_matrix = np.loadtxt(obfuscated_file_path, delimiter=' ', )
            # Call the main function with parameters from the request
            imputed_matrix = Wrapper.algo_collection.native_stmvl_param(
                __py_matrix=obfuscated_matrix,
                __py_window=window_size,
                __py_gamma=gamma,
                __py_alpha=alpha
            )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mae = statistics.determine_mae(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            mi = statistics.determine_mutual_info(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished STMVL! RMSE: ", rmse)
            return JsonResponse({'rmse': rmse, 'mae': mae, 'mi': mi,
                                 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()}
                                , status=200)
        else:
            print('No matching datasets found for path: ', data_set)

    return JsonResponse({'message': 'Invalid request'}, status=400)



def load_from_request(request):
    data = json.loads(request.body)
    print(f"Received data: {data}")
    data_set = data.get('data_set')
    print(f"Received dataset: {data_set}")
    return data, data_set


def get_file_paths(search_string: str = 'BAFU_small'):
    folder_path = '../Datasets'
    clean_file_path = utils.find_non_obfuscated_file(folder_path, search_string.split('_obfuscate')[0])
    print(f'Found clean file at: {clean_file_path}')
    obfuscated_file_path = utils.find_obfuscated_file(folder_path, search_string)
    print(f'Found obfuscated file at: {obfuscated_file_path}')
    return clean_file_path, obfuscated_file_path
