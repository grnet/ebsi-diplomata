"""Generic OAuth2 client"""

import requests
import logging
from abc import ABCMeta, abstractmethod
from authlib.integrations.django_client import OAuthError

logger = logging.getLogger(__name__)


class OAuthException(BaseException):
    pass

class OAuthClient(object, metaclass=ABCMeta):

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
        """Extra params used for oauth client registration
        """

    def _check_error_param(self, request):
        # Check for error query param in request, after ensuring proper state
        # parameter (this is the only param required according to RFC6749)
        error = request.GET.get('error')
        if error:
            if error == 'access_denied':
                err = "IDProvider denied access to user"
            else:
                err = "IDProvider returned error: %s" % error
            raise OAuthException(err)

    def _fix_access_token_params(self, request):
        """Modify here retrieved access-token params (if needed)
        """
        return {}

    def retrieve_access_token(self, request):
        # NOTE: Latest version of authlib enforces the presence of the state
        # parameter, so there is no need to check it. The case of mismatchin
        # state is implicitly handled as exception below
        self._check_error_param(request)
        params = self._fix_access_token_params(request)
        try:
            token = self.oauth.authorize_access_token(request, **params)
        except OAuthError as err:
            # Ignore the common case, caused by invalid code or issueing a GET
            # on the URL without arguments
            if not err.error in ('invalid_grant', 'invalid_request',):
                logger.exception("Error during oauth flow: %s" % err.error)
            raise OAuthException(err)
        except requests.exceptions.ConnectTimeout:
            err = "Timeout during access token authorization"
            raise OAuthException(err)
        except Exception as err:
            err = "Error during access token authorization: %s" % err
            raise OAuthException(err)
        return token

    @abstractmethod
    def parse_access_token(self, request, token):
        """Define here how to extract profile from token
        """
