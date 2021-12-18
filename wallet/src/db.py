from ssi_lib.conf import _Group
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

        # TODO: Load and sort method
        body = cur.fetchone()[0]
        aux1 = json.loads(body)
        aux2 = json.dumps(aux1, sort_keys=True) # TODO
        out = json.loads(aux2)

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
        return out

    def store(self, entry, group):
        alias = entry[_pkey[group]]
        body = json.dumps(entry)
        con = self._create_connection()
        cur = con.cursor()
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
