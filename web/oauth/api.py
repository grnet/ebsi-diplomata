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
    out = user
    status = 200
    return JsonResponse(out, status=status)

@require_http_methods(['GET',])
def google_login(request):
    redirect_uri = google.get_redirect_uri(request, google_callback)
    state = google.generate_state()
    return google._oauth.provider.oauth.authorize_redirect(request,
        redirect_uri, state=state)
