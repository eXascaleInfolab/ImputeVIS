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


# TODO Can be removed later on
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")



@csrf_exempt
def iim(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        print(f"Received name: {name}")

        # Call the main function with parameters from the request
        alg_code = data.get('alg_code', 'default_alg_code')
        # filename_input = data.get('filename_input', '../Datasets/bafu/raw_matrices/BAFU_small_with_NaN.txt')
        # filename_output = data.get('filename_output', '../Results/')
        # runtime = data.get('runtime', 0)

        folder_path = '../Datasets'
        search_string = 'BAFU_small'

        clean_file_path = utils.find_non_obfuscated_file(folder_path, search_string)
        print(f'Found clean file at: {clean_file_path}')
        obfuscated_file_path = utils.find_obfuscated_file(folder_path, search_string)
        print(f'Found obfuscated file at: {obfuscated_file_path}')

        if obfuscated_file_path is not None:
            imputed_matrix = iim_alg.main(alg_code, obfuscated_file_path)
            ground_truth_matrix = np.loadtxt(clean_file_path, delimiter=' ', )
            obfuscated_matrix = np.loadtxt(obfuscated_file_path, delimiter=' ', )
            rmse = statistics.determine_rmse(ground_truth_matrix, np.asarray(imputed_matrix), obfuscated_matrix)
            print("Finished iim! ", rmse)
            return JsonResponse({'rmse': rmse, 'matrix_imputed': np.transpose(np.asarray(imputed_matrix)).tolist()}, status=200)
        else:
            print('No matching file found')

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def mrnn(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        print(f"Received name: {name}")

        # Call the main function with parameters from the request
        alg_code = data.get('alg_code', 'default_alg_code')
        # filename_input = data.get('filename_input', '../Datasets/bafu/raw_matrices/BAFU_small_with_NaN.txt')
        # filename_output = data.get('filename_output', '../Results/')
        # runtime = data.get('runtime', 0)

        rmse, matrix_imputed = M_RNN.testerMRNN.main(alg_code)
        print("finished MRNN! ", rmse)

        return JsonResponse({'rmse': rmse, 'matrix_imputed': matrix_imputed}, status=200)

    return JsonResponse({'message': 'Invalid request'}, status=400)