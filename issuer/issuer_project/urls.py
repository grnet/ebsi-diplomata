from django.contrib import admin
from django.urls import include, path
from issuer.api import *

api_endpoint = 'api/'

issuer_urls = [
    path('index/', show_index),
    path('did/', show_did),
    path('vc/', recv_issuance_request),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_endpoint, include(issuer_urls)),
]
