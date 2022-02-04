import json
from json.decoder import JSONDecodeError
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from oauth.logic import authlib

@require_http_methods(['GET',])
def google_login(request):
    out = {}
    out['data'] = { 'message': 'dummy google login' }
    status = 200
    return JsonResponse(out, status=status)

@require_http_methods(['GET',])
def google_callback(request):
    out = {}
    out['data'] = { 'message': 'dummy google callback' }
    status = 200
    return JsonResponse(out, status=status)
