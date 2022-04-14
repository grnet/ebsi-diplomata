import os
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from docs import spec_to_swagger, swagger_to_html


def get_openapi_spec():
    return spec_to_swagger.generate_swagger_dict()


@require_http_methods(['GET', ])
def swagger(request):
    openapi_spec = get_openapi_spec()
    html = swagger_to_html.convert(openapi_spec)
    return HttpResponse(html)
