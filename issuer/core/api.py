from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import subprocess
import json

EBSI_PREFIX = 'did:ebsi:'   # TODO

def run_cmd(args):
    result = subprocess.run(args, stdout=subprocess.PIPE)
    resp = result.stdout.decode('utf-8').rstrip('\n')
    code = result.returncode
    return (resp, code)

def get_did(nr=None, no_ebsi_prefix=False):
    args = ['get-did']
    if nr:
        args += ['--nr', str(nr)]
    resp, code = run_cmd(args)
    if no_ebsi_prefix:
        resp = resp.lstrip(EBSI_PREFIX)
    return resp, code

def get_did_resource(did, resource):
    _path = f'{settings.WALTDIR}/data/ebsi/{did}/{resource}.json'   # TODO
    with open(_path, 'r') as f:
        if resource == 'ebsi_access_token':
            out = f.read()
        else:
            out = json.load(f)
    return out

@require_http_methods(['GET',])
def show_index(request):
    out = {'TODO': 'Include here issuer info'}
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did(request):
    resp, code = get_did()
    if code == 0:
        _path = f'{settings.STORAGE}/did/1/repr.json'   # TODO
        with open(_path, 'r') as f:
            out = json.load(f)
    else:
        out = {'error': resp}
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did_authorization(request):
    resp, code = get_did(no_ebsi_prefix=True)
    if code == 0:
        did = resp
        out = get_did_resource(did, 'verifiable-authorization')
    else:
        out = {'error': resp}
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did_presentation(request):
    resp, code = get_did(no_ebsi_prefix=True)
    if code == 0:
        did = resp
        out = get_did_resource(did, 'verifiable-presentation')
    else:
        out = {'error': resp}
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did_access_token(request):
    resp, code = get_did(no_ebsi_prefix=True)
    if code == 0:
        did = resp
        out = get_did_resource(did, 'ebsi_access_token')
    else:
        out = {'error': resp}
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did_ake1_enc(request):
    resp, code = get_did(no_ebsi_prefix=True)
    if code == 0:
        did = resp
        out = get_did_resource(did, 'ake1_enc')
    else:
        out = {'error': resp}
    return JsonResponse(out, safe=False)
