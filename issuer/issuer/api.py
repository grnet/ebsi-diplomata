from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from common import load_issuer


issuer = load_issuer()

@require_http_methods(['GET',])
def show_info(request):
    out = issuer.get_info()
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did(request):
    out = issuer.get_did()
    return JsonResponse(out, safe=False)

@csrf_exempt
@require_http_methods(['POST',])
def issue_credentials(request):
    payload = json.loads(request.body)
    out = issuer.issue_credentials(payload)
    return JsonResponse(out, safe=False)
