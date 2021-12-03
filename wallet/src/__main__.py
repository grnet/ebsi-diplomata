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
from config import STORAGE, TMPDIR, DBNAME, INTRO, PROMPT, INDENT, \
    _Group, _Action, _UI, ED25519, SECP256
from db import DbConnector

# TODO
_mapping = {
    _UI.KEY: _Group.KEY,
    _UI.KEYS: _Group.KEY,
    _UI.DID: _Group.DID,
    _UI.DIDS: _Group.DID,
    _UI.VC: _Group.VC,
    _UI.VCS: _Group.VC,
    _UI.ISSUE: _Action.ISSUE,
    _UI.VERIFY: _Action.VERIFY,
    _UI.DISCARD: _Action.DISCARD,
}

class BadInputError(BaseException):
    pass

class WalletShell(cmd.Cmd):
    intro   = INTRO
    prompt  = PROMPT

    def __init__(self):
        self._db = DbConnector(os.path.join(STORAGE, DBNAME))
        super().__init__()

    def create_key(self):
        # TODO
        outfile = os.path.join(TMPDIR, 'created.json')
        args = ['create-key', '--export', outfile]
        _, code = run_cmd(args)
        with open(outfile, 'r') as f:
            created = json.load(f)
        self._db.store(created, _Group.KEY)

    def create_did(self):
        # TODO
        outfile = os.path.join(TMPDIR, 'created.json')
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

    def flush(self, buff):
        if type(buff) in (dict, list,):
            buff = json.dumps(buff, indent=INDENT)
        else:
            buff = str(buff)
        sys.stdout.write(buff + '\n')

    def show_list(self, lst):
        for _ in lst:
            self.flush(_)

    def _adjust_line(self, line):
        return line.strip().lower().rstrip('s')

    def _resolve_group(self, line, prompt):
        aux = self._adjust_line(line)
        match aux:
            case '':
                ans = launch_single_choice(prompt, [
                    _UI.KEYS, 
                    _UI.DIDS, 
                    _UI.VCS,
                ])
                out = _mapping[ans]
            case (
                    _UI.KEY |
                    _UI.DID |
                    _UI.VC
                ):
                out = _mapping[aux]
            case (
                    _Group.KEY |
                    _Group.DID |
                    _Group.VC
                ):
                out = aux
            case _:
                err = "Bad input: %s" % line
                raise BadInputError(err)
        return out

    def do_list(self, line):
        try:
            group = self._resolve_group(line, prompt='Show list of')
        except BadInputError as err:
            self.flush(err)
        else:
            out = self._db.get_all_ids(group)
            self.show_list(out)

    def do_count(self, line):
        try:
            group = self._resolve_group(line, prompt='Show number of')
        except BadInputError as err:
            self.flush(err)
        else:
            out = self._db.get_nr(group)
            self.flush(out)

    def do_inspect(self, line):
        try:
            group = self._resolve_group(line, prompt='Inspect')
        except BadInputError as err:
            self.flush(err)
        else:
            ids = self._db.get_all_ids(group)
            if not ids:
                self.flush('Nothing found')
            else:
                ans = launch_single_choice('Choose', ids)
                out = self._db.get(ans, group)  # TODO: Handle None?
                self.flush(out)

    def do_create(self, line):
        ans = launch_single_choice('Type of object to create:', [
            _UI.KEY, 
            _UI.DID,
        ])
        match _mapping[ans]:
            case _Group.KEY:
                # answers = launch_prompt({
                #     'input': 'Give a name:',
                #     'single': {
                #         'prompt': 'Choose keygen algorithm: ',
                #         'choices': [
                #             ED25519,
                #             SECP256
                #         ],
                #     },
                #     'yes_no': 'Key will be saved to disk. Proceed?'
                # })
                # proceed = answers[-1]
                # if not proceed: 
                #     self.flush('Key generation aborted')
                # else:
                #     params = {
                #         'name': answers[0],
                #         'algo': answers[1],
                #     }
                #     self.flush(params)
                self.create_key()
            case _Group.DID:
                # answers = launch_prompt({
                #     'single': {
                #         'prompt': 'Choose key: ',
                #         'choices': [
                #             'watermelon',
                #             # put non-empty list of keys here
                #         ],
                #     },
                # })
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
                # except BadInputError as err:
                #     self.flush(err)
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
        try:
            group = self._resolve_group(line, prompt='Clear')
        except BadInputError as err:
            self.flush('Could not list: %s' % err)
        else:
            msg = 'Are you sure? This cannot be undone.'
            yes = launch_yes_no(msg)
            if yes:
                self._db.clear(group)
                self.flush('Cleared')
            else:
                self.flush('Aborted')

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
        self.flush(results)

    def do_EOF(self, line):
        """Equivalent to exit"""
        return True

    def do_exit(self, line):
        """Close current wallet session"""
        return self.do_EOF(line)


if __name__ == '__main__':
    WalletShell().cmdloop()

