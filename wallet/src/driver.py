import cmd, sys
import json
import os
from ui import MenuHandler
from util import HttpClient
from conf import STORAGE, TMPDIR, DBNAME, INTRO, PROMPT, INDENT, \
    _Group, _Action, _UI, ED25519, SECP256
from app import LoadError, CreationError, RegistrationError, \
    ResolutionError

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

__version__ = '0.0.1'

class BadInputError(BaseException):
    pass


class WalletShell(cmd.Cmd, MenuHandler):
    intro   = INTRO.format(__version__)
    prompt  = PROMPT

    def __init__(self, app):
        self.app = app
        super().__init__()

    def _flush(self, buff):
        if type(buff) in (dict, list,):
            buff = json.dumps(buff, indent=INDENT)
        else:
            buff = str(buff)
        sys.stdout.write(buff + '\n')

    def _flush_list(self, lst):
        for _ in lst: self._flush(_)

    def _flush_help(self, *messages):
        self._flush('\n'.join(messages))

    def _normalize_input(self, line):
        return line.strip().lower().rstrip('s')

    def _resolve_group(self, line, prompt):
        aux = self._normalize_input(line)
        match aux:
            case '':
                ans = self.launch_single_choice(prompt, [
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
                err = 'Bad input: %s' % line
                raise BadInputError(err)
        return out

    def run(self):
        super().cmdloop()

    def preloop(self):
        pass

    def postloop(self):
        pass

    def do_list(self, line):
        try:
            group = self._resolve_group(line, prompt='Show list of')
        except BadInputError as err:
            self._flush(err)
            return
        entries = self.app.get_aliases(group)
        if not entries:
            self._flush('Nothing found')
            return
        self._flush_list(entries)

    def do_count(self, line):
        try:
            group = self._resolve_group(line, prompt='Show number of')
        except BadInputError as err:
            self._flush(err)
            return
        nr = self.app.get_nr(group)
        self._flush(nr)

    def do_inspect(self, line):
        try:
            group = self._resolve_group(line, prompt='Inspect from')
        except BadInputError as err:
            self._flush(err)
            return
        aliases = self.app.get_aliases(group)
        if not aliases:
            self._flush('Nothing found')
            return
        alias = self.launch_single_choice('Choose', aliases)
        entry = self.app.get(alias, group)
        self._flush(entry)

    def do_create(self, line):
        ans = self.launch_single_choice('Create', [
            _UI.KEY, 
            _UI.DID,
        ])
        match _mapping[ans]:
            case _Group.KEY:
                answers = self.launch_prompt({
                    'single': {
                        'prompt': 'Choose keygen algorithm: ',
                        'choices': [
                            ED25519,
                            SECP256
                        ],
                    },
                    'yes_no': 'A new key will be saved to disk. Proceed?',
                })
                algorithm, proceed = answers
                if not proceed: 
                    self._flush('Key generation aborted')
                    return
                self._flush('Creating %s key (takes seconds) ...' \
                    % algorithm)
                try:
                    alias = self.app.create_key(algorithm)
                except CreationError as err:
                    self._flush(err)
                    return
                self._flush('Created key: %s' % alias)
            case _Group.DID:
                keys = self.app.get_aliases(_Group.KEY)
                if not keys:
                    self._flush('No keys found. Must first create one.')
                    return
                answers = self.launch_prompt({
                    'single': {
                        'prompt': 'Choose key:',
                        'choices': keys
                    },
                    'input': 'Token: ',
                    'yes_no': 'A new DID will be saved to disk. Proceed?',
                })
                key, token, proceed = answers
                if not proceed: 
                    self._flush('DID generation aborted')
                    return
                self._flush('Creating DID (takes seconds) ...')
                try:
                    alias = self.app.create_did(key, token)
                except CreationError as err:
                    self._flush(err)
                    return
                self._flush('Created DID: %s' % alias)

    def do_resolve(self, line):
        alias = self.launch_input('Give DID:')
        self._flush('Resolving ...')
        try:
            did = self.app.resolve_did(alias)
        except ResolutionError as err:
            self._flush('Cound not resolve: %s' % err)
            return
        self._flush(did)

    def do_present(self, line):
        pass

    def do_request(self, line):
        action = self.launch_single_choice('Request', [
            _UI.ISSUE, 
            _UI.VERIFY, 
            _UI.DISCARD,
        ])
        match _mapping[action]:
            case _Action.ISSUE:
                choices = self.app.get_aliases(_Group.DID)
                if not choices:
                    self._flush('No DIDs found. Must first create one.')
                    return
                did = self.launch_single_choice('Choose DID', choices)
                # TODO: Choose from known registar of issuers?
                remote = 'http://localhost:7000'
                endpoint = 'api/vc/'
                # TODO: Construction of payload presupposes that an API
                # spec is known on behalf of the issuer
                payload = {
                    'did': did,
                    # TODO: Provide more info, e.g. name, diploma etc.
                }
                # TODO: Handle connection errors and timeouts
                resp = HttpClient(remote).post(endpoint, payload)
                # TODO: Check that a credential is indeed returned. This
                # presupposes that an API spec on behalf of the issuer is
                # known
                credential = resp.json()
                self.app.store(credential, _Group.VC)
                self._flush('The following credential was saved to disk:')
                self._flush(credential['id'])
            case _Action.VERIFY:
                # choices = self.app.get_aliases(_Group.VC)
                # if not choices:
                #     self._flush('No credentials found')
                #     return
                # alias = self.launch_single_choice('Choose credential', 
                #     choices)
                # credential = self.app.get(alias, _Group.VC)
                # # TODO: Choose from known registar of verifiers?
                # remote = 'http://localhost:7001'
                # endpoint = 'api/vc/'
                # # TODO: Construction of payload presupposes that an API
                # # spec is known on behalf of the verifier
                # payload = {
                #     'credential': credential,
                # }
                # resp = HttpClient(remote).post(endpoint, payload)
                # # TODO
                # self._flush(resp.json())
                did_choices = self.app.get_aliases(_Group.DID)
                if not did_choices:
                    self._flush('No DIDs found. Must create at least one.')
                    return
                did = self.launch_single_choice('Choose DID', did_choices)
                vc_choices = self.app.get_vcs_by_did(did)
                if not vc_choices:
                    self._flush('No credentials found for the provided DID')
                    return
                selected = self.launch_multiple_choices(
                    'Select credentials to present', vc_choices)
                credentials = [self.app.get(alias, _Group.VC) for alias
                    in selected]
                if not credentials:
                    self._flush('Aborted')
                    return
                vc_files = []
                for c in credentials:
                    tmpfile = os.path.join(TMPDIR, '%s.json' \
                        % c['id'])
                    with open(tmpfile, 'w+') as f:
                        json.dump(c, f, indent=INDENT)
                    vc_files += [tmpfile,]
                try:
                    vp = self.app.create_verifiable_presentation(vc_files, 
                            did)
                except CreationError as err:
                    self._flush(err)
                    return
                pass    # TODO
                #
                #
                #
                import pdb; pdb.set_trace()
                for tmpfile in vc_files:
                    os.remove(tmpfile)
            case _Action.DISCARD:
                self._flush('Aborted')

    def do_remove(self, line):
        try:
            group = self._resolve_group(line, prompt='Remove from')
        except BadInputError as err:
            self._flush(err)
            return
        aliases = self.app.get_aliases(group)
        if not aliases:
            self._flush('Nothing found')
            return
        alias = self.launch_single_choice('Choose', aliases)
        warning = 'This cannot be undone. Are you sure?'
        yes = self.launch_yes_no(warning)
        if yes:
            self.app.remove(alias, group)
            self._flush('Removed %s' % alias)
        else:
            self._flush('Aborted')

    def do_clear(self, line):
        try:
            group = self._resolve_group(line, prompt='Clear')
        except BadInputError as err:
            self._flush(err)
            return
        warning = 'This cannot be undone. Are you sure?'
        yes = self.launch_yes_no(warning)
        if yes:
            self.app.clear(group)
            self._flush(f'Cleared {group}s')
        else:
            self._flush('Aborted')

    def do_EOF(self, line):
        return True

    do_exit = do_EOF
    do_quit = do_EOF
    do_q    = do_EOF

    def help_list(self):
        self._flush_help(
            'list [key | did | credentials]',
            'List objects of provided type',
        )

    def help_count(self):
        self._flush_help(
            'count [key | did | credentials]',
            'Count objects of provided type',
        )

    def help_inspect(self):
        msg = '\n'.join([
            'TODO',
        ])
        self._flush(msg)

    def help_create(self):
        msg = '\n'.join([
            'TODO',
        ])
        self._flush(msg)

    def help_resolve(self):
        msg = '\n'.join([
            'TODO',
        ])
        self._flush(msg)

    def help_present(self):
        msg = '\n'.join([
            'TODO'
        ])
        self._flush(msg)

    def help_request(self):
        msg = '\n'.join([
            'TODO'
        ])
        self._flush(msg)

    def help_remove(self):
        msg = '\n'.join([
            'TODO',
        ])
        self._flush(msg)

    def help_clear(self):
        msg = '\n'.join([
            'TODO',
        ])
        self._flush(msg)

    def help_EOF(self):
        msg = '\n'.join([
            'Quit current wallet session',
        ])
        self._flush(msg)

    help_exit   = help_EOF
    help_quit   = help_EOF
    help_q      = help_EOF

