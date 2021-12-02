from tinydb import TinyDB
from config import DBCONF, _Group


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
        return self.db.table(group).get(doc_id=pkey)

    def _get_nr(self, group):
        return len(self.db.table(group).all())

    def _get_all(self, group):
        return self.db.table(group).all()
 
    def _store(self, payload, group):
        self.db.table(group).insert(payload)
        
    def _exists(self, pkey, group):
        return self.db.table(group).contains(doc_id=pkey)

    def get(self, pkey, group):
        return self._get(pkey, group)
 
    def get_nr(self, group):
        return self._get_nr(group)

    def get_all(self, group):
        return self._get_all(group)

    def store(self, payload, group):
        self._store(payload, group)

    def exists(self, pkey, group):
        return exists(pkey, group)
