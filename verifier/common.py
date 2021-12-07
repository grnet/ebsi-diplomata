from django.apps import apps

def _app(label):
    return apps.get_app_config(label)

def load_verifier():
    return _app('verifier').get_verifier()
