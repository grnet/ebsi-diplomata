from django.contrib import admin
from django.urls import include, path
from django.conf import settings
import ssi.api as api
import oauth.api as auth

api_prefix = settings.API_PREFIX + ('/' if not
        settings.API_PREFIX.endswith('/') else '')

ssi_urls = [
    path('did/', api.show_did),
    path('did/create/', api.do_create_did),
    path('credentials/issue/', api.do_issue_credential),
    path('credentials/verify/', api.do_verify_credentials),
    path('alumni/', api.show_alumni),
    path('alumni/<int:id>/', api.show_alumnus),
    path('tokens/', api.show_tokens),
    path('tokens/<int:id>/', api.show_tokens_by_user),
    path('token/', api.show_token_by_code), # /api/v1/token/?code=<code>
    path('users/current/', api.show_current_user),
]

oauth_urls = [
    path('google/login/', auth.google_login),
    path('google/callback/', auth.google_callback),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_prefix, include(ssi_urls)),
    path(api_prefix, include(oauth_urls)),
]
