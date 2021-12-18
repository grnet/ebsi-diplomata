from ssi_lib.conf import _Group
from tinydb import TinyDB, where
import json

_pkey = {
    _Group.KEY: 'kid',
    _Group.DID: 'id',
    _Group.VC:  'id',
    _Group.VP:  'id',
}

class DbConnector(object):

    def __init__(self, path):
        self.db = self._init_db(path)

    @staticmethod
    def _init_db(path):
        db = TinyDB(path, **{
            'sort_keys': True,
            'indent': 4,
            'separators': [',', ': '],
        })
        for group in (_Group.KEY, _Group.DID, _Group.VC, _Group.VP):
            db.table(group)
        return db

    def _dump_dict(self, entry):
        return json.dumps(entry, sort_keys=True)

    def _load_dict(self, body):
        return json.loads(body)

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

    def _store(self, entry, group):
        self.db.table(group).insert(entry)

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

    def store_key(self, alias, entry):
        self._store(entry, _Group.KEY)
        return alias

    def store_did(self, alias, key, entry):
        self._store(entry, _Group.DID)
        return alias

    def store_vc(self, alias, holder, entry):
        self._store(entry, _Group.VC)
        return alias

    def store_vp(self, alias, holder, entry):
        self._store(entry, _Group.VP)
        return alias

    def remove(self, alias, group):
        self._remove(alias, group)

    def clear(self, group):
        self._clear(group)
