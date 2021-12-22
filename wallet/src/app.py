from ssi_lib import SSI, SSIGenerationError, SSIRegistrationError, \
    SSIResolutionError, SSIIssuanceError, SSIVerificationError
from conf import EBSI_PRFX, RESOLVED, WALTDIR, Table
from db import DbConnector


class CreationError(BaseException):
    pass

class RegistrationError(BaseException):
    pass

class ResolutionError(BaseException):
    pass

class IssuanceError(BaseException):
    pass

class VerificationError(BaseException):
    pass


class WalletApp(SSI):

    def __init__(self, tmpdir, dbpath):
        self._db = DbConnector(dbpath)
        super().__init__(tmpdir)
    
    @classmethod
    def create(cls, config):
        tmpdir = config['tmpdir']
        dbpath = config['dbpath']
        return cls(tmpdir, dbpath)

    def _fetch_key(self, alias):
        return self._db.fetch_entry(alias, Table.KEY)

    def fetch_aliases(self, table):
        return self._db.fetch_aliases(table)

    def fetch_keys(self):
        return self._db.fetch_aliases(Table.KEY)

    def fetch_dids(self):
        return self._db.fetch_aliases(Table.DID)

    def fetch_credentials(self):
        return self._db.fetch_aliases(Table.VC)

    def fetch_presentations(self):
        return self._db.fetch_aliases(Table.VP)

    def fetch_credentials_by_holder(self, alias):
        return self._db.fetch_credentials_by_holder(
            alias)

    def fetch_nr(self, table):
        return self._db.fetch_nr(table)

    def fetch_nr_keys(self):
        return self._db.fetch_nr(Table.KEY)

    def fetch_nr_dids(self):
        return self._db.fetch_nr(Table.DID)

    def fetch_nr_credentials(self):
        return self._db.fetch_nr(Table.VC)

    def fetch_nr_presentations(self):
        return self._db.fetch_nr(Table.VP)

    def fetch_entry(self, alias, table):
        return self._db.fetch_entry(alias, table)

    def fetch_key(self, alias):
        return self._fetch_key(alias)

    def fetch_did(self, alias):
        return self._db.fetch_entry(alias, Table.DID)

    def fetch_credential(self, alias):
        return self._db.fetch_entry(alias, Table.VC)

    def fetch_presentation(self, alias):
        return self._db.fetch_entry(alias, Table.VP)

    def store_key(self, entry):
        alias = self.extract_alias_from_key(entry)
        return self._db.store_key(alias, entry)

    def store_did(self, entry):
        alias = self.extract_alias_from_did(entry)
        key = self.extract_key_from_did(entry)
        return self._db.store_did(alias, key, entry)

    def store_credential(self, entry):
        alias = self.extract_alias_from_vc(entry)
        holder = self.extract_holder_from_vc(entry)
        return self._db.store_vc(alias, holder, entry)

    def store_presentation(self, entry):
        alias = self.extract_alias_from_vp(entry)
        holder = self.extract_holder_from_vp(entry)
        return self._db.store_vp(alias, holder, entry)

    def remove(self, alias, table):
        self._db.remove(alias, table)

    def clear(self, table):
        self._db.clear(table)

    def clear_keys(self):
        self._db.clear(Table.KEY)

    def clear_dids(self):
        self._db.clear(Table.DID)

    def clear_credentials(self):
        self._db.clear(Table.VC)

    def clear_presentations(self):
        self._db.clear(Table.VP)

    def create_key(self, algo):
        try:
            key = self.generate_key(algo)
        except SSIGenerationError as err:
            err = 'Could not generate key: %s' % err
            raise CreationError(err)
        alias = self.store_key(key)
        return alias

    def register_did(self, alias, token):
        try:
            super().register_did(alias, token)
        except SSIRegistrationError as err:
            raise RegistrationError(err)

    def resolve_did(self, alias):
        try:
            super().resolve_did(alias)
        except SSIResolutionError as err:
            raise ResolutionError(err)

    def create_did(self, key, token, onboard=True):
        try:
            did = self.generate_did(key, token, onboard)
        except SSIGenerationError as err:
            err = 'Could not generate DID: %s' % err
            raise CreationError(err)
        if onboard:
            try:
                alias = self.extract_alias_from_did(did)
                super().register_did(alias, token)
            except SSIRegistrationError as err:
                err = 'Could not register: %s' % err
                raise CreationError(err)
        alias = self.store_did(did)
        return alias

    def retrieve_resolved_did(self, alias):
        resolved = os.path.join(RESOLVED, 'did-ebsi-%s.json' % \
            alias.lstrip(EBSI_PRFX))
        with open(resolved, 'r') as f:
            did = json.load(f)
        return did

    def issue_credential(self, holder, issuer, vc_type, content):
        try:
            vc = super().issue_credential(holder, issuer, vc_type,
                    content)
        except SSIIssuanceError as err:
            raise IssuanceError(err)
        return vc

    def create_presentation(self, holder, credentials,
            waltdir=WALTDIR):
        try:
            vp = self.generate_presentation(holder, credentials,
                    waltdir)
        except SSIGenerationError as err:
            err = 'Could not generate presentation: %s' % err
            raise CreationError(err)
        alias = self.store_presentation(vp)
        return alias

    def verify_presentation(self, vp):
        try:
            results = super().verify_presentation(vp)
        except SSIVerificationError as err:
            raise VerificationError(err)
        return results
