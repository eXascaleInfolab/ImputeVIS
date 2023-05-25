from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")



@csrf_exempt
def submit_name(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        print(f"Received name: {name}")
        return JsonResponse({'message': 'Success!'})

    return JsonResponse({'message': 'Invalid request'}, status=400)