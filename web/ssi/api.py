import json
from json.decoder import JSONDecodeError
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from ssi.logic import fetch_did, create_did, issue_credential, \
    verify_presentation, IdentityError, CreationError, IssuanceError, \
    VerificationError
from ssi.models import User, Alumnus
from oauth.models import UserToken

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

@require_http_methods(['GET',])
def show_tokens(request):
    out = {}
    out['data'] = [t.serialize() for t in UserToken.objects.all()]
    status = 200
    return JsonResponse(out, status=status, safe=False)

@require_http_methods(['GET',])
def show_token_by_code(request):
    out = {}
    code = request.GET.get('code')
    from django.core.cache import cache
    token = cache.get('session:%s' % code)
    cache.delete('session:%s' % code)
    if not token:
        out['errors'] = ['Code invalid',]
        status = 400    # Bad request
        return JsonResponse(out, status=status)
    out['data'] = { 'token': token }
    status = 200
    return JsonResponse(out, status=status, safe=False)

@require_http_methods(['GET',])
def show_tokens_by_user(request, id):
    out = {}
    try:
        user = get_object_or_404(User, id=id)
    except Http404 as err:
        out['errors'] = ['%s' % err,]
        status = 404
        return JsonResponse(out, status=status)
    tokens = UserToken.objects.filter(user=user)
    out['data'] = [t.serialize() for t in tokens]
    status = 200
    return JsonResponse(out, status=status, safe=False)

@require_http_methods(['GET',])
def show_alumnus(request, id):
    out = {}
    try:
        alumnus = get_object_or_404(Alumnus, id=id)
    except Http404 as err:
        out['errors'] = ['%s' % err,]
        status = 404
        return JsonResponse(out, status=status)
    out['data'] = alumnus.serialize()
    status = 200
    return JsonResponse(out, status=status, safe=False)

@require_http_methods(['GET',])
def show_alumni(request):
    out = {}
    out['data'] = [a.serialize() for a in Alumnus.objects.all()]
    status = 200
    return JsonResponse(out, status=status)

from oauth.util import token_auth

@require_http_methods(['GET',])
@token_auth
def show_sample(request):
    out = {}
    out['data'] = 'sample'
    status = 200
    return JsonResponse(out, status=status)
