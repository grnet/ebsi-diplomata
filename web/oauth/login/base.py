"""Generic OAuth2 login"""

from abc import ABCMeta, abstractmethod
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.core.cache import cache
from authlib.common.security import generate_token
import uuid
from oauth.models import UserToken

CODE_EXPIRES_AFTER_SECS = settings.CODE_EXPIRES_AFTER_SECS

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

    def _get_redirect_uri(self, request, callback):
        redirect_uri = getattr(settings, '%s_REDIRECT_URI' % self.name.upper(),
            None)
        if not redirect_uri:
            redirect_uri = request.build_absolute_uri(
                reverse(callback).rstrip('/'))
        return redirect_uri

    def _generate_state(self):
        return settings.AUTH_STATE_PREFIX + generate_token()

    def redirect_to_provider(self, request, callback):
        redirect_uri = self._get_redirect_uri(request, callback)
        state = self._generate_state()
        resp = self._oauth.provider.oauth.authorize_redirect(request,
                redirect_uri, state=state)
        return resp

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
        """Define here how to create user from data
        """

    def _generate_token_value(self, nr_bytes=32):
        return generate_token(nr_bytes)

    def _generate_session_code(self, nr_bytes=32):
        return generate_token(nr_bytes)

    def retrieve_user(self, profile):
        info = self._extract_user_info(profile)
        data = self._extract_user_data(info)
        user = self._get_or_create_user(data)
        return user

    def create_session(self, user, nr_bytes=32):
        token = self._generate_token_value(nr_bytes)
        UserToken.objects.create(
            user=user,
            token=token,
            session_id=str(uuid.uuid4()).replace('-', ''),
        )
        tmp_code = self._generate_session_code(nr_bytes)
        cache.set('session:%s' % tmp_code, CODE_EXPIRES_AFTER_SECS)
        return tmp_code
