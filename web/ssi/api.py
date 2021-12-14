from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from ssi.logic import IssuanceError, CreationError, IdentityError
from common import load_ssi_party


ssi_party = load_ssi_party()

@require_http_methods(['GET',])
def show_info(request):
    out = ssi_party.get_info()
    status = 200
    return JsonResponse(out, safe=False, status=status)

@require_http_methods(['GET',])
def show_did(request):
    try:
        out = ssi_party.get_did()
        status = 200
    except IdentityError as err:
        out = {'message': '%s' % err}                   # TODO
        status = 200                                    # TODO
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['PUT',])
def create_did(request):
    payload = json.loads(request.body)
    try:
        alias = ssi_party.create_did(payload)
        out = {'did': alias}
        status = 201
    except CreationError as err:
        out = {'message': '%s' % err}                   # TODO
        status = 512                                    # TODO
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def issue_credential(request):
    payload = json.loads(request.body)
    try:
        out = ssi_party.issue_credential(payload)       # TODO
        status = 200
    except IssuanceError as err:
        out = {'message': '%s' % err}                   # TODO
        status = 512
    return JsonResponse(out, safe=False, status=status)

@csrf_exempt
@require_http_methods(['POST',])
def verify_credentials(request):
    payload = json.loads(request.body)
    try:
        out = ssi_party.verify_presentation(payload)    # TODO
        status = 200
    except VerificationError as err:
        out = {'message': '%s' % err}                   # TODO
        status = 512
    return JsonResponse(out, safe=False, status=status)
