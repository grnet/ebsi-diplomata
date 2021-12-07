from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import json
import os
from issuer.logic import get_did, run_cmd, issue_vc, get_did_resource, \
    resolve_vc_args
from common import load_issuer


issuer = load_issuer()

@require_http_methods(['GET',])
def show_info(request):
    out = {'TODO': 'Include here issuer info'}
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did(request):
    resp, code = get_did()
    # TODO
    if code == 0:
        _path = os.path.join(settings.STORAGE, 'did', '1', 'repr.json')
        with open(_path, 'r') as f:
            out = json.load(f)
    else:
        out = {'error': resp}
    return JsonResponse(out, safe=False)

@csrf_exempt
@require_http_methods(['POST',])
def issue_credentials(request):
    payload = json.loads(request.body)
    args = resolve_vc_args(payload)
    resp, code = issue_vc(*args)
    out = {}
    # TODO
    if code == 0:
        vc_file = resp
        with open(vc_file, 'r') as f:
            out = json.load(f)
    else:
        out['error'] = resp
    return JsonResponse(out, safe=False)
