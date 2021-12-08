from django.contrib import admin
from django.urls import include, path
from issuer.api import *
from verifier.api import *

api_endpoint = 'api/v1/'

issuer_urls = [
    path('index/', show_info),
    path('did/', show_did),
    path('credentials/issue/', issue_credential),
]

verifier_urls = [
    # path('index/', show_info),
    path('credentials/verify/', verify_credentials),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_endpoint, include(issuer_urls)),
    path(api_endpoint, include(verifier_urls)),
]
