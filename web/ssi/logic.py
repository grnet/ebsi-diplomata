import os
import json
import logging
from django.conf import settings
from ssi_lib import SSIApp
from ssi_lib import SSIGenerationError, SSIRegistrationError, \
    SSIResolutionError, SSIIssuanceError, SSIVerificationError
from ssi_lib.conf import _Group   # TODO: Get rid of this?
from ssi_lib.conf import _Vc # TODO


class IdentityError(BaseException):     # TODO
    pass

class CreationError(BaseException):     # TODO
    pass

class IssuanceError(BaseException):     # TODO
    pass

class VerificationError(BaseException): # TODO
    pass


class SSIParty(SSIApp):

    def __init__(self, dbpath, tmpdir):
        super().__init__(dbpath, tmpdir)

    @classmethod
    def init_from_app(cls, settings):
        config = cls.derive_config(settings)
        return cls.create(config)

    @classmethod
    def create(cls, config):
        dbpath = config['dbpath']
        tmpdir = config['tmpdir']
        return cls(dbpath, tmpdir)

    @classmethod
    def derive_config(cls, settings):
        out = {}
        dbpath = os.path.join(settings.STORAGE, 'db.json')      # TODO
        tmpdir = settings.TMPDIR
        out['dbpath'] = dbpath
        out['tmpdir'] = tmpdir
        return out

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
        alias = self.store_did(did)
        return alias

    def _get_did(self):
        dids = self.get_dids()
        return dids[-1] if dids else None

    def _extract_did_creation_payload(self, payload):
        # TODO: Validate
        token = payload.get('token', '')                    # TODO
        algo = payload.get('algo', 'Ed25519')               # TODO
        onboard = payload.get('onboard', True)              # TODO
        return token, algo, onboard

    def _extract_issuance_payload(self, payload):
        # TODO: Validate
        holder = payload['holder']
        template = payload['template']
        content = payload['content']
        return holder, template, content

    def _extract_verification_payload(self, payload):
        # TODO: Implement
        vp = payload
        return vp

    def get_info(self):
        return {'TODO': 'Include here service info'}        # TODO

    def get_did(self, full=False):                          # TODO
        dids = self.get_dids()
        if not dids:
            err = 'No DID found'
            raise IdentityError(err)
        alias = dids[-1]
        if not full:
            return alias
        return super().get_did(alias)

    def create_did(self, payload):
        token, algo, onboard = self._extract_did_creation_payload(
            payload)
        self.clear_keys()
        self.clear_dids()
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

    def issue_credential(self, payload):
        holder, template, content = self._extract_issuance_payload(
            payload)
        issuer = self._get_did()
        if not issuer:
            err = 'No issuer DID found'
            raise IssuanceError(err)
        try:
            out = super().issue_credential(holder, issuer, template,
                    content)
        except SSIIssuanceError as err:
            raise IssuanceError(err)
        return out

    def verify_presentation(self, payload):
        vp = self._extract_verification_payload(payload)
        try:
            out = super().verify_presentation(vp)
        except SSIVerificationError as err:
            raise VerificationError(err)
        return out
