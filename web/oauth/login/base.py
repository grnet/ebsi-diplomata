"""Generic OAuth2 login"""

from abc import ABCMeta, abstractmethod
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.core.cache import cache
from authlib.common.security import generate_token as generate_randomness
import uuid
from ssi.models import UserToken
from oauth.clients.base import OAuthException

CODE_EXPIRES_AFTER_SECS = settings.CODE_EXPIRES_AFTER_SECS


class OAuthLoginFailure(Exception):
    pass


class OAuthLoginHandler(object):

    def __init__(self, oauth, client_cls, login_checks=None):
        self._login_checks = login_checks
        self._client = client_cls(oauth)

    @property
    def name(self):
        return self._client.name

    def _get_redirect_uri(self, request, callback):
        redirect_uri = getattr(settings, '%s_REDIRECT_URI' % self.name.upper(),
                               None)
        if not redirect_uri:
            redirect_uri = request.build_absolute_uri(
                reverse(callback).rstrip('/'))
        return redirect_uri

    def _generate_auth_state(self, prefix=''):
        return prefix + generate_randomness()

    def redirect_to_provider(self, request, callback):
        redirect_uri = self._get_redirect_uri(request, callback)
        state = self._generate_auth_state(prefix=settings.AUTH_STATE_PREFIX)
        resp = self._client.authorize_redirect(request, redirect_uri, state)
        return resp

    def _retrieve_access_token(self, request):
        return self._client.retrieve_access_token(request)

    def _parse_access_token(self, request, token):
        return self._client.parse_access_token(request, token)

    def _extract_profile_from_access_token(self, request):
        try:
            token = self._retrieve_access_token(request)
            # profile = self._parse_access_token(request, token)
            profile = token['userinfo']
        except OAuthException as err:
            raise OAuthLoginFailure
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
        """Define here how to create user from data
        """

    def _retrieve_user(self, profile):
        info = self._extract_user_info(profile)
        data = self._extract_user_data(info)
        user = self._get_or_create_user(data)
        return user

    def _generate_token_value(self, nr_bytes=32):
        return generate_randomness(nr_bytes)

    def _generate_session_id(self):
        return str(uuid.uuid4()).replace('-', ''),

    def _generate_session_code(self, nr_bytes=32):
        return generate_randomness(nr_bytes)

    def create_session(self, request):
        profile = self._extract_profile_from_access_token(
            request)
        user = self._retrieve_user(profile)
        token = self._generate_token_value()
        UserToken.objects.create(user=user, token=token,
                                 session_id=self._generate_session_id())
        code = self._generate_session_code()
        cache.set('session:%s' % code, token, CODE_EXPIRES_AFTER_SECS)
        return code
