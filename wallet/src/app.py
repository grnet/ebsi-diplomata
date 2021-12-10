import json
import os
import subprocess
from conf import STORAGE, TMPDIR, RESOLVED, DBNAME, INDENT, \
    _Group,  ED25519, SECP256, EBSI_PRFX
from db import DbConnector


def run_cmd(args):
    rslt = subprocess.run(args, stdout=subprocess.PIPE)
    resp = rslt.stdout.decode('utf-8').rstrip('\n')
    code = rslt.returncode
    return (resp, code)


class WaltWrapper(object):

    def _generate_key(self, algorithm, outfile):
        res, code = run_cmd([
            'generate-key', '--algo', algorithm, '--export', outfile,
        ])
        return res, code

    def _load_key(self, alias):
        outfile = os.path.join(TMPDIR, 'jwk.json')
        entry = self._db.get_entry(alias, _Group.KEY)
        with open(outfile, 'w+') as f:
            json.dump(entry, f, indent=INDENT)
        res, code = run_cmd(['load-key', '--file', outfile])
        os.remove(outfile)
        return res, code

    def _generate_did(self, key, outfile):
        res, code = run_cmd([
            'generate-did', '--key', key, '--export', outfile,
        ])
        return res, code

    def _register_did(self, alias, token):
        token_file = os.path.join(TMPDIR, 'bearer-token.txt')
        with open(token_file, 'w+') as f:
            f.write(token)
        res, code = run_cmd(['register-did', '--did', alias, 
            '--token', token_file, '--resolve',
        ])
        os.remove(token_file)
        return res, code

    def _resolve_did(self, alias):
        res, code = run_cmd(['resolve-did', '--did', alias,])
        return res, code

    def _retrieve_resolved_did(self, alias):
        resolved = os.path.join(RESOLVED, 'did-ebsi-%s.json' % \
            alias.lstrip(EBSI_PRFX))
        with open(resolved, 'r') as f:
            out = json.load(f)
        return out


class CreationError(BaseException):
    pass

class ResolutionError(BaseException):
    pass

class App(WaltWrapper):

    def __init__(self):
        self._db = DbConnector(os.path.join(STORAGE, DBNAME))

    @classmethod
    def create(cls):
        return cls()

    def get_aliases(self, group):
        return self._db.get_aliases(group)

    def get_keys(self):
        return self._db.get_aliases(_Group.KEY)

    def get_dids(self):
        return self._db.get_aliases(_Group.DID)

    def get_credentials(self):
        return self._db.get_aliases(_Group.VC)

    def get_credentials_by_did(self, alias):
        return self._db.get_credentials_by_did(alias)

    def get_nr(self, group):
        return self._db.get_nr(group)

    def get_entry(self, alias, group):
        return self._db.get_entry(alias, group)

    def get_key(self, alias):
        return self._db.get_entry(alias, _Group.KEY)

    def get_did(self, alias):
        return self._db.get_entry(alias, _Group.DID)

    def get_credential(self, alias):
        return self._db.get_entry(alias, _Group.VC)

    def store(self, obj, group):
        self._db.store(obj, group)

    def store_key(self, obj):
        self._db.store(obj, _Group.KEY)

    def store_did(self, obj):
        self._db.store(obj, _Group.DID)

    def store_credential(self, obj):
        self._db.store(obj, _Group.VC)

    def remove(self, alias, group):
        self._db.remove(alias, group)

    def clear(self, group):
        self._db.clear(group)

    def create_key(self, algorithm):
        outfile = os.path.join(TMPDIR, 'key.json')
        res, code = self._generate_key(algorithm, outfile)
        if code != 0:
            err = 'Could not generate key: %s' % res
            raise CreationError(err)
        with open(outfile, 'r') as f:
            created = json.load(f)
        self._db.store(created, _Group.KEY)
        os.remove(outfile)
        alias = created['kid']  # TODO
        return alias

    def create_did(self, key, token):
        res, code = self._load_key(key)
        if code != 0:
            err = 'Could not load key: %s' % res
            raise CreationError(err)
        outfile = os.path.join(TMPDIR, 'did.json')
        res, code = self._generate_did(key, outfile)
        if code != 0:
            err = 'Could not generate DID: %s' % res
            raise CreationError(err)
        with open(outfile, 'r') as f:
            created = json.load(f)
        os.remove(outfile)
        alias = created['id']       # TODO
        res, code = self._register_did(alias, token)
        if code != 0:
            err = 'Could not register DID: %s' % res
            raise CreationError(err)
        self._db.store(created, _Group.DID)
        return alias

    def resolve_did(self, alias):
        res, code = self._resolve_did(alias)
        if code != 0:
            err = 'Could not resolve: %s' % res
            raise ResolutionError(err)
        out = self._retrieve_resolved_did(alias)
        return out

    def create_verifiable_presentation(self, vc_files, did):
        # self.load_did(did)    # TODO
        # TODO: Trasfer part to walt-wrapper
        args = ['present-vc', '--holder-did', did,]
        for credential in vc_files:
            args += ['--credential', credential,]
        res, code = run_cmd(args)
        if code != 0:
            err = 'Could not present: %s' % res
            raise CreationError(err)
        # TODO: Where was it saved?
