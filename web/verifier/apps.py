from django.conf import settings
from django.apps import AppConfig
from verifier.logic import Verifier


class VerifierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'verifier'

    def __init__(self, *args):
        self.verifier = Verifier.init_from_app(settings)
        super().__init__(*args)

    def get_verifier(self):
        return self.verifier
