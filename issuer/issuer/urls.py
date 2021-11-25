from django.contrib import admin
from django.urls import include, path
from core.api import *

api_endpoint = 'api/'

core_urls = [
    path('did/', show_did),
    path('did/authorization', show_did_authorization),
    path('did/presentation', show_did_presentation),
    path('did/token', show_did_access_token),
    path('did/ake', show_did_ake),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_endpoint, include(core_urls)),
]
