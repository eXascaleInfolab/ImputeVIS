from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os, sys
import numpy as np


sys.path.insert(0, os.path.abspath(".."))
from Utils_Thesis import utils, statistics

import IIM.iim as iim_alg
import M_RNN.testerMRNN
import M_RNN.Data_Loader


# TODO Can be removed later on
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")



@csrf_exempt
def iim(request):
    if request.method == 'POST':
        data, data_set = load_from_request(request)
        clean_file_path, obfuscated_file_path = get_file_paths(data_set)

        # Call the main function with parameters from the request
        alg_code = data.get('alg_code', 'default_alg_code')
        # filename_input = data.get('filename_input', '../Datasets/bafu/raw_matrices/BAFU_small_with_NaN.txt')
        # filename_output = data.get('filename_output', '../Results/')
        # runtime = data.get('runtime', 0)

        if clean_file_path is not None and obfuscated_file_path is not None:
            imputed_matrix = iim_alg.main(alg_code, obfuscated_file_path)
            ground_truth_matrix = np.loadtxt(clean_file_path, delimiter=' ', )
            obfuscated_matrix = np.loadtxt(obfuscated_file_path, delimiter=' ', )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished IIM! RMSE: ", rmse)
            return JsonResponse({'rmse': rmse, 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()}, status=200)
        else:
            print('No matching file found or erroneous configuration, stopping imputation.')

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
                                                         keep_prob=keep_prob
                                                         )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished M-RNN! RMSE: ", rmse)
            return JsonResponse({'rmse': rmse, 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()}
                                , status=200)
        else:
            print('No matching file found or erroneous configuration, stopping imputation.')

    return JsonResponse({'message': 'Invalid request'}, status=400)


def load_from_request(request):
    data = json.loads(request.body)
    print(f"Received data: {data}")
    data_set = data.get('data_set')
    print(f"Received dataset: {data_set}")
    return data, data_set


def get_file_paths(search_string: str = 'BAFU_small'):
    folder_path = '../Datasets'
    clean_file_path = utils.find_non_obfuscated_file(folder_path, search_string)
    print(f'Found clean file at: {clean_file_path}')
    obfuscated_file_path = utils.find_obfuscated_file(folder_path, search_string)
    print(f'Found obfuscated file at: {obfuscated_file_path}')
    return clean_file_path, obfuscated_file_path
