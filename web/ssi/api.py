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
        did = fetch_did()
    except IdentityError as err:
        out['errors'] = ['%s' % err,]
        status = 512
        return JsonResponse(out, status=status)
    out['data'] = { 'did': did }
    status = 200
    return JsonResponse(out, status=status)

@csrf_exempt
@require_http_methods(['PUT',])
def do_create_did(request):
    out = {}
    payload = extract_payload(request)
    try:
        algo    = payload['algo']
        token   = payload['token']
        onboard = payload.get('onboard', True)
    except KeyError as err:
        out['errors'] = ['Bad request',]
        status = 400
        return JsonResponse(out, status=status)
    try:
        alias = create_did(token, algo, onboard)
    except CreationError as err:
        out['errors'] = ['%s' % err,]
        status = 512
        return JsonResponse(out, status=status)
    out['data'] = { 'did': alias }
    status = 201
    return JsonResponse(out, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def do_issue_credential(request):
    out = {}
    payload = extract_payload(request)
    try:
        holder  = payload['holder']
        vc_type = payload['vc_type']
        content = payload['content']
    except KeyError as err:
        out['errors'] = ['Bad request',]
        status = 400
        return JsonResponse(out, status=status)
    try:
        credential = issue_credential(holder, vc_type,
                content)
    except IssuanceError as err:
        out['errors'] = ['%s' % err,]
        status = 512
        return JsonResponse(out, status=status)
    out['data'] = { 'credential': credential, }
    status = 200
    return JsonResponse(out, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def do_verify_credentials(request):
    out = {}
    payload = extract_payload(request)
    try:
        presentation = payload['presentation']
    except (JSONDecodeError, KeyError,) as err:
        out['errors'] = ['Bad request',]
        status = 400
        return JsonResponse(out, status=status)
    try:
        results = verify_presentation(presentation)
    except VerificationError as err:
        out['errors'] = ['%s' % err,]
        status = 512
        return JsonResponse(out, status=status)
    out['data'] = { 'results': results }
    status = 200
    return JsonResponse(out, status=status)
