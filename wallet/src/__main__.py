import cmd, sys
import json
import os
from ui import \
    launch_yes_no, \
    launch_input, \
    launch_number, \
    launch_single_choice, \
    launch_multiple_choices, \
    launch_prompt
from util import run_cmd, HttpClient
from config import STORAGE, TMPDIR, DBNAME, INTRO, PROMPT, \
    _Group, _Action, _UI
from db import DbConnector

# class WalletError(Exception):
#     pass

_mapping = {
    _UI.KEY: _Group.KEY,
    _UI.DID: _Group.DID,
    _UI.VC: _Group.VC,
    _UI.ISSUE: _Action.ISSUE,
    _UI.VERIFY: _Action.VERIFY,
    _UI.DISCARD: _Action.DISCARD,
}

class WalletShell(cmd.Cmd):
    intro   = INTRO
    prompt  = PROMPT

    def __init__(self):
        self._db = DbConnector(os.path.join(STORAGE, DBNAME))
        super().__init__()

    def create_did(self):
        args = ['create-did',]
        _, code = run_cmd(args)
        with open(os.path.join(TMPDIR, 'created.json'), 'r') as f:
            created = json.load(f)
        self._db.store(created, _Group.DID)

    # def get_did(nr, no_ebsi_prefix=False):
    #     out = load_did(nr)['id']
    #     if no_ebsi_prefix:
    #         out = out.lstrip(EBSI_PREFIX)
    #     return out

    def preloop(self):
        pass

    def postloop(self):
        pass

    def do_list(self, line):
        ans = launch_single_choice('Show list of', [
            _UI.KEY, _UI.DID, _UI.VC,
        ])
        entries = self._db.get_all(_mapping[ans])
        print(entries)

    def do_count(self, line):
        ans = launch_single_choice('Show number of', [
            _UI.KEY, _UI.DID, _UI.VC,
        ])
        group = _mapping[ans]
        nr = self._db.get_nr(group)
        print(nr)

    def do_inspect(self, line):
        ans = launch_single_choice('Type of object to inspect:', [
            _UI.KEY, _UI.DID, _UI.VC,
        ])
        match _mapping[ans]:
            case _Group.KEY:
                pass
            case _Group.DID:
                pass
            case _Group.VC:
                pass

    def do_create(self, line):
        ans = launch_single_choice('Type of object to create:', [
            _UI.KEY, _UI.DID,
        ])
        match _mapping[ans]:
            case _Group.KEY:
                pass
            case _Group.DID:
                self.create_did()

    def do_register(self, line):
        pass

    def do_resolve(self, line):
        pass

    def do_present(self, line):
        pass

    def do_request(self, line):
        action = launch_single_choice('Request', [
            _UI.ISSUE, _UI.VERIFY, _UI.DISCARD,
        ])
        match _mapping[action]:
            case _Action.ISSUE:
                pass
                # try:
                #     did = get_last_did()
                # except WalletError as err:
                #     print(err)
                # else:
                #     remote = 'http://localhost:7000'
                #     resp = HttpClient(remote).post('api/vc/', {
                #         'did': did
                #     })
                #     credential = resp.json()
                #     vc_t.insert(credential)
            case _Action.VERIFY:
                pass
            case _Action.DISCARD:
                pass

    def do_remove(self, line):
        ans = launch_single_choice('Type of object to remove:', [
            _UI.KEY, _UI.DID, _UI.VC,
        ])
        match _mapping[ans]:
            case _Group.KEY:
                pass
            case _Group.DID:
                pass
            case _Group.VC:
                pass

    def do_clear(self, line):
        ans = launch_single_choice('Choose group to clear:', [
            _UI.KEY, _UI.DID, _UI.VC,
        ])
        match _mapping[ans]:
            case _Group.KEY:
                pass
            case _Group.DID:
                pass
            case _Group.VC:
                pass

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
        """Equivalent to exit"""
        return True

    def do_exit(self, line):
        """Close current wallet session"""
        return self.do_EOF(line)


if __name__ == '__main__':
    WalletShell().cmdloop()
