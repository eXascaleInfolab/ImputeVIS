from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os, sys
sys.path.insert(0, os.path.abspath(".."))

from IIM.iim import main



# TODO Can be removed later on
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")



@csrf_exempt
def submit_name(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        print(f"Received name: {name}")

        # Call the main function with parameters from the request
        alg_code = data.get('alg_code', 'default_alg_code')
        # filename_input = data.get('filename_input', '../Datasets/bafu/raw_matrices/BAFU_small_with_NaN.txt')
        # filename_output = data.get('filename_output', '../Results/')
        # runtime = data.get('runtime', 0)

        rmse = main(alg_code)
        print("finished! ", rmse)

        return JsonResponse({'rmse': rmse}, status=200)

    return JsonResponse({'message': 'Invalid request'}, status=400)