import cmd, sys
import requests
import json
import os
import subprocess
from tinydb import TinyDB

def run_cmd(args):
    result = subprocess.run(args, stdout=subprocess.PIPE)
    resp = result.stdout.decode('utf-8').rstrip('\n')
    code = result.returncode
    return (resp, code)

def create_db(path):
    return TinyDB(path, sort_keys=True, indent=4, separators=(',', ':'))

STORAGE = os.getenv('STORAGE')
TMPDIR  = os.path.join(STORAGE, 'tmp')

db = create_db(os.path.join(STORAGE, 'db.json'))
did_t = db.table('did')
vc_t = db.table('vc')

class WalletError(Exception):
    pass

def create_did():
    args = ['create-did',]
    _, code = run_cmd(args)
    with open(os.path.join(TMPDIR, 'created.json'), 'r') as f:
        created = json.load(f)
    did_t.insert(created)

def get_nr_dids():
    return len(did_t.all())

def load_did(nr):
    if not did_t.contains(doc_id=nr):
        err = "Requested DID not detected"
        raise WalletError(err)
    return did_t.get(doc_id=nr)

def load_last_did():
    return load_did(nr=get_nr_dids())

def get_did(nr, no_ebsi_prefix=False):
    out = load_did(nr)['id']
    if no_ebsi_prefix:
        out = out.lstrip(EBSI_PREFIX)
    return out

def get_last_did(**kw):
    return get_did(nr=get_nr_dids(), **kw)

def wallet_setup():
    if get_nr_dids() == 0:
        create_did()

wallet_setup()

class WalletShell(cmd.Cmd):
    intro = " * Type help or ? to list commands.\n"
    prompt = "(wallet) > "

    def preloop(self):
        print('\nStarted wallet session\n')

    def postloop(self):
        print('\nClosed wallet session\n')

    def do_info(self, line):
        """Show wallet info"""
        # did = load_last_did()
        # print(json.dumps(did, indent=2))
        did = get_last_did()
        print(did)

    def do_issue(self, line):
        """Request credentials issuance"""
        try:
            did = get_last_did()
        except WalletError as err:
            print(err)
        else:
            resp = requests.post('http://localhost:7000/api/vc', json={
                'did': did,
            })
            # TODO: Store credentials
            credential = resp.json()
            vc_t.insert(credential)
            # print(json.dumps(resp.json(), indent=2))

    def do_EOF(self, line):
        """Equivalent to exit."""
        return True

    def do_exit(self, line):
        """Close current wallet session."""
        return self.do_EOF(line)


if __name__ == '__main__':
    WalletShell().cmdloop()
