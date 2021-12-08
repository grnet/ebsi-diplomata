from django.conf import settings
from django.apps import AppConfig
from issuer.logic import Issuer


class IssuerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'issuer'

    def __init__(self, *args):
        self.issuer = Issuer.init_from_app(settings)
        super().__init__(*args)

    def get_issuer(self):
        return self.issuer
