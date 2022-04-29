from django.contrib import admin
from django.urls import include, path
from django.conf import settings
import core.api
import oauth.api
import docs.api

api_prefix = settings.API_PREFIX + ('/' if not
                                    settings.API_PREFIX.endswith('/') else '')

core_urls = [
    path('did/', core.api.show_did),
    path('did/create/', core.api.create_did),
    path('credentials/', core.api.show_credentials),
    path('credentials/issue/', core.api.issue_credential),
    path('credentials/verify/', core.api.verify_credentials),
    path('alumni/', core.api.show_alumni),
    path('alumni/<int:id>/', core.api.show_alumnus),
    path('tokens/', core.api.show_tokens),
    path('tokens/<int:id>/', core.api.show_tokens_by_user),
    path('token/', core.api.show_token_by_code),  # /api/v1/token/?code=<code>
    path('users/current/', core.api.show_current_user),
]

oauth_urls = [
    path('google/login/', oauth.api.google_login),
    path('google/callback/', oauth.api.google_callback),
]

docs_urls = [
    path('', docs.api.swagger),
    path('swagger/', docs.api.swagger),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_prefix, include(core_urls)),
    path(api_prefix, include(oauth_urls)),
    path(api_prefix, include(docs_urls)),
]
