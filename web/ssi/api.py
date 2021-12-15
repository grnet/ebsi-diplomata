from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from ssi.logic import IssuanceError, CreationError, IdentityError
from ssi.logic import IdentityError, IssuanceError, CreationError, \
        VerificationError
from common import load_ssi_party


ssi_party = load_ssi_party()

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
    except IdentityError as err:
        out['err'] = '%s' % err
    status = 200
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['PUT',])
def create_did(request):
    payload = json.loads(request.body)
    out = {}
    try:
        alias = ssi_party.create_did(payload)
        out['did'] = alias
        status = 201
    except CreationError as err:
        out['err'] = '%s' % err
        status = 512                                    # TODO
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def issue_credential(request):
    payload = json.loads(request.body)                  # TODO
    out = {}
    try:
        vc = ssi_party.issue_credential(payload)        # TODO
        out['vc'] = vc
        status = 200
    except IssuanceError as err:
        out['err'] = '%s' % err
        status = 512
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def verify_credentials(request):
    payload = json.loads(request.body)
    out = {}
    try:
        reslt = ssi_party.verify_presentation(payload)  # TODO
        out['results'] = reslt
        status = 200
    except VerificationError as err:
        out['err'] = '%s' % err
        status = 512
    return JsonResponse(out, safe=False, status=status)
