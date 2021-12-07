import json
import os
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@require_http_methods(['GET',])
def show_info(request):
    out = {'TODO': 'Include here verifier info'}
    return JsonResponse(out, safe=False)

@csrf_exempt
@require_http_methods(['POST',])
def verify_credentials(request):
    payload = json.loads(request.body)
    tmpfile = os.path.join(settings.TMPDIR, 'vc.json')
    with open(tmpfile, 'w+') as f:
        json.dump(payload, f, indent=4)
    out = {'msg': 'OK'}
    return JsonResponse(out, safe=False)
