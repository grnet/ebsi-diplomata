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


class SSIParty(SSIApp):

    def __init__(self, dbpath, tmpdir, algo, token='',
            force_did=False):
        super().__init__(dbpath, tmpdir)
        if self.get_nr_dids() == 0 or force_did:
            logging.info('\nCLEARING\n')
            self.clear_keys()
            self.clear_dids()
            try:
                key = self.create_key(algo)
            except CreationError as err:
                logging.error('Could not create key: %s' % err)
                return
            logging.info('Created key %s' % key)
            try:
                onboard = False                                 # TODO
                alias = self.create_did(key, token, onboard)
            except CreationError as err:
                logging.error('Could not create DID: %s' % err)
                return
            logging.info('Created DID %s' % alias)

    @classmethod
    def init_from_app(cls, settings):
        config = cls.derive_config(settings)
        return cls.create(config)

    @classmethod
    def create(cls, config):
        dbpath = config['dbpath']
        tmpdir = config['tmpdir']
        algo = config['algo']
        token = config.get('token', '')
        force_did = config.get('force_did', False)
        return cls(dbpath, tmpdir, algo, token, force_did)

    @classmethod
    def derive_config(cls, settings):
        out = {}
        dbpath = os.path.join(settings.STORAGE, 'db.json')      # TODO
        tmpdir = settings.TMPDIR
        algo = os.environ.get('KEYGEN_ALGO', 'Ed25519')         # TODO
        token = os.environ.get('EBSI_TOKEN', '')                # TODO
        force_did = bool(int(os.environ.get('FORCE_DID',
            default=0)))                                        # TODO
        out['dbpath'] = dbpath
        out['tmpdir'] = tmpdir
        out['algo'] = algo
        out['token'] = token
        out['force_did'] = force_did
        return out

    def create_key(self, algo):
        logging.info('Generating %s key (takes seconds) ...' % algo)
        try:
            key = self.generate_key(algo)
        except SSIGenerationError as err:
            err = 'Could not generate key: %s' % err
            raise CreationError(err)
        alias = self.store_key(key)
        return alias

    def create_did(self, key, token, onboard=True):
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

    def _extract_issuance_payload(self, payload):
        # TODO: Validate structure
        holder_did = payload['holder']
        template = payload['template']
        content = payload['content']
        return holder_did, template, content

    def get_info(self):
        return {'TODO': 'Include here service info'}        # TODO

    def _get_did(self):
        dids = self.get_dids()
        return dids[-1] if dids else None

    def get_did(self, full=False):                          # TODO
        dids = self.get_dids()
        if not dids:
            err = 'No DID found'
            raise IdentityError(err)
        alias = dids[-1]
        if not full:
            return alias
        return super().get_did(alias)

    def issue_credential(self, payload):
        holder_did, template, content = self._extract_issuance_payload(
            payload)
        issuer_did = self._get_did()
        if not issuer_did:
            err = 'No issuer DID found'
            raise IssuanceError(err)
        try:
            out = super().issue_credential(holder_did, issuer_did, template,
                    content)
        except SSIIssuanceError as err:
            raise IssuanceError(err)
        return out
