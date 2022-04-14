"""Interface for making SQL queries to any database whose schema is defined by
../init-db.sql. Rough overview:

    key | alias(VARCHAR) | body(JSONB)
    did | alias(VARCHAR) | body(JSONB) | key(VARCHAR)    [fk to key(alias)]
    vc  | alias(VARCHAR) | body(JSONB) | holder(VARCHAR) [fk to did(alias)]
    vp  | alias(VARCHAR) | body(JSONB) | holder(VARCHAR) [fk to did(alias)]

We should here be able to import and use any ORM library conforming to the
DB API 2.0 protocol (PEP 249 spec v2.0), e.g., psycopg for connecting to a
postgres database instead of sqlite.
"""

import sqlite3 as _orm
import json


class DbConnectionError(Exception):
    pass


class DbQueryError(Exception):
    pass


class DbConnector(object):

    def __init__(self, db):
        self._run_sql_script(db, self._get_init_script())
        self.db = db

    def _create_connection(self, db=None):
        if not db:
            db = self.db
        try:
            con = _orm.connect(db)
        except _orm.DatabaseError as err:
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
        # TODO: The present module is agnostic to the ORM in use with the
        # exception of this function (executescript is sqlite spcific).
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

    def fetch_entry(self, alias, table):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            SELECT body FROM '{table}' WHERE alias = '{alias}'
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        body = cur.fetchone()[0]
        con.close()
        out = self._load_dict(body)
        return out

    def fetch_nr(self, table):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            SELECT COUNT(*) FROM '{table}'
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        out = cur.fetchone()[0]
        con.close()
        return out

    def fetch_aliases(self, table):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            SELECT alias FROM '{table}'
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        out = list(map(lambda _: _[0], cur.fetchall()))
        con.close()
        return out

    def fetch_credentials_by_holder(self, alias):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            SELECT alias FROM vc WHERE holder = '{alias}'
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        out = list(map(lambda _: _[0], cur.fetchall()))
        con.close()
        return out

    def store_key(self, alias, entry):
        con = self._create_connection()
        cur = con.cursor()
        body = self._dump_dict(entry)
        query = f'''
            INSERT INTO key(alias, body)
            VALUES ('{alias}', '{body}')
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        con.commit()
        con.close()
        return alias

    def store_did(self, alias, key, entry):
        con = self._create_connection()
        cur = con.cursor()
        body = self._dump_dict(entry)
        query = f'''
            INSERT INTO did(key, alias, body)
            VALUES ('{key}', '{alias}', '{body}')
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        con.commit()
        con.close()
        return alias

    def store_vc(self, alias, holder, entry):
        con = self._create_connection()
        cur = con.cursor()
        body = self._dump_dict(entry)
        query = f'''
            INSERT INTO vc(holder, alias, body)
            VALUES ('{holder}', '{alias}', '{body}')
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        con.commit()
        con.close()
        return alias

    def store_vp(self, alias, holder, entry):
        con = self._create_connection()
        cur = con.cursor()
        body = self._dump_dict(entry)
        query = f'''
            INSERT INTO vp(holder, alias, body)
            VALUES ('{holder}', '{alias}', '{body}')
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        con.commit()
        con.close()
        return alias

    def remove(self, alias, table):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            DELETE FROM '{table}' WHERE alias = '{alias}'
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        con.commit()
        con.close()

    def clear(self, table):
        con = self._create_connection()
        cur = con.cursor()
        query = f'''
            DELETE FROM '{table}'
        '''
        try:
            cur.execute(query)
        except _orm.DatabaseError as err:
            raise DbQueryError(err)
        con.commit()
        con.close()
