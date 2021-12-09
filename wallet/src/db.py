from tinydb import TinyDB, where
from conf import DBCONF, _Group
import json

_pkey = {
    _Group.KEY: 'kid',
    _Group.DID: 'id',
    _Group.VC:  'id',
}

class DbConnector(object):

    def __init__(self, path):
        self.db = self._init_db(path)

    @staticmethod
    def _init_db(path):
        db = TinyDB(path, **DBCONF)
        for group in (_Group.KEY, _Group.DID, _Group.VC):
            db.table(group)
        return db

    def _get_entry(self, alias, group):
        filtered = self.db.table(group).search(
            where(_pkey[group])==alias)
        if not filtered:
            return None
        out = json.loads(str(filtered[0]).replace('\'', '"'))
        return out

    def _get_nr(self, group):
        return len(self.db.table(group).all())

    def _get_all(self, group):
        return self.db.table(group).all()

    def _get_aliases(self, group):
        return list(map(
            lambda x: x[_pkey[group]],
            self.db.table(group).all(),
        ))

    def _get_credentials_by_did(self, alias):
        filtered = self.db.table(_Group.VC).search(
            where('credentialSubject')['id']==alias)
        out = list(map(
            lambda x: x['id'],
            filtered,
        ))
        return out

    def _get_key_from_did(self, alias):
        did = self._get(alias, _Group.DID)
        if did:
            return did['verificationMethod'][0]['publicKeyJwk']['kid']
 
    def _store(self, obj, group):
        self.db.table(group).insert(obj)

    def _remove(self, alias, group):
        self.db.table(group).remove(where(
            _pkey[group])==alias)
        
    def _clear(self, group):
        self.db.table(group).truncate()

    def get_entry(self, alias, group):
        return self._get_entry(alias, group)
 
    def get_nr(self, group):
        return self._get_nr(group)

    def get_all(self, group):
        return self._get_all(group)

    def get_aliases(self, group):
        return self._get_aliases(group)

    def get_credentials_by_did(self, alias):
        return self._get_credentials_by_did(alias)

    def get_key_from_did(self, alias):
        return self._get_key_from_did(alias)

    def store(self, obj, group):
        self._store(obj, group)

    def remove(self, alias, group):
        self._remove(alias, group)

    def clear(self, group):
        self._clear(group)
