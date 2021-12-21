import json
from json.decoder import JSONDecodeError
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ssi.logic import fetch_did, create_did, issue_credential, \
    verify_presentation, IdentityError, CreationError, IssuanceError, \
    VerificationError

def extract_payload(request):
    return json.loads(request.body)

@require_http_methods(['GET',])
def show_did(request):
    out = {}
    try:
        out['did'] = fetch_did()
        status = 200
    except IdentityError as err:
        out['msg'] = '%s' % err
        status = 200                                            # TODO
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['PUT',])
def do_create_did(request):
    out = {}
    try:
        payload = extract_payload(request)
        algo = payload['algo']
        token = payload['token']
        onboard = payload.get('onboard', True)
    except (JSONDecodeError, KeyError,) as err:
        out['err'] = 'Bad request'
        status = 400                                            # TODO
        return JsonResponse(out, safe=False, status=status)
    try:
        alias = create_did(token, algo, onboard)
        out['did'] = alias
        status = 201
    except CreationError as err:
        out['err'] = '%s' % err
        status = 512                                            # TODO
    return JsonResponse(out, safe=True, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def do_issue_credential(request):
    out = {}
    try:
        payload = extract_payload(request)
        holder = payload['holder']
        vc_type = payload['vc_type']
        content = payload['content']
    except (JSONDecodeError, KeyError,) as err:
        out['err'] = 'Bad request'
        status = 400                                            # TODO
        return JsonResponse(out, safe=False, status=status)
    try:
        vc = issue_credential(holder, vc_type,
                content)
        out['vc'] = vc
        status = 200
    except IssuanceError as err:
        out['err'] = '%s' % err
        status = 512                                            # TODO
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def do_verify_credentials(request):
    out = {}
    try:
        payload = extract_payload(request)
        vp = payload['vp']
    except (JSONDecodeError, KeyError,) as err:
        out['err'] = 'Bad request'
        status = 400                                            # TODO
        return JsonResponse(out, safe=False, status=status)
    try:
        rslts = verify_presentation(vp)
        out['results'] = rslts
        status = 200
    except VerificationError as err:
        out['err'] = '%s' % err
        status = 512                                            # TODO
    return JsonResponse(out, safe=False, status=status)
