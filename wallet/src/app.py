from ssi_lib import SSIApp
from ssi_lib.conf import _Group
from db import DbConnector


class WalletApp(SSIApp):

    def __init__(self, tmpdir, dbpath):
        self._db = DbConnector(dbpath)
        super().__init__(tmpdir)
    
    @classmethod
    def create(cls, config):
        tmpdir = config['tmpdir']
        dbpath = config['dbpath']
        return cls(tmpdir, dbpath)

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
