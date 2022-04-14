import json
from json.decoder import JSONDecodeError
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from authlib.integrations.django_client import OAuth
from oauth.login.base import OAuthLoginFailure
from oauth.login.google import GoogleLoginHandler
from util import render_200_OK, render_401_UNAUTHORIZED

oauth = OAuth()
google = GoogleLoginHandler(oauth)


@require_http_methods(['GET', ])
def google_callback(request):
    try:
        code = google.create_session(request)
    except OAuthLoginFailure:
        return render_401_UNAUTHORIZED()
    return render_200_OK({'session': code})


@require_http_methods(['GET', ])
def google_login(request):
    return google.redirect_to_provider(request, google_callback)
