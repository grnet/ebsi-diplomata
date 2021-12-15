from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from json.decoder import JSONDecodeError
from ssi.logic import IdentityError, IssuanceError, CreationError, \
        VerificationError
from common import load_ssi_party


ssi_party = load_ssi_party()

def extract_payload(request):
    return json.loads(request.body)

@require_http_methods(['GET',])
def show_info(request):
    out = ssi_party.get_info()
    status = 200
    return JsonResponse(out, safe=False, status=status)

@require_http_methods(['GET',])
def show_did(request):
    out = {}
    try:
        alias = ssi_party.get_did()
        out['did'] = alias
        status = 200
    except IdentityError as err:
        out['msg'] = '%s' % err
        status = 204
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['PUT',])
def create_did(request):
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
        alias = ssi_party.create_did(token, algo, onboard)
        out['did'] = alias
        status = 201
    except CreationError as err:
        out['err'] = '%s' % err
        status = 512                                            # TODO
        return JsonResponse(out, safe=False, status=status)
    return JsonResponse(out, safe=True, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def issue_credential(request):
    out = {}
    try:
        payload = extract_payload(request)
        holder = payload['holder']
        template = payload['template']
        content = payload['content']
    except (JSONDecodeError, KeyError,) as err:
        out['err'] = 'Bad request'
        status = 400                                            # TODO
        return JsonResponse(out, safe=False, status=status)
    try:
        vc = ssi_party.issue_credential(holder, template,
                content)
        out['vc'] = vc
        status = 200
    except IssuanceError as err:
        out['err'] = '%s' % err
        status = 512                                            # TODO
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def verify_credentials(request):
    out = {}
    try:
        payload = extract_payload(request)
        vp = payload['vp']
    except (JSONDecodeError, KeyError,) as err:
        out['err'] = 'Bad request'
        status = 400                                            # TODO
        return JsonResponse(out, safe=False, status=status)
    try:
        rslts = ssi_party.verify_presentation(vp)
        out['results'] = rslts
        status = 200
    except VerificationError as err:
        out['err'] = '%s' % err
        status = 512                                            # TODO
    return JsonResponse(out, safe=False, status=status)
