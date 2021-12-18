import sqlite3
import json
from ssi_lib.conf import _Group

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


class DbConnector(object):

    def __init__(self, db):
        self._run_sql_script(db, self._get_init_script())
        self.db = db

    def _create_connection(self, db=None):
        if not db: 
            db = self.db
        try:
            con = sqlite3.connect(db)
        except sqlite3.DatabaseError as err:
            raise WalletDbConectionError(err)
        return con

    @staticmethod
    def _get_init_script():
        from os.path import dirname
        import os
        rootdir = dirname(dirname(os.path.abspath(
            __file__)))
        return os.path.join(rootdir, 'init-db.sql')

    def _run_sql_script(self, db, script):
        con = self._create_connection(db)
        cur = con.cursor()
        with open(script, 'r') as f:
            sql = f.read()
        cur.executescript(sql)
        con.close()

    def _dump_dict(self, entry):
        return json.dumps(entry, sort_keys=True)

    def _load_dict(self, body):
        return json.loads(body)

    def get_entry(self, alias, group):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            SELECT body FROM '{group}' WHERE alias = '{alias}'
        '''
        try:
            cur.execute(query)
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        body = cur.fetchone()[0]
        con.close()
        out = self._load_dict(body)
        return out
 
    def get_nr(self, group):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            SELECT COUNT(*) FROM '{group}'
        '''
        try:
            cur.execute(query)
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        out = cur.fetchone()[0]
        con.close()
        return out

    def get_aliases(self, group):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            SELECT alias FROM '{group}'
        '''
        try:
            cur.execute(query)
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        out = list(map(lambda _: _[0], cur.fetchall()))
        con.close()
        return out

    def get_credentials_by_did(self, alias):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            SELECT alias FROM vc WHERE holder = '{alias}'
        '''
        try:
            cur.execute(query)
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        out = list(map(lambda _: _[0], cur.fetchall()))
        con.close()
        return out

    def store(self, entry, group):
        con = self._create_connection()
        cur = con.cursor()
        alias = entry[_pkey[group]]
        body = self._dump_dict(entry)
        match group:
            case _Group.KEY:
                query = f'''
                    INSERT INTO '{group}'(alias, body)
                    VALUES ('{alias}', '{body}')
                '''
            case _Group.DID:
                key = entry['verificationMethod'][0]['publicKeyJwk']['kid'] # TODO
                query = f'''
                    INSERT INTO '{group}'(key, alias, body)
                    VALUES ('{key}', '{alias}', '{body}')
                '''
            case _Group.VC:
                holder = entry['credentialSubject']['id']                   # TODO
                query = f'''
                    INSERT INTO '{group}'(holder, alias, body)
                    VALUES ('{holder}', '{alias}', '{body}')
                '''
            case _Group.VP:
                holder = entry['holder']                                    # TODO
                query = f'''
                    INSERT INTO '{group}'(holder, alias, body)
                    VALUES ('{holder}', '{alias}', '{body}')
                '''
        try:
            cur.execute(query)
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        con.commit()
        con.close()
        return alias

    def remove(self, alias, group):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            DELETE FROM '{group}' WHERE alias = '{alias}'
        '''
        try:
            cur.execute(query)
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        con.commit()
        con.close()

    def clear(self, group):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            DELETE FROM '{group}'
        '''
        try:
            cur.execute(query)
        except sqlite3.DatabaseError as err:
            raise WalletDbQueryError(err)
        con.commit()
        con.close()
