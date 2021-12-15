import cmd, sys
import json
import os
from ui import MenuHandler
from util import HttpClient
from conf import TMPDIR, WALTDIR, INTRO, PROMPT, INDENT, RESOLVED, \
    STORAGE, _Action, _UI, EBSI_PRFX, Ed25519, Secp256k1, RSA
from ssi_lib import SSIGenerationError, SSIRegistrationError, \
    SSIResolutionError, SSIIssuanceError, SSIVerificationError
from ssi_lib.conf import _Group   # TODO: Get rid of this?
from ssi_lib.conf import _Vc # TODO

_mapping = {
    _UI.KEY: _Group.KEY,
    _UI.KEYS: _Group.KEY,
    _UI.DID: _Group.DID,
    _UI.DIDS: _Group.DID,
    _UI.VC: _Group.VC,
    _UI.VCS: _Group.VC,
    _UI.VP: _Group.VP,
    _UI.VPS: _Group.VP,
    _UI.ISSUE: _Action.ISSUE,
    _UI.VERIFY: _Action.VERIFY,
    _UI.CHOOSE: _Action.CHOOSE,
    _UI.IMPORT: _Action.IMPORT,
    _UI.DISCARD: _Action.DISCARD,
}

__version__ = '0.0.1'

class BadInputError(BaseException):
    pass

class CreationError(BaseException):
    pass

class RegistrationError(BaseException):
    pass

class IssuanceError(BaseException):
    pass

class PresentationError(BaseException):
    pass

class VerificationError(BaseException):
    pass

class WalletImportError(BaseException):
    pass

class Abortion(BaseException):
    pass


