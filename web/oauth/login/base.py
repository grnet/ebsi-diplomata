"""Generic OAuth2 login"""

from abc import ABCMeta, abstractmethod
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from authlib.common.security import generate_token


class OAuthWrapper(object):

    def __init__(self, oauth, backend_cls, **kw):
        self.provider = backend_cls(oauth, **kw)

    def generate_state(self):
        return self.provider.generate_state()


class OAuthLoginHandler(object):

    def __init__(self, oauth, backend_cls, login_checks=None):
        self._login_checks = login_checks
        self._oauth = OAuthWrapper(oauth, backend_cls)

    @property
    def name(self):
        return self._oauth.provider.name

    def get_redirect_uri(self, request, callback):
        redirect_uri = getattr(settings, '%s_REDIRECT_URI' % self.name.upper(),
            None)
        if not redirect_uri:
            redirect_uri = request.build_absolute_uri(
                reverse(callback).rstrip('/'))
        return redirect_uri

    def generate_state(self):
        # TODO: Use auth prefix from settings, if given
        token = generate_token()
        return token

    def retrieve_profile_from_token(self, request):
        # TODO: handle oauth exceptions
        token = self._oauth.provider.retrieve_access_token(request)
        profile = self._oauth.provider.parse_access_token(request, token)
        return profile

    @abstractmethod
    def _extract_user_info(self, profile):
        """Define here how to extract user info from profile
        """

    @abstractmethod
    def _extract_user_data(self, info):
        """Define here how to transform user info to data
        """

    @transaction.atomic
    @abstractmethod
    def _get_or_create_user(self, data):
        """
        """

    def retrieve_user(self, profile):
        info = self._extract_user_info(profile)
        data = self._extract_user_data(info)
        user = self._get_or_create_user(data)
        return user
