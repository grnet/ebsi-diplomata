from django.contrib import admin
from django.urls import include, path
from ssi.api import *
from oauth.api import *

api_endpoint = 'api/v1/'

ssi_urls = [
    path('did/', show_did),
    path('did/create/', do_create_did),
    path('credentials/issue/', do_issue_credential),
    path('credentials/verify/', do_verify_credentials),
]

oauth_urls = [
    path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_endpoint, include(ssi_urls)),
    path(api_endpoint, include(oauth_urls)),
]
