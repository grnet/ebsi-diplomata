import json
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

@require_http_methods(['GET',])
def show_index(request):
    out = {'TODO': 'Include here verifier info'}
    return JsonResponse(out, safe=False)

@require_http_methods(['POST',])
def recv_vc(request):
    raise NotImplementedError('TODO')
