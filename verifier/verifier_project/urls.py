from django.contrib import admin
from django.urls import include, path
from verifier.api import *

api_endpoint = 'api/v1/'

verifier_urls = [
    path('index/', show_info),
    path('credentials/verify/', verify_credentials),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_endpoint, include(verifier_urls)),
]
