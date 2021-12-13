import json
import os
import subprocess
from .conf import _Group

def run_cmd(args):
    rslt = subprocess.run(args, stdout=subprocess.PIPE)
    resp = rslt.stdout.decode('utf-8').rstrip('\n')
    code = rslt.returncode
    return (resp, code)


class WaltWrapper(object):

    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def _generate_key(self, algorithm, outfile):
        res, code = run_cmd([
            'generate-key', '--algo', algorithm, '--export', outfile,
        ])
        return res, code

    def _load_key(self, alias):
        outfile = os.path.join(self.tmpdir, 'jwk.json')
        entry = self._db.get_entry(alias, _Group.KEY)
        with open(outfile, 'w+') as f:
            json.dump(entry, f)
        res, code = run_cmd(['load-key', '--file', outfile])
        os.remove(outfile)
        return res, code

    def _generate_did(self, key, outfile):
        res, code = run_cmd([
            'generate-did', '--key', key, '--export', outfile,
        ])
        return res, code

    def _register_did(self, alias, token):
        token_file = os.path.join(self.tmpdir, 'bearer-token.txt')
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

    def _issue_credential(self, holder_did, issuer_did, command, arguments,
            outfile):
        res, code = run_cmd([
            command,
            '--holder-did', holder_did,
            '--issuer-did', issuer_did,
            '--export', outfile,
            *arguments,
        ])
        return res, code

    def _generate_presentation(self, holder_did, credentials):
        args = ['present-credentials', '--holder-did', holder_did]
        for credential in credentials:
            args += ['-c', credential,]
        res, code = run_cmd(args)
        return res, code

    def _verify_credential(self, *args):
        raise NotImplementedError('TODO')
