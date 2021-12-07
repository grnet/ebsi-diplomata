from django.contrib import admin
from django.urls import include, path
from issuer.api import *

api_endpoint = 'api/v1/'

issuer_urls = [
    path('index/', show_info),
    path('did/', show_did),
    path('credentials/issue/', issue_credentials),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_endpoint, include(issuer_urls)),
]
