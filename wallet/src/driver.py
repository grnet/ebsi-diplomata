import cmd, sys
import json
import os
from ui import MenuHandler
from util import run_cmd, HttpClient
from conf import STORAGE, TMPDIR, DBNAME, INTRO, PROMPT, INDENT, \
    _Group, _Action, _UI, ED25519, SECP256
from db import DbConnector

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

class CreationError(BaseException):
    pass

class LoadError(BaseException):
    pass

class RegistrationError(BaseException):
    pass

class ResolutionError(BaseException):
    pass

class WalletShell(cmd.Cmd, MenuHandler):
    intro   = INTRO.format(__version__)
    prompt  = PROMPT

    def __init__(self):
        self._db = DbConnector(os.path.join(STORAGE, DBNAME))
        super().__init__()

    def run(self):
        super().cmdloop()

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
        entry = self._db.get(key, _Group.KEY)
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
        # NOTE: check data/ebsi/<did>/
        # NOTE: Check data/did/resolved/did-ebsi-*.json
        self._db.store(created, _Group.DID)
        os.remove(tmpfile)
        return alias

    def resolve_did(self, alias):
        res, code = run_cmd(['resolve-did', '--did', alias,])
        if code != 0:
            err = res
            raise ResolutionError(err)
        # NOTE: check data/ebsi/<did>/
        # NOTE: Check data/did/resolved/did-ebsi-*.json

    def create_verifiable_presentation(self, vc_files, did):
        key = self._db.get_key_from_did(did)
        try:
            self.load_key(key)
        except LoadError as err:
            err = 'Could not create DID: %s' % err
            raise CreationError(err)
        args = ['present-vc', '--holder-did', did,]
        for credential in vc_files:
            args += ['--credential', credential,]
        res, code = run_cmd(args)
        if code != 0:
            err = 'Could not present: %s' % res
            raise CreationError(err)
        # TODO: Where was it saved?

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

    def flush_list(self, lst):
        for _ in lst: self.flush(_)

    def flush_help(self, *messages):
        self.flush('\n'.join(messages))

    def _adjust_input(self, line):
        return line.strip().lower().rstrip('s')

    def _resolve_group(self, line, prompt):
        aux = self._adjust_input(line)
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

    def do_list(self, line):
        try:
            group = self._resolve_group(line, prompt='Show list of')
        except BadInputError as err:
            self.flush(err)
            return
        entries = self._db.get_aliases(group)
        if not entries:
            self.flush('Nothing found')
            return
        self.flush_list(entries)

    def do_count(self, line):
        try:
            group = self._resolve_group(line, prompt='Show number of')
        except BadInputError as err:
            self.flush(err)
            return
        nr = self._db.get_nr(group)
        self.flush(nr)

    def do_inspect(self, line):
        try:
            group = self._resolve_group(line, prompt='Inspect from')
        except BadInputError as err:
            self.flush(err)
            return
        aliases = self._db.get_aliases(group)
        if not aliases:
            self.flush('Nothing found')
            return
        alias = self.launch_single_choice('Choose', aliases)
        entry = self._db.get(alias, group)
        self.flush(entry)

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
                    self.flush('Key generation aborted')
                    return
                self.flush('Creating %s key (takes seconds) ...' \
                    % algorithm)
                try:
                    alias = self.create_key(algorithm)
                except CreationError as err:
                    self.flush(err)
                    return
                self.flush('Created key: %s' % alias)
            case _Group.DID:
                keys = self._db.get_aliases(_Group.KEY)
                if not keys:
                    self.flush('No keys found. Must first create one.')
                    return
                answers = self.launch_prompt({
                    'single': {
                        'prompt': 'Choose key: ',
                        'choices': keys
                    },
                    'input': 'Token: ',
                    'yes_no': 'A new DID will be saved to disk. Proceed?',
                })
                key, token, proceed = answers
                if not proceed: 
                    self.flush('DID generation aborted')
                    return
                self.flush('Creating DID (takes seconds) ...')
                try:
                    alias = self.create_did(key, token)
                except CreationError as err:
                    self.flush(err)
                    return
                self.flush('Created DID: %s' % alias)

    def do_resolve(self, line):
        alias = self.launch_input('Give DID: ')
        try:
            self.resolve_did(alias)
        except ResolutionError as err:
            self.flush('Cound not resolve: %s' % err)
            return
        self.flush('DID resolved')

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
                choices = self._db.get_aliases(_Group.DID)
                if not choices:
                    self.flush('No DIDs found. Must first create one.')
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
                self._db.store(credential, _Group.VC)
                self.flush('The following credential was saved to disk:')
                self.flush(credential['id'])
            case _Action.VERIFY:
                # choices = self._db.get_aliases(_Group.VC)
                # if not choices:
                #     self.flush('No credentials found')
                #     return
                # alias = self.launch_single_choice('Choose credential', 
                #     choices)
                # credential = self._db.get(alias, _Group.VC)
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
                # self.flush(resp.json())
                did_choices = self._db.get_aliases(_Group.DID)
                if not did_choices:
                    self.flush('No DIDs found. Must create at least one.')
                    return
                did = self.launch_single_choice('Choose DID', did_choices)
                vc_choices = self._db.get_vcs_by_did(did)
                if not vc_choices:
                    self.flush('No credentials found for the provided DID')
                    return
                selected = self.launch_multiple_choices(
                    'Select credentials to present', vc_choices)
                credentials = [self._db.get(alias, _Group.VC) for alias
                    in selected]
                if not credentials:
                    self.flush('Aborted')
                    return
                vc_files = []
                for c in credentials:
                    tmpfile = os.path.join(TMPDIR, '%s.json' \
                        % c['id'])
                    with open(tmpfile, 'w+') as f:
                        json.dump(c, f, indent=INDENT)
                    vc_files += [tmpfile,]
                try:
                    vp = self.create_verifiable_presentation(vc_files, 
                            did)
                except CreationError as err:
                    self.flush(err)
                    return
                pass    # TODO
                #
                #
                #
                import pdb; pdb.set_trace()
                for tmpfile in vc_files:
                    os.remove(tmpfile)
            case _Action.DISCARD:
                self.flush('Aborted')

    def do_remove(self, line):
        try:
            group = self._resolve_group(line, prompt='Remove from')
        except BadInputError as err:
            self.flush(err)
            return
        aliases = self._db.get_aliases(group)
        if not aliases:
            self.flush('Nothing found')
            return
        alias = self.launch_single_choice('Choose', aliases)
        warning = 'This cannot be undone. Are you sure?'
        yes = self.launch_yes_no(warning)
        if yes:
            self._db.remove(alias, group)
            self.flush('Removed %s' % alias)
        else:
            self.flush('Aborted')

    def do_clear(self, line):
        try:
            group = self._resolve_group(line, prompt='Clear')
        except BadInputError as err:
            self.flush(err)
            return
        warning = 'This cannot be undone. Are you sure?'
        yes = self.launch_yes_no(warning)
        if yes:
            self._db.clear(group)
            self.flush(f'Cleared {group}s')
        else:
            self.flush('Aborted')

    def do_EOF(self, line):
        return True

    do_exit = do_EOF
    do_quit = do_EOF
    do_q    = do_EOF

    def help_list(self):
        self.flush_help(
            'list [key | did | credentials]',
            'List objects of provided type',
        )

    def help_count(self):
        self.flush_help(
            'count [key | did | credentials]',
            'Count objects of provided type',
        )

    def help_inspect(self):
        msg = '\n'.join([
            'TODO',
        ])
        self.flush(msg)

    def help_create(self):
        msg = '\n'.join([
            'TODO',
        ])
        self.flush(msg)

    def help_resolve(self):
        msg = '\n'.join([
            'TODO',
        ])
        self.flush(msg)

    def help_present(self):
        msg = '\n'.join([
            'TODO'
        ])
        self.flush(msg)

    def help_request(self):
        msg = '\n'.join([
            'TODO'
        ])
        self.flush(msg)

    def help_remove(self):
        msg = '\n'.join([
            'TODO',
        ])
        self.flush(msg)

    def help_clear(self):
        msg = '\n'.join([
            'TODO',
        ])
        self.flush(msg)

    def help_EOF(self):
        msg = '\n'.join([
            'Quit current wallet session',
        ])
        self.flush(msg)

    help_exit   = help_EOF
    help_quit   = help_EOF
    help_q      = help_EOF

