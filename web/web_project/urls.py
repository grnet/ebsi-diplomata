from django.contrib import admin
from django.urls import include, path
from ssi.api import *

api_endpoint = 'api/v1/'

ssi_urls = [
    path('', show_info),
    path('did/', show_did),
    path('did/create/', create_did),
    path('credentials/issue/', issue_credential),
    path('credentials/verify/', verify_credentials),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_endpoint, include(ssi_urls)),
]
