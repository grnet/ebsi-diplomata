from django.conf import settings
from oauth.providers.base import BaseIdProvider


class GoogleIdProvider(BaseIdProvider):

    def __init__(self, oauth, **kw):
        super().__init__(settings.PN_GOOGLE, oauth, **kw)

    def _extra_oauth(self):
        extras = {}
        # extras['compliance_fix'] = requests_with_retries
        return extras

    def _fix_access_token_params(self, at_params):
        pass

    def extract_profile(self, access_token, request):
        pass
