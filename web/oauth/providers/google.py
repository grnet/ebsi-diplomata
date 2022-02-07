from django.conf import settings
from oauth.providers.base import BaseIdProvider, OAuthException
from authlib.jose.errors import JoseError
from authlib.integrations.django_client import OAuthError


class GoogleIdProvider(BaseIdProvider):

    def __init__(self, oauth, **kw):
        super().__init__(settings.PN_GOOGLE, oauth, **kw)

    def _extra_oauth(self):
        return {
            # 'compliance_fix': requests_with_retries,
        }

    def parse_access_token(self, request, token):
        try:
            profile = self.oauth.parse_id_token(request, token)
        except JoseError as err:
            # Captures multiple cases of bad encoding, or insufficient
            # crypto, or low or wrong security standards:
            # https://github.com/lepture/authlib/blob/master/authlib/jose/errors.py
            err = "JWT error getting profile: %s" % err
            raise OAuthException(err)
        except OAuthError as err:
            err = "OAuth error getting profile: %s" % err
            raise OAuthException(err)
        except Exception as err:
            err = "Something wrong happened: %s" % err
            raise OAuthException(err)
        return profile