class WalletShell(cmd.Cmd, MenuHandler):
    intro   = INTRO.format(__version__)
    prompt  = PROMPT

    def __init__(self, app):
        self.app = app
        super().__init__()

    def get_keys(self):
        return self.app.get_keys()

    def run(self):
        super().cmdloop()

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

    def dump(self, obj, filename):
        filename = filename + ('.json' \
            if not filename.endswith('.json') else '')
        tmpfile = os.path.join(TMPDIR, filename)
        with open(tmpfile, 'w+') as f:
            json.dump(obj, f)
        return tmpfile

    def resolve_group(self, line, prompt):
        line = line.strip().lower().rstrip('s')
        match line:
            case '':
                ans = self.launch_choice(prompt, [
                    _UI.KEYS, 
                    _UI.DIDS, 
                    _UI.VCS,
                    _UI.VPS,
                ])
                out = _mapping[ans]
            case (
                    _UI.KEY |
                    _UI.DID |
                    _UI.VC  |
                    _UI.VP
                ):
                out = _mapping[line]
            case (
                    _Group.KEY |
                    _Group.DID |
                    _Group.VC  |
                    _Group.VP
                ):
                out = line
            case _:
                err = 'Bad input: %s' % line
                raise BadInputError(err)
        return out

    def create_key(self, algo):
        try:
            key = self.app.generate_key(algo)
        except SSIGenerationError as err:
            err = 'Could not generate key: %s' % err
            raise CreationError(err)
        alias = self.app.store_key(key)
        return alias

    def register_did(self, alias, token):
        try:
            self.app.register_did(alias, token)
        except SSIRegistrationError as err:
            raise RegistrationError(err)

    def create_did(self, key, token, onboard=True):
        try:
            did = self.app.generate_did(key, token, onboard)
        except SSIGenerationError as err:
            err = 'Could not generate DID: %s' % err
            raise CreationError(err)
        if onboard:
            try:
                self.app.register_did(did['id'], token)
            except SSIRegistrationError as err:
                err = 'Could not register: %s' % err
                raise CreationError(err)
        alias = self.app.store_did(did)
        return alias

    def retrieve_resolved_did(self, alias):
        resolved = os.path.join(RESOLVED, 'did-ebsi-%s.json' % \
            alias.lstrip(EBSI_PRFX))
        with open(resolved, 'r') as f:
            out = json.load(f)
        return out

    def prepare_issuance_payload(self):
        aliases = self.app.get_dids()
        if not aliases:
            err = 'No DIDs found. Must first create one.'
            raise Abortion(err)
        holder_did = self.launch_choice('Choose holder DID', aliases)
        # TODO: Select values via user input
        # TODO: This construction assumes than an API spec has been advertized
        # on behalf of the issuer
        payload = {
            'holder': holder_did,
            'template': _Vc.DIPLOMA,
            'content': {
                'person_id': '0x666',
                'name': 'Lucrezia',
                'surname': 'Borgia',
                'subject': 'POISONING',
            },
        }
        return payload

    def extract_issuance_payload(self, payload):
        # TODO: Validate structure?
        holder_did = payload['holder']
        template = payload['template']
        content = payload['content']
        return holder_did, template, content

    def issue_credential(self, line):
        try:
            payload = self.prepare_issuance_payload()
        except Abortion as err:
            self.flush('Request aborted: %s' % err)
            return
        aliases = self.app.get_dids()
        issuer_did = self.launch_choice('Choose issuer DID', aliases)
        if not self.launch_yn('New credential will be issued. Proceed?'):
            raise Abortion('Issuance aborted')
        try:
            holder_did, template, content = self.extract_issuance_payload(
                payload)
            out = self.app.issue_credential(holder_did, issuer_did, template,
                    content)
        except SSIIssuanceError as err:
            raise IssuanceError(err)
        return out

    def create_presentation(self, holder_did, credentials):
        try:
            out = self.app.generate_presentation(holder_did, credentials,
                WALTDIR)
        except SSIGenerationError as err:
            err = 'Could not generate presentation: %s' % err
            raise CreationError(err)
        return out

    def present_credentials(self, line):
        did_choices = self.app.get_aliases(_Group.DID)
        if not did_choices:
            err = 'No DIDs found. Must create at least one.'
            raise PresentationError(err)
        holder_did = self.launch_choice('Choose holder DID', did_choices)
        vc_choices = self.app.get_credentials_by_did(holder_did)
        if not vc_choices:
            err = 'No credentials found for the provided holder DID'
            raise PresentationError(err)
        vc_selected = self.launch_selection(
            'Select credentials to verify', vc_choices)
        if not vc_selected:
            err = 'Presentation aborted: No credentials selected'
            raise PresentationError(err)
        credentials = []
        for alias in vc_selected:
            credential = self.app.get_credential(alias)
            vc_file = self.dump(credential, '%s.json' % alias)
            credentials += [vc_file,]
        try:
            out = self.create_presentation(holder_did, credentials)
        except CreationError as err:
            raise PresentationError(err)
        return out

    def select_presentation(self):
        match self.launch_choice('Select presentation to verify', [
            _UI.CHOOSE, _UI.IMPORT]):
            case _UI.CHOOSE:
                aliases = self.app.get_presentations()
                if not aliases:
                    err = 'Nothing found'
                    raise Abortion(err)
                alias = self.launch_choice('', aliases)
                out = self.app.get_presentation(alias)
            case _UI.IMPORT:
                try:
                    out = self.import_object()
                except WalletImportError:
                    raise
        return out

    def verify_presentation(self, vp):
        try:
            results = self.app.verify_presentation(vp)
        except SSIVerificationError as err:
            raise VerificationError(err)
        return results

    def export_object(self, entry):
        filename = ''
        while filename in ('', None):
            filename = self.launch_input('Give filename:')
            if filename is not None:
                filename = filename.strip()
        outfile = os.path.join(STORAGE, filename)
        if os.path.isfile(outfile):
            if not self.launch_yn('File exists. Overwrite?'):
                raise Abortion
        with open(outfile, 'w+') as f:
            json.dump(entry, f, indent=INDENT)
        return outfile

    def import_object(self):
        infile = self.launch_input('Give absolute path to file:')
        try:
            with open(infile, 'r') as f:
                out = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as err:
            err = 'Could not import: %s' % str(err)
            raise WalletImportError(err)
        return out

    def do_list(self, line):
        try:
            group = self.resolve_group(line, prompt='Show list of')
        except BadInputError as err:
            self.flush(err)
            return
        entries = self.app.get_aliases(group)
        if not entries:
            self.flush('Nothing found')
            return
        self.flush_list(entries)

    def do_count(self, line):
        try:
            group = self.resolve_group(line, prompt='Show number of')
        except BadInputError as err:
            self.flush(err)
            return
        nr = self.app.get_nr(group)
        self.flush(nr)

    def do_inspect(self, line):
        try:
            group = self.resolve_group(line, prompt='Inspect from')
        except BadInputError as err:
            self.flush(err)
            return
        aliases = self.app.get_aliases(group)
        if not aliases:
            self.flush('Nothing found')
            return
        alias = self.launch_choice('Choose', aliases)
        entry = self.app.get_entry(alias, group)
        self.flush(entry)

    def do_create(self, line):
        ans = self.launch_choice('Create', [
            _UI.KEY, 
            _UI.DID,
        ])
        match _mapping[ans]:
            case _Group.KEY:
                algo = self.launch_choice('Choose keygen algorithm', [
                        Ed25519,
                        Secp256k1,
                        RSA,
                    ])
                if not self.launch_yn('Key will be save to disk. Proceed?'):
                    self.flush('Key creation aborted')
                    return
                self.flush('Generating %s key (takes seconds) ...' % algo)
                try:
                    alias = self.create_key(algo)
                except CreationError as err:
                    self.flush('Could not create key: %s' % err)
                    return
                self.flush('Created key: %s' % alias)
            case _Group.DID:
                keys = self.get_keys()
                if not keys:
                    self.flush('No keys found. Must first create one.')
                    return
                key = self.launch_choice('Choose key:', keys)
                token = ''
                if self.launch_yn('Do you want to provide an EBSI token?'):
                    token = self.launch_input('Token:')
                if not token and not self.launch_yn(
                    'WARNING: No token provided. The newly created DID will ' +
                    'not be registered to the EBSI. Proceed?'):
                    self.flush('DID creation aborted')
                    return
                onboard = False
                if token:
                    onboard = self.launch_yn(
                        'Register the newly created DID to EBSI?')
                if not self.launch_yn(
                        'A new DID will be saved to disk. Proceed?'):
                    self.flush('DID creation aborted')
                    return
                self.flush('Creating DID (takes seconds) ...')
                try:
                    alias = self.create_did(key, token, onboard)
                except CreationError as err:
                    self.flush('Could not create DID: %s' % err)
                    return
                self.flush('Created DID: %s' % alias)

    def do_register(self, line):
        dids = self.app.get_dids()
        if not dids:
            self.flush('No DIDs found')
            return
        alias = self.launch_choice('Choose DID:', dids)
        token = self.launch_input('Token:')
        self.flush('Registering (takes seconds) ...')
        try:
            self.app.register_did(alias, token)
        except SSIRegistrationError as err:
            err = 'Could not register: %s' % err
            self.flush(err)
            return
        self.flush('Registered %s to the EBSI')

    def do_resolve(self, line):
        alias = self.launch_input('Give DID:')
        self.flush('Resolving ...')
        try:
            self.app.resolve_did(alias)
        except SSIResolutionError as err:
            self.flush('Could not resolve: %s' % err)
            return
        did = self.retrieve_resolved_did(alias)
        self.flush(did)

    def do_issue(self, line):
        try:
            credential = self.issue_credential(line)
        except IssuanceError as err:
            self.flush('Could not issue: %s' % err)
            return
        except Abortion as msg:
            self.flush(msg)
            return
        self.flush('Issued credential')
        if self.launch_yn('Inspect?'):
            self.flush(credential)
        if not self.launch_yn('Save to disk?'):
            if self.launch_yn('Credential will be lost. Are you sure?'):
                del credential
                return
        alias = self.app.store_credential(credential)
        self.flush('Credential was saved to disk:')
        self.flush(alias)

    def do_present(self, line):
        try:
            presentation = self.present_credentials(line)
        except PresentationError as err:
            self.flush('Could not present: %s' % err)
            return
        self.flush('Created verifiable presentation from selected credentials.')
        if self.launch_yn('Inspect?'):
            self.flush(presentation)
        if self.launch_yn('Save in disk?'):
            alias = self.app.store_presentation(presentation)
            self.flush('Credential was saved to disk:')
            self.flush(alias)
        if self.launch_yn('Export?'):
            try:
                outfile = self.export_object(presentation)
            except Abortion:
                self.flush('Aborted export')
                return
            self.flush('Exported to: %s' % outfile)

    def do_verify(self, line):
        try:
            vp = self.select_presentation()
        except (Abortion, WalletImportError,) as err:
            self.flush('Verification aborted: %s' % err)
            return
        self.flush('Verifying (takes seconds)...')
        try:
            results = self.verify_presentation(vp)
        except VerificationError as err:
            self.flush('Could not verify: %s' % err)
            return
        # Flush results
        verified = results['Verified']
        message = 'Presentation was %sverified:' % (
            '' if verified else 'NOT ')
        self.flush(message)
        self.flush(results)

    def do_request(self, line):
        action = self.launch_choice('Request', [
            _UI.ISSUE, 
            _UI.VERIFY, 
        ])
        match _mapping[action]:
            case _Action.ISSUE:
                try:
                    payload = self.prepare_issuance_payload()
                except Abortion as err:
                    self.flush('Request aborted: %s' % err)
                    return
                # TODO: Choose from known registar of issuers?
                # TODO: Handle connection errors and timeouts
                remote = 'http://localhost:7000'
                endpoint = 'api/v1/credentials/issue/'
                resp = HttpClient(remote).post(endpoint, payload)
                # TODO: This handling assumes that an API spect has been
                # aedvertized on behalf of the issuer
                match resp.status_code:
                    case 200:
                        self.flush('Credential received from issuer')
                        credential = resp.json()
                        if self.launch_yn('Inspect?'):
                            self.flush(credential)
                        if not self.launch_yn('Save to disk?'):
                            if self.launch_yn('Credential will be lost. '
                            + 'Are you sure?'):
                                del credential
                                return
                        alias = self.app.store_credential(credential)
                        self.flush('Credential was saved to disk:')
                        self.flush(alias)
                    case 512:
                        message = resp.json()['message']
                        self.flush('Could not issue: %s' % message)
                    case _:
                        self.flush('Could not issue:')
                        self.flush(resp.json())             # TODO: Capture message
            case _Action.VERIFY:
                try:
                    payload = self.select_presentation()
                except (Abortion, WalletImportError,) as err:
                    self.flush('Could not select: %s' % err)
                    return
                # TODO: Choose from known registar of verifiers?
                # TODO: Handle connection errors and timeouts
                remote = 'http://localhost:7001'
                endpoint = 'api/v1/credentials/verify/'
                resp = HttpClient(remote).post(endpoint, payload)
                # TODO: This handling assumes that an API spect has been
                # aedvertized on behalf of the verifier
                match resp.status_code:
                    case 200:
                        resutlts = resp.json()
                        verified = results['Verified']
                        message = 'Presentation was %sverified:' % (
                            '' if verified else 'NOT ')
                        self.flush(message)
                        self.flush(results)
                    case 512:
                        message = resp.json()['message']
                        self.flush('Could not verify: %s' % message)
                    case _:
                        self.flush('Could not verify:')
                        self.flush(resp.json())             # TODO: Capture message
                pass
            case _Action.DISCARD:
                self.flush('Request aborted')

    def do_export(self, line):
        try:
            group = self.resolve_group(line, prompt='Export from')
        except BadInputError as err:
            self.flush(err)
            return
        aliases = self.app.get_aliases(group)
        if not aliases:
            self.flush('Nothing found')
            return
        alias = self.launch_choice('Choose', aliases)
        entry = self.app.get_entry(alias, group)
        try:
            outfile = self.export_object(entry)
        except Abortion:
            self.flush('Export aborted')
            return
        self.flush('Exported to: %s' % outfile)

    def do_import(self, line):
        infile = self.launch_input('Give absolute path to file:')
        try:
            with open(infile, 'r') as f:
                obj = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as err:
            self.flush('Could not import: %s' % str(err))
            return
        self.flush('Imported:')
        self.flush(obj)
        if not self.launch_yn('Save to disk?'):
            del obj
            self.flush('Imported object deleted from memory')
            return
        group = self.launch_choice('Saved as', [
            _UI.KEY, _UI.DID, _UI.VC, _UI.VP,
        ])
        self.app.store(obj, _mapping[group])

    def do_remove(self, line):
        try:
            group = self.resolve_group(line, prompt='Remove from')
        except BadInputError as err:
            self.flush(err)
            return
        aliases = self.app.get_aliases(group)
        if not aliases:
            self.flush('Nothing found')
            return
        chosen = self.launch_selection('Choose entries to remove',
            aliases)
        if not self.launch_yn('This cannot be undone. Proceed?'):
            self.flush('Removal aborted')
            return
        for alias in chosen:
            self.app.remove(alias, group)
            self.flush('Removed %s' % alias)

    def do_clear(self, line):
        try:
            group = self.resolve_group(line, prompt='Clear')
        except BadInputError as err:
            self.flush(err)
            return
        if not self.launch_yn('This cannot be undone. Proceed?'):
            self.flush('Aborted')
            return
        self.app.clear(group)
        self.flush(f'Cleared {group}s')

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

    # help_exit   = help_EOF
    # help_quit   = help_EOF
    # help_q      = help_EOF

