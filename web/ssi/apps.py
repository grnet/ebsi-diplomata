from django.conf import settings
from django.apps import AppConfig
from ssi.logic import SSIParty


class SSIConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ssi'

    def __init__(self, *args):
        self.ssi_party = SSIParty.init_from_app(settings)
        super().__init__(*args)

    def get_ssi_party(self):
        return self.ssi_party
