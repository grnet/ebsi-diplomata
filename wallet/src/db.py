from tinydb import TinyDB, where
from config import DBCONF, _Group
import json

_pkey = {
    _Group.KEY: 'kid',
    _Group.DID: 'id',
    _Group.VC:  'id',               # TODO
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

    def _get(self, pkey, group):
        filtered = self.db.table(group).search(where(
            _pkey[group])==pkey)
        if not filtered:
            return None
        out = json.loads(str(filtered[0]).replace('\'', '"'))
        return out

    def _get_nr(self, group):
        return len(self.db.table(group).all())

    def _get_all(self, group):
        return self.db.table(group).all()

    def _get_pkeys(self, group):
        return list(map(
            lambda x: x[_pkey[group]],
            self.db.table(group).all(),
        ))
 
    def _store(self, obj, group):
        self.db.table(group).insert(obj)

    def _remove(self, pkey, group):
        self.db.table(group).remove(where(
            _pkey[group])==pkey)
        
    def _clear(self, group):
        self.db.table(group).truncate()

    def get(self, pkey, group):
        return self._get(pkey, group)
 
    def get_nr(self, group):
        return self._get_nr(group)

    def get_all(self, group):
        return self._get_all(group)

    def get_pkeys(self, group):
        return self._get_pkeys(group)

    def store(self, obj, group):
        self._store(obj, group)

    def remove(self, pkey, group):
        self._remove(pkey, group)

    def clear(self, group):
        self._clear(group)
