from django.apps import apps

def _app(label):
    return apps.get_app_config(label)

def load_ssi_party():
    return _app('ssi').get_ssi_party()
