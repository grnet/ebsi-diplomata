from oauth.login.base import OAuthLoginHandler
from oauth.providers.google import GoogleIdProvider


class GoogleLoginHandler(OAuthLoginHandler):

    def __init__(self, oauth):
        super().__init__(oauth, GoogleIdProvider)

    def _extract_user_info(self, profile):
        pass

    def _extract_user_data(self, info):
        pass

    def _get_or_create_user(self, data):
        pass
