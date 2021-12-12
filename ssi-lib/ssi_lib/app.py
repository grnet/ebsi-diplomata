import json
import os
from .conf import _Group
from .db import DbConnector
from .walt import WaltWrapper


class SSIGenerationError(BaseException):
    pass

class SSICreationError(BaseException):
    pass

class SSIRegistrationError(BaseException):
    pass

class SSIResolutionError(BaseException):
    pass

class SSIApp(WaltWrapper):

    def __init__(self, dbpath, tmpdir):
        self._db = DbConnector(dbpath)
        self.tmpdir = tmpdir
        super().__init__(tmpdir)

    @classmethod
    def create(cls, config):
        dbpath = config['db']
        tmpdir = config['tmp']
        return cls(dbpath, tmpdir)

    def get_aliases(self, group):
        return self._db.get_aliases(group)

    def get_keys(self):
        return self._db.get_aliases(_Group.KEY)

    def get_dids(self):
        return self._db.get_aliases(_Group.DID)

    def get_credentials(self):
        return self._db.get_aliases(_Group.VC)

    def get_presentations(self):
        return self._db.get_aliases(_Group.VP)

    def get_credentials_by_did(self, alias):
        return self._db.get_credentials_by_did(alias)

    def get_nr(self, group):
        return self._db.get_nr(group)

    def get_nr_keys(self):
        return self._db.get_nr(_Group.KEY)

    def get_nr_dids(self):
        return self._db.get_nr(_Group.DID)

    def get_nr_credentials(self):
        return self._db.get_nr(_Group.VC)

    def get_nr_presentations(self):
        return self._db.get_nr(_Group.VP)

    def get_entry(self, alias, group):
        return self._db.get_entry(alias, group)

    def get_key(self, alias):
        return self._db.get_entry(alias, _Group.KEY)

    def get_did(self, alias):
        return self._db.get_entry(alias, _Group.DID)

    def get_credential(self, alias):
        return self._db.get_entry(alias, _Group.VC)

    def get_presentation(self, alias):
        return self._db.get_entry(alias, _Group.VP)

    def store(self, obj, group):
        self._db.store(obj, group)

    def store_key(self, obj):
        self._db.store(obj, _Group.KEY)

    def store_did(self, obj):
        self._db.store(obj, _Group.DID)

    def store_credential(self, obj):
        self._db.store(obj, _Group.VC)

    def store_presentation(self, obj):
        self._db.store(obj, _Group.VP)

    def remove(self, alias, group):
        self._db.remove(alias, group)

    def clear(self, group):
        self._db.clear(group)

    def clear_keys(self):
        self._db.clear(_Group.KEY)

    def clear_dids(self):
        self._db.clear(_Group.DID)

    def clear_credentials(self):
        self._db.clear(_Group.VC)

    def clear_presentations(self):
        self._db.clear(_Group.VP)

    def generate_key(self, algorithm):
        outfile = os.path.join(self.tmpdir, 'jwk.json')
        res, code = self._generate_key(algorithm, outfile)
        if code != 0:
            raise SSIGenerationError(res)
        with open(outfile, 'r') as f:
            out = json.load(f)
        os.remove(outfile)
        return out

    def generate_did(self, key, token, onboard=True):
        res, code = self._load_key(key)
        if code != 0:
            err = 'Could not load key: %s' % res
            raise SSIGenerationError(err)
        outfile = os.path.join(self.tmpdir, 'did.json')
        res, code = self._generate_did(key, outfile)
        if code != 0:
            raise SSIGenerationError(res)
        with open(outfile, 'r') as f:
            out = json.load(f)
        os.remove(outfile)
        return out

    def register_did(self, alias, token):
        if not token:
            err = 'No token provided'
            raise SSIRegistrationError(err)
        res, code = self._register_did(alias, token)
        if code != 0:
            raise SSIRegistrationError(res)

    def resolve_did(self, alias):
        res, code = self._resolve_did(alias)
        if code != 0:
            raise SSIResolutionError(res)

    def issue_credential(self, *args):
        raise NotImplementedError('TODO')

    def generate_presentation(self, holder_did, credentials, waltdir):
        res, code = self._generate_presentation(holder_did, credentials)
        if code != 0:
            raise SSIGenerationError(res)
        sep = 'Verifiable presentation was saved to file: '
        if not sep in res:
            raise SSIGenerationError(res)
        filename = res.split(sep)[-1].replace('"', '')
        outfile = os.path.join(waltdir, filename)
        with open(outfile, 'r') as f:
            out = json.load(f)
        os.remove(outfile)
        for tmpfile in credentials:
            os.remove(tmpfile)
        return out

    def verify_credentials(self, *args):
        raise NotImplementedError('TODO')