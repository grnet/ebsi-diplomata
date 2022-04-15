from functools import wraps
from django.views.decorators import csrf
from ssi.models import User, UserToken
from django.utils import timezone
from django.http import JsonResponse


class Unauthorized(Exception):
    pass


def _extract_token_from_headers(request):
    token = request.headers.get('Authorization', None)
    if token in (None, 'null', '',):
        return None
    label, token = token.split(' ', 1)
    if label != 'Token':
        raise Unauthorized('Invalid token')
    return token


def _load_session(token):
    try:
        token = UserToken.objects.get(token=token)
    except UserToken.DoesNotExist:
        raise Unauthorized('Invalid token')
    if not token.is_active:
        raise Unauthorized('Invalid token')
    now = timezone.now()
    if token.has_expired(now):
        token.is_active = False
        token.save()
        raise Unauthorized('Invalid token')
    token.refresh_if_needed(now)
    return token


def _load_user_from_session(user_token):
    try:
        user = user_token.user
    except User.DoesNotExist:
        raise Unauthorized('Invalid token')
    return user


def token_auth(func):
    """Decorator for authorized requests. When a view is decorated with this,
    the request headers must include

        "Authorization": "Token <token>",

    otherwise Unauhorized 401 with cause is returned.
    """
    @wraps(func)
    def _wrapper(request, *args, **kwargs):
        request.x_auth_token = None
        try:
            token = _extract_token_from_headers(request)
            if not token:
                err = "Access denied: No authorization token"
                raise Unauthorized(err)
            request.x_auth_token = token
            request.user_token = _load_session(token)
            request.user = _load_user_from_session(request.user_token)
        except Unauthorized as err:
            return JsonResponse({'errors': ['%s' % err, ]}, status=401)
        resp = func(request, *args, **kwargs)
        return resp
    return csrf.csrf_exempt(_wrapper)
