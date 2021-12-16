from ssi_lib import SSIApp
from ssi_lib.conf import _Group
from db import DbConnector


class WalletApp(SSIApp):

    def __init__(self, dbpath, tmpdir):
        self._db = DbConnector(dbpath)
        super().__init__(tmpdir)
    
    @classmethod
    def create(cls, config):
        dbpath = config['db']
        tmpdir = config['tmp']
        return cls(dbpath, tmpdir)

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

    def store(self, obj, group):
        return self._db.store(obj, group)

    def store_key(self, obj):
        return self._db.store(obj, _Group.KEY)

    def store_did(self, obj):
        return self._db.store(obj, _Group.DID)

    def store_credential(self, obj):
        return self._db.store(obj, _Group.VC)

    def store_presentation(self, obj):
        return self._db.store(obj, _Group.VP)

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
