"""Generic OAuth2 login"""

from abc import ABCMeta, abstractmethod
from django.db import transaction


class OAuthWrapper(object):

    def __init__(self, oauth, backend_cls, **kw):
        self._oauth = backend_cls(oauth, **kw)


class OAuthLoginHandler(object):

    def __init__(self, oauth, backend_cls, login_checks=None):
        self._login_checks = login_checks
        self._oauth = OAuthWrapper(oauth, backend_cls)

    @abstractmethod
    def _extract_user_info(self, *args):
        """
        """

    @abstractmethod
    def _extract_user_data(self, info):
        """
        """

    @transaction.atomic
    @abstractmethod
    def _get_or_create_user(self, data):
        """
        """

    def retrieve_user(self, *args):
        info = self._extract_user_info(*args)
        data = self._extract_user_data(info)
        user = self._get_or_create_user(data)
        return user
