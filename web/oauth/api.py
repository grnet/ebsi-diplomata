import json
from json.decoder import JSONDecodeError
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from authlib.integrations.django_client import OAuth
from .login.google import GoogleLoginHandler

oauth = OAuth()
google = GoogleLoginHandler(oauth)


@require_http_methods(['GET',])
def google_login(request):
    out = {}
    out['data'] = google.login(request)
    status = 200
    return JsonResponse(out, status=status)

@require_http_methods(['GET',])
def google_callback(request):
    out = {}
    out['data'] = google.callback(request)
    status = 200
    return JsonResponse(out, status=status)
