from ssi_lib.conf import _Group
from tinydb import TinyDB, where
import json
import os
from os.path import dirname
import sqlite3
from conf import SQL_DBNAME

_pkey = {
    _Group.KEY: 'kid',
    _Group.DID: 'id',
    _Group.VC:  'id',
    _Group.VP:  'id',
}

class WalletDbConnectionError(BaseException):
    pass

class WalletDbQueryError(BaseException):
    pass

def _get_init_script():
    rootdir = dirname(dirname(os.path.abspath(__file__)))   # TODO
    return os.path.join(rootdir, 'init-db.sql')


class DbConnector(object):

    def __init__(self, path):
        self.db = self._init_db(path)   # TODO: Get gradually rid of this
        # SQL
        script = _get_init_script()
        with open(script, 'r') as f:
            content = f.read()
        con = self._create_connection()
        cur = con.cursor()
        cur.executescript(content)
        con.close()

    @staticmethod 
    def _create_connection():
        try:
            con = sqlite3.connect(SQL_DBNAME)   # TODO
        except sqlite3.DatabaseError as err:
            raise WalletDbConectionError(err)
        return con

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
        _out = self._get_entry(alias, group)
        # SQL
        con = self._create_connection()
        cur = con.cursor()
        try:
            cur.execute(f'''
                SELECT
                    body
                FROM
                    '{group}'
                WHERE
                    alias = '{alias}'
            ''')
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)

        # TODO: Load and sort method
        body = cur.fetchone()[0]
        aux1 = json.loads(body)
        aux2 = json.dumps(aux1, sort_keys=True) # TODO
        out = json.loads(aux2)

        return out
 
    def get_nr(self, group):
        _out = self._get_nr(group)
        # SQL
        con = self._create_connection()
        cur = con.cursor()
        try:
            cur.execute(f'''
                SELECT
                    COUNT(*)
                FROM
                    '{group}'
            ''')
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        out = cur.fetchone()[0]
        return out

    def get_all(self, group):
        return self._get_all(group)

    def get_aliases(self, group):
        return self._get_aliases(group)

    def get_credentials_by_did(self, alias):
        return self._get_credentials_by_did(alias)

    def get_key_from_did(self, alias):
        return self._get_key_from_did(alias)

    def store(self, entry, group):
        alias = entry[_pkey[group]]
        self._store(entry, group)
        # SQL
        body = json.dumps(entry)
        con = self._create_connection()
        cur = con.cursor()
        try:
            cur.execute(f'''
                INSERT INTO
                    '{group}'(alias, body)
                VALUES
                    ('{alias}', '{body}')
            ''')
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        con.commit()
        return alias

    def remove(self, alias, group):
        self._remove(alias, group)
        # SQL
        con = self._create_connection()
        cur = con.cursor()
        try:
            cur.execute(f'''
                DELETE FROM
                    '{group}'
                WHERE
                    alias = '{alias}'
            ''')
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        con.commit()

    def clear(self, group):
        self._clear(group)
        # SQL
        con = self._create_connection()
        cur = con.cursor()
        try:
            cur.execute(f'''
                DELETE FROM
                    '{group}'
            ''')
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        con.commit()
