import json
from json.decoder import JSONDecodeError
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from authlib.integrations.django_client import OAuth
from oauth.login.base import OAuthLoginFailure
from oauth.login.google import GoogleLoginHandler

oauth = OAuth()
google = GoogleLoginHandler(oauth)


@require_http_methods(['GET', ])
def google_callback(request):
    out = {}
    try:
        code = google.create_session(request)
    except OAuthLoginFailure:
        out['errors'] = ['Unauthorized', ]
        status = 401
        return JsonResponse(out, status=status)
    out['session'] = code
    status = 200
    return JsonResponse(out, status=status)


@require_http_methods(['GET', ])
def google_login(request):
    return google.redirect_to_provider(request, google_callback)
