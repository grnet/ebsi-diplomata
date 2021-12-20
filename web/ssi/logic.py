import os
import json
import logging
from django.conf import settings
from ssi_lib import SSIApp
from ssi_lib import SSIGenerationError, SSIRegistrationError, \
    SSIResolutionError, SSIIssuanceError, SSIVerificationError


class IdentityError(BaseException):     # TODO
    pass

class CreationError(BaseException):     # TODO
    pass

class IssuanceError(BaseException):     # TODO
    pass

class VerificationError(BaseException): # TODO
    pass


class SSIParty(SSIApp):

    def __init__(self, tmpdir):
        # TODO: Explicitly define data vault location for securely storing
        # asymmetric key and relevant DID.
        self.keyfile = os.path.join(settings.STORAGE, 'jwk.json')   # TODO
        self.didfile = os.path.join(settings.STORAGE, 'did.json')   # TODO
        super().__init__(tmpdir)

    @classmethod
    def init_from_app(cls, settings):
        config = cls.derive_config(settings)
        return cls.create(config)

    @classmethod
    def create(cls, config):
        tmpdir = config['tmpdir']
        return cls(tmpdir)

    @classmethod
    def derive_config(cls, settings):
        out = {}
        tmpdir = settings.TMPDIR
        out['tmpdir'] = tmpdir
        return out

    def _get_key(self, *args):
        try:
            with open(self.keyfile, 'r') as f:
                out = json.load(f)
        except FileNotFoundError:
            return None
        return out

    def _get_local_did(self):                                           # TODO
        try:
            with open(self.didfile, 'r') as f:
                out = json.load(f)
        except FileNotFoundError:
            return None
        return out

    def store_key(self, entry):
        alias = self._extract_alias_from_key(entry)
        with open(self.keyfile, 'w+') as f:
            json.dump(entry, f, indent=4)
        return alias

    def store_local_did(self, entry):
        alias = self._extract_alias_from_did(entry)
        with open(self.didfile, 'w+') as f:
            json.dump(entry, f, indent=4)
        return alias

    def _create_key(self, algo):
        logging.info('Generating %s key (takes seconds) ...' % algo)
        try:
            key = self.generate_key(algo)
        except SSIGenerationError as err:
            err = 'Could not generate key: %s' % err
            raise CreationError(err)
        alias = self.store_key(key)
        return alias

    def _create_did(self, key, token, onboard=True):
        logging.info('Generating DID (takes seconds) ...')
        try:
            did = self.generate_did(key, token, onboard)
        except SSIGenerationError as err:
            err = 'Could not generate DID: %s' % err
            raise CreationError(err)
        if onboard:
            logging.info('Registering DID to EBSI (takes seconds)...')
            try:
                self.register_did(did['id'], token)
            except SSIRegistrationError as err:
                err = 'Could not register: %s' % err
                raise CreationError(err)
            logging.info('DID registered to EBSI')
        alias = self.store_local_did(did)
        return alias

    def get_info(self):
        return {'TODO': 'Include here service info'}        # TODO

    def get_local_did(self, full=False):                          # TODO
        did = self._get_local_did()
        if not did:
            err = 'No DID found'
            raise IdentityError(err)
        alias = self._extract_alias_from_did(did)
        return alias

    def create_did(self, token, algo, onboard):
        try:
            key = self._create_key(algo)
        except CreationError as err:
            err = 'Could not create key: %s' % err
            raise CreationError(err)
        logging.info('Created key %s' % key)
        try:
            alias = self._create_did(key, token, onboard)
        except CreationError as err:
            err = 'Could not create DID: %s' % err
            raise CreationError(err)
        logging.info('Created DID %s' % alias)
        return alias

    def issue_credential(self, holder, template, content):
        issuer = self.get_local_did()
        if not issuer:
            err = 'No issuer DID found'
            raise IssuanceError(err)
        try:
            out = super().issue_credential(holder, issuer, template,
                    content)
        except SSIIssuanceError as err:
            raise IssuanceError(err)
        return out

    def verify_presentation(self, vp):
        try:
            out = super().verify_presentation(vp)
        except SSIVerificationError as err:
            raise VerificationError(err)
        return out
