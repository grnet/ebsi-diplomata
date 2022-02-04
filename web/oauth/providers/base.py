"""Generic OAuth2 flow"""

from abc import ABCMeta, abstractmethod


class BaseIdProvider(object, metaclass=ABCMeta):

    def __init__(self, name, oauth, **kw):
        self._name = name
        self._oauth = oauth
        self._register()

    @property
    def name(self):
        return self._name

    @property
    def oauth(self):
        return getattr(self._oauth, self._name)

    def _register(self):
        extras = self._extra_oauth()
        self._oauth.register(name=self._name, overwrite=True,
                **extras)

    @abstractmethod
    def _extra_oauth(self):
        """
        Extra params used for oauth client registration
        """

    @abstractmethod
    def _fix_access_token_params(self, at_params):
        """
        Modify here retrieved access-token params (if needed)
        """

    @abstractmethod
    def extract_profile(self, access_token, request):
        """
        Define here how to extract profile from token
        """
