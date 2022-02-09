from django.conf import settings
from oauth.clients.base import OAuthClient, OAuthException
from authlib.jose.errors import JoseError
from authlib.integrations.django_client import OAuthError


class GoogleOAuthClient(OAuthClient):

    def __init__(self, oauth, **kw):
        super().__init__(settings.PN_GOOGLE, oauth, **kw)

    def _extra_oauth(self):
        return {
            # 'compliance_fix': requests_with_retries,
        }
