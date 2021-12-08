import json
import os
from .util import run_cmd
from .conf import STORAGE, TMPDIR, RESOLVED, DBNAME, INDENT, \
    _Group,  ED25519, SECP256, EBSI_PRFX
from .db import DbConnector


class CreationError(BaseException):
    pass

class LoadError(BaseException):
    pass

class RegistrationError(BaseException):
    pass

class ResolutionError(BaseException):
    pass


class App(object):

    def __init__(self):
        self._db = DbConnector(os.path.join(STORAGE, DBNAME))

    @classmethod
    def create(cls):
        return cls()

    def get_aliases(self, group):
        return self._db.get_aliases(group)

    def get_nr(self, group):
        return self._db.get_nr(group)

    def get_entry(self, alias, group):
        return self._db.get_entry(alias, group)

    def get_vcs_by_did(self, alias):
        return self._db.get_vcs_by_did(alias)

    def store(self, obj, group):
        self._db.store(obj, group)

    def remove(self, alias, group):
        self._db.remove(alias, group)

    def clear(self, group):
        self._db.clear(group)

    def create_key(self, algorithm):
        tmpfile = os.path.join(TMPDIR, 'key.json')
        res, code = run_cmd([
            'create-key', '--algo', algorithm, '--export', tmpfile
        ])
        if code != 0:
            err = 'Could not generate key: %s' % res
            raise CreationError(err)
        with open(tmpfile, 'r') as f:
            created = json.load(f)
        self._db.store(created, _Group.KEY)
        os.remove(tmpfile)
        alias = created['kid']  # TODO
        return alias

    def load_key(self, key):
        tmpfile = os.path.join(TMPDIR, 'jwk.json')
        entry = self._db.get_entry(key, _Group.KEY)
        with open(tmpfile, 'w+') as f:
            json.dump(entry, f, indent=INDENT)
        res, code = run_cmd(['load-key', '--file', tmpfile])
        if code != 0:
            err = 'Could not load key: %s' % res
            raise LoadError(err)
        os.remove(tmpfile)

    def register_did(self, did, token):
        token_file = os.path.join(TMPDIR, 'bearer-token.txt')
        with open(token_file, 'w+') as f:
            f.write(token)
        res, code = run_cmd(['register-did',
            '--did', did, '--token', token_file,
            '--resolve',])
        if code != 0:
            err = 'Could not register: %s' % res
            raise RegistrationError(err)
        os.remove(token_file)

    def create_did(self, key, token):
        try:
            self.load_key(key)
        except LoadError as err:
            err = 'Could not create DID: %s' % err
            raise CreationError(err)
        tmpfile = os.path.join(TMPDIR, 'did.json')
        res, code = run_cmd([
            'create-did', '--key', key, '--export', tmpfile
        ])
        if code != 0:
            err = 'Could not create DID: %s' % res
            raise CreationError(err)
        with open(tmpfile, 'r') as f:
            created = json.load(f)
        alias = created['id']       # TODO
        try:
            self.register_did(alias, token)
        except RegistrationError as err:
            raise CreationError(err)
        self._db.store(created, _Group.DID)
        os.remove(tmpfile)
        return alias

    def resolve_did(self, alias):
        res, code = run_cmd(['resolve-did', '--did', alias,])
        if code != 0:
            err = res
            raise ResolutionError(err)
        resolved = os.path.join(RESOLVED, 'did-ebsi-%s.json' % \
            alias.lstrip(EBSI_PRFX))
        with open(resolved) as f:
            out = json.load(f)
        return out

    def create_verifiable_presentation(self, vc_files, did):
        # key = self._db.get_key_from_did(did)
        # try:
        #     self.load_key(key)
        # except LoadError as err:
        #     err = 'Could not create vp: %s' % err
        #     raise CreationError(err)
        args = ['present-vc', '--holder-did', did,]
        for credential in vc_files:
            args += ['--credential', credential,]
        res, code = run_cmd(args)
        if code != 0:
            err = 'Could not present: %s' % res
            raise CreationError(err)
        # TODO: Where was it saved?
