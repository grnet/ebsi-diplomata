from oauth.login.base import OAuthLoginHandler
from oauth.providers.google import GoogleIdProvider


class GoogleLoginHandler(OAuthLoginHandler):

    def __init__(self, oauth):
        super().__init__(oauth, GoogleIdProvider)

    def _extract_user_info(self, *args):
        pass

    def _extract_user_data(self, info):
        pass

    def _get_or_create_user(self, data):
        pass

    def login(self, request):
        return { 'message': 'dummy google login' }

    def callback(self, request):
        return { 'message': 'dummy google callback' }
