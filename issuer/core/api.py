import json
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

@require_http_methods(['GET',])
def show_did(request):
    # _path = f'{settings.STORAGE}/dids/oculus.json'
    # with open(_path, 'r') as f:
    #     did = json.load(f)
    did = {'a': 0, 'b': 1}
    out = did
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did_authorization(request):
    # _path = f'{settings.WALTDIR}/data/ebsi/' + \
    #         'zcG8iHhNeUHgUUciVs1nExy/verifiable-authorization.json'
    # with open(_path, 'r') as f:
    #     authorization = json.load(f)
    authorization = {'a': 0, 'b': 1}
    out = authorization
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did_presentation(request):
    # _path = f'{settings.WALTDIR}/data/ebsi/' + \
    #         'zcG8iHhNeUHgUUciVs1nExy/verifiable-presentation.json'
    # with open(_path, 'r') as f:
    #     presentation = json.load(f)
    presentation = {'a': 0, 'b': 1}
    out = presentation
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did_access_token(request):
    # _path = f'{settings.WALTDIR}/data/ebsi/' + \
    #         'zcG8iHhNeUHgUUciVs1nExy/ebsi_access_token.json'
    # with open(_path, 'r') as f:
    #     access_token = f.read()
    access_token = {'a': 0, 'b': 1}
    out = access_token
    return JsonResponse(out, safe=False)

@require_http_methods(['GET',])
def show_did_ake(request):
    # _path = f'{settings.WALTDIR}/data/ebsi/' + \
    #         'zcG8iHhNeUHgUUciVs1nExy/ake1_enc.json'
    # with open(_path, 'r') as f:
    #     ake = json.load(f)
    ake = {'a': 0, 'b': 1}
    out = ake
    return JsonResponse(out, safe=False)
