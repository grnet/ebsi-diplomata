from django.contrib import admin
from django.urls import include, path
from verifier.api import *

api_endpoint = 'api/'

verifier_urls = [
    path('index/', show_index),
    path('vc/', recv_vc),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_endpoint, include(verifier_urls)),
]
