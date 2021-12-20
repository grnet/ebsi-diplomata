import os
import json
import logging
from django.conf import settings
from ssi_lib import SSIApp
from ssi_lib import SSIGenerationError, SSIRegistrationError, \
    SSIResolutionError, SSIIssuanceError, SSIVerificationError
from ssi_lib.conf import Vc, Template


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

    def _fetch_key(self, *args):
        try:
            with open(self.keyfile, 'r') as f:
                out = json.load(f)
        except FileNotFoundError:
            return None
        return out

    def _fetch_did(self, full=False):
        try:
            with open(self.didfile, 'r') as f:
                did = json.load(f)
        except FileNotFoundError:
            return None
        out = self._extract_alias_from_did(did) if not full \
                else did
        return out

    def _store_key(self, entry):
        alias = self._extract_alias_from_key(entry)
        with open(self.keyfile, 'w+') as f:
            json.dump(entry, f, indent=4)
        return alias

    def _store_did(self, entry):
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
        alias = self._store_key(key)
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
        alias = self._store_did(did)
        return alias

    def _adapt_credential_content(self, vc_type, content):
        # TODO
        try:
            template = getattr(Template, vc_type)
        except AttributeError:
            err = 'Requested credential type does not exist: %s' % vc_type
            raise NotImplementedError(err)
        out = template
        match vc_type:
            case Vc.DIPLOMA:
                # TODO
                out['person_identifier'] = content['person_id']
                out['person_family_name'] = content['name']
                out['person_given_name'] = content['surname']
                out['awarding_opportunity_identifier'] = content['subject']
            case _:
                err = 'Requested credential type does not exist: %s' % vc_type
                raise NotImplementedError(err)
        return out

    def get_info(self):
        return {'TODO': 'Include here service info'}        # TODO

    def get_did(self):
        did = self._fetch_did(full=False)
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

    def issue_credential(self, holder, vc_type, content):
        issuer = self._fetch_did(full=False)
        if not issuer:
            err = 'No issuer DID found'
            raise IssuanceError(err)
        try:
            content = self._adapt_credential_content(vc_type, 
                    content)
        except NotImplementedError as err:
            raise IssuanceError(err)
        try:
            out = super().issue_credential(holder, issuer, vc_type,
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
