import json
from json.decoder import JSONDecodeError
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from core.models import User, Alumnus, UserToken, Credential
from core import logic
from core.logic import (
    IdentityError,
    CreationError,
    IssuanceError,
    VerificationError,
)
from oauth.util import token_auth
from util import (
    render_200_OK,
    render_201_CREATED,
    render_400_BAD_REQUEST,
    render_404_NOT_FOUND,
    render_errors,
)


def _extract_payload(request):
    return json.loads(request.body)


def _extract_user_data(request):
    data = {}
    if request.user:
        data['id'] = request.user.id
        if request.user.is_alumnus():
            alumnus = Alumnus.objects.get(user=request.user)
            data.update(alumnus.serialize())
    return data


@require_http_methods(['GET', ])
def show_did(request):
    try:
        did = logic.fetch_did()
    except IdentityError as err:
        return render_errors(['%s' % err], 512)  # TODO
    return render_200_OK({'did': did})


@csrf_exempt
@require_http_methods(['PUT', ])
def create_did(request):
    payload = _extract_payload(request)
    try:
        algo = payload['algo']
        token = payload['token']
        onboard = payload.get('onboard', True)
    except KeyError as err:
        return render_400_BAD_REQUEST()
    try:
        alias = logic.create_did(token, algo, onboard)
    except CreationError as err:
        return render_errors(['%s' % err, ], 512)
    return render_201_CREATED({'did': alias})


@csrf_exempt
@require_http_methods(['POST', ])
@token_auth
def issue_credential(request):
    payload = _extract_payload(request)
    try:
        holder = payload['holder']
        vc_type = payload['vc_type']
        content = payload['content']
    except KeyError as err:
        return render_400_BAD_REQUEST()
    user_data = _extract_user_data(request)
    try:
        credential = logic.issue_credential(holder, vc_type,
                                            content, user_data)
    except IssuanceError as err:
        return render_errors(['%s' % err, ], 512)
    return render_200_OK({'credential': credential})


@csrf_exempt
@require_http_methods(['POST', ])
def verify_credentials(request):
    payload = _extract_payload(request)
    try:
        presentation = payload['presentation']
    except (JSONDecodeError, KeyError,) as err:
        return render_400_BAD_REQUEST()
    try:
        results = logic.verify_presentation(presentation)
    except VerificationError as err:
        return render_errors(['%s' % err, ], 512)
    return render_200_OK({'results': results})


@require_http_methods(['GET', ])
def show_credentials(request):
    credentials = [c.serialize() for c in Credential.objects.all()]
    return render_200_OK(credentials)


@require_http_methods(['GET', ])
def show_tokens(request):
    tokens = [t.serialize() for t in UserToken.objects.all()]
    return render_200_OK(tokens)


@require_http_methods(['GET', ])
def show_token_by_code(request):
    code = request.GET.get('code')
    token = cache.get(code)
    cache.delete(code)
    if not token:
        return render_400_BAD_REQUEST('Code invalid')
    return render_200_OK({'token': token})


@require_http_methods(['GET', ])
def show_tokens_by_user(request, id):
    try:
        user = get_object_or_404(User, id=id)
    except Http404 as err:
        return render_404_NOT_FOUND('%s' % err)
    tokens = [t.serialize() for t in UserToken.objects.filter(
        user=user)]
    return render_200_OK(tokens)


@require_http_methods(['GET', ])
def show_alumnus(request, id):
    try:
        alumnus = get_object_or_404(Alumnus, id=id)
    except Http404 as err:
        return render_404_NOT_FOUND('%s' % err)
    return render_200_OK(alumnus.serialize())


@require_http_methods(['GET', ])
def show_alumni(request):
    alumni = [a.serialize() for a in Alumnus.objects.all()]
    return render_200_OK(alumni)


@require_http_methods(['GET', ])
@token_auth
def show_current_user(request):
    user = _extract_user_data(request)
    return render_200_OK(user)
