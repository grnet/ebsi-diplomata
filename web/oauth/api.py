import json
from json.decoder import JSONDecodeError
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from oauth.logic import authlib

@require_http_methods(['GET',])
def login(request):
    out = {}
    out['data'] = { 'message': 'dummy login' }
    status = 200
    return JsonResponse(out, status=status)
