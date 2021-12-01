import cmd, sys
import json
import os
from tinydb import TinyDB
from ui import \
    launch_yes_no, \
    launch_input, \
    launch_number, \
    launch_single_choice, \
    launch_multiple_choices, \
    launch_prompt
from util import run_cmd, HttpClient
from config import STORAGE, TMPDIR

def init_db(path):
    db = TinyDB(
        path, 
        sort_keys=True, 
        indent=4,
        separators=(',', ': ')
    )
    db.table('key')
    db.table('did')
    db.table('vc')
    return db

def get_table(db, name):
    return db.table(name)

db = init_db(os.path.join(STORAGE, 'db.json'))
key_t = get_table(db, 'key')
did_t = get_table(db, 'did')
vc_t  = get_table(db, 'vc')

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
    prompt = "[ebsi-wallet] >> "

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

    def do_create(self, line):
        create_did()
        did = get_last_did()
        print(did)

    def do_issue(self, line):
        """Request credentials issuance"""
        try:
            did = get_last_did()
        except WalletError as err:
            print(err)
        else:
            remote = 'http://localhost:7000'
            resp = HttpClient(remote).post('api/vc/', {
                'did': did
            })
            credential = resp.json()
            vc_t.insert(credential)

    def do_choose(self, line):
        result = launch_single_choice('Choose a fruit', [
            'apple',
            'banana', 
            'orange', 
            'watermelon',
            'discard',
        ])
        if result[0] != 'discard':
            print("You chose:", result)

    def do_check(self, line):
        result = launch_multiple_choices('Choose fruits', [
            'apple',
            'banana', 
            'orange', 
            'watermelon',
        ])
        print('You chose:', result)

    def do_prompt(self, line):
        results = launch_prompt({
            'yes_no': 'Yes or no?',
            'input': 'Give anything',
            'number': 'Enter the beast (666):',
            'single': {
                'prompt': 'Choose language: ',
                'choices': [
                    "python", 
                    "js", 
                    "rust",
                ],
            },
            'multiple': {
                'prompt': 'Choose fruits with space:',
                'choices': [
                    "apple", 
                    "banana", 
                    "orange", 
                    "watermelon"
                ],
            },
        })
        print(results)

    def do_EOF(self, line):
        """Equivalent to exit."""
        return True

    def do_exit(self, line):
        """Close current wallet session."""
        return self.do_EOF(line)


if __name__ == '__main__':
    WalletShell().cmdloop()
