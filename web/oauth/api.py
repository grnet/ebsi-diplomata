import json
from json.decoder import JSONDecodeError
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from authlib.integrations.django_client import OAuth
from oauth.login.google import GoogleLoginHandler

oauth = OAuth()
google = GoogleLoginHandler(oauth)

@require_http_methods(['GET',])
def google_callback(request):
    profile = google.retrieve_profile_from_token(request)
    user = google.retrieve_user(profile)
    tmp_code = google.create_session(user)
    out = {}
    out['session'] = tmp_code
    status = 200
    return JsonResponse(out, status=status)

@require_http_methods(['GET',])
def google_login(request):
    resp = google.redirect_to_provider(request, google_callback)
    return resp
