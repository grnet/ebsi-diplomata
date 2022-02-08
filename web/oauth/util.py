from functools import wraps
from django.views.decorators import csrf

def token_auth(func):
    @wraps(func)
    def _wrapper(request, *args, **kwargs):
        # TODO
        resp = func(request, *args, **kwargs)
        return resp
    return csrf.csrf_exempt(_wrapper)
