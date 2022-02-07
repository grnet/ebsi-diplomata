import json
from json.decoder import JSONDecodeError
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from authlib.integrations.django_client import OAuth
from oauth.login.google import GoogleLoginHandler

oauth = OAuth()
google = GoogleLoginHandler(oauth)


def _get_redirect_uri(request, login_handler, callback):
    redirect_uri = getattr(settings, '%s_REDIRECT_URI' % login_handler.name.upper(),
        None)
    if not redirect_uri:
        redirect_uri = request.build_absolute_uri(
            reverse(callback).rstrip('/'))
    return redirect_uri

@require_http_methods(['GET',])
def google_callback(request):
    profile = google.retrieve_profile_from_token(request)
    user = google.retrieve_user(profile)
    out = user
    status = 200
    return JsonResponse(out, status=status)

@require_http_methods(['GET',])
def google_login(request):
    redirect_uri = _get_redirect_uri(request, google, google_callback)
    state = google.generate_state()
    return google._oauth.provider.oauth.authorize_redirect(request,
        redirect_uri, state=state)
