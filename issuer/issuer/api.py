from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from issuer.logic import IssuanceError
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
def issue_credential(request):
    payload = json.loads(request.body)
    try:
        out = issuer.issue_credential(payload)
    except IssuanceError as err:
        out = {'err': err}
    return JsonResponse(out, safe=False)
