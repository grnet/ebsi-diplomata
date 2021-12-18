import os
import json
import logging
from django.conf import settings
from ssi_lib import SSIApp
from ssi_lib import SSIGenerationError, SSIRegistrationError, \
    SSIResolutionError, SSIIssuanceError, SSIVerificationError
from ssi_lib.conf import _Group   # TODO: Get rid of this?
from ssi_lib.conf import _Vc # TODO
from .db import DbConnector


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
        self._db = DbConnector(dbpath)
        super().__init__(tmpdir)

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

    def _extract_alias_from_key(self, entry):
        return entry['kid']

    def _extract_alias_from_did(self, entry):
        return entry['id']

    def _extract_key_from_did(self, entry):
        return entry['verificationMethod'][0]['publicKeyJwk']['kid']

    def _extract_alias_from_vc(self, entry):
        return entry['id']

    def _extract_holder_from_vc(self, entry):
        return entry['credentialSubject']['id']

    def _extract_alias_from_vp(self, entry):
        return entry['id']

    def _extract_holder_from_vp(self, entry):
        return entry['holder']

    def get_aliases(self, group):
        return self._db.get_aliases(group)

    def get_keys(self):
        return self._db.get_aliases(_Group.KEY)

    def get_dids(self):
        return self._db.get_aliases(_Group.DID)

    def get_credentials(self):
        return self._db.get_aliases(_Group.VC)

    def get_presentations(self):
        return self._db.get_aliases(_Group.VP)

    def get_credentials_by_did(self, alias):
        return self._db.get_credentials_by_did(alias)

    def get_nr(self, group):
        return self._db.get_nr(group)

    def get_nr_keys(self):
        return self._db.get_nr(_Group.KEY)

    def get_nr_dids(self):
        return self._db.get_nr(_Group.DID)

    def get_nr_credentials(self):
        return self._db.get_nr(_Group.VC)

    def get_nr_presentations(self):
        return self._db.get_nr(_Group.VP)

    def get_entry(self, alias, group):
        return self._db.get_entry(alias, group)

    def get_key(self, alias):
        return self._db.get_entry(alias, _Group.KEY)

    def get_did(self, alias):
        return self._db.get_entry(alias, _Group.DID)

    def get_credential(self, alias):
        return self._db.get_entry(alias, _Group.VC)

    def get_presentation(self, alias):
        return self._db.get_entry(alias, _Group.VP)

    def store_key(self, entry):
        alias = self._extract_alias_from_key(entry)
        return self._db.store_key(alias, entry)

    def store_did(self, entry):
        alias = self._extract_alias_from_did(entry)
        key = self._extract_key_from_did(entry)
        return self._db.store_did(alias, key, entry)

    def store_credential(self, entry):
        alias = self._extract_alias_from_vc(entry)
        holder = self._extract_holder_from_vc(entry)
        return self._db.store_vc(alias, holder, entry)

    def store_presentation(self, entry):
        alias = self._extract_alias_from_vp(entry)
        holder = self._extract_holder_from_vp(entry)
        return self._db.store_vp(alias, holder, entry)

    def remove(self, alias, group):
        self._db.remove(alias, group)

    def clear(self, group):
        self._db.clear(group)

    def clear_keys(self):
        self._db.clear(_Group.KEY)

    def clear_dids(self):
        self._db.clear(_Group.DID)

    def clear_credentials(self):
        self._db.clear(_Group.VC)

    def clear_presentations(self):
        self._db.clear(_Group.VP)

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

    def create_did(self, token, algo, onboard):
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

    def issue_credential(self, holder, template, content):
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

    def verify_presentation(self, vp):
        try:
            out = super().verify_presentation(vp)
        except SSIVerificationError as err:
            raise VerificationError(err)
        return out
