import json
import os
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from common import load_verifier


verifier = load_verifier()

@require_http_methods(['GET',])
def show_info(request):
    out = verifier.get_info()
    return JsonResponse(out, safe=False)

@csrf_exempt
@require_http_methods(['POST',])
def verify_credentials(request):
    payload = json.loads(request.body)
    verifier.verify_credentials(payload)    # TODO
    out = {'msg': 'OK'}                     # TODO
    return JsonResponse(out, safe=False)
