from django.apps import apps

def _app(label):
    return apps.get_app_config(label)

def load_issuer():
    return _app('issuer').get_issuer()
