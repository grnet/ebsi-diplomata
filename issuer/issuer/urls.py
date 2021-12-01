from django.contrib import admin
from django.urls import include, path
from core.api import *

api_endpoint = 'api/'

core_urls = [
    path('index/', show_index),
    path('did/', show_did),
    path('vc/', recv_issuance_request),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_endpoint, include(core_urls)),
]
