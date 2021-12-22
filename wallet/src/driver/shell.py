import cmd, sys
import json
import os
from urllib.parse import urljoin
import requests
from ssi_lib import \
    Template, \
    Vc
from conf import STORAGE, TMPDIR, Table, Ed25519, Secp256k1, RSA
from app import CreationError, RegistrationError, ResolutionError, \
        IssuanceError, VerificationError
from driver.conf import INTRO, PROMPT, INDENT, Action, UI
from driver.ui import MenuHandler
from __init__ import __version__


# This module is terminal and any exceptions are intended for internal
# consumption (print message in stdout and return).

class NothingFound(BaseException):
    pass

class BadImport(BaseException):
    pass

class BadInput(BaseException):
    pass

class Abortion(BaseException):
    pass

class HttpConnectionError(BaseException):
    pass


class HttpClient(object):

    def __init__(self, remote):
        self.remote = remote

    def _create_url(self, endpoint):
        return urljoin(self.remote, endpoint.lstrip('/'))

    def _do_request(self, method, url, **kw):
        try:
            resp = getattr(requests, method)(url, **kw)
        except requests.exceptions.ConnectionError as err:
            raise HttpConnectionError(err)
        return resp

    def get(self, endpoint):
        resp = self._do_request('get', self._create_url(endpoint))
        return resp

    def post(self, endpoint, payload):
        resp = self._do_request('post', self._create_url(endpoint),
                json=payload)
        return resp


class WalletShell(cmd.Cmd, MenuHandler):
    intro   = INTRO.format(__version__)
    prompt  = PROMPT

    def __init__(self, app):
        self._app = app
        self._mapping = {
            UI.KEY: Table.KEY,
            UI.KEYS: Table.KEY,
            UI.DID: Table.DID,
            UI.DIDS: Table.DID,
            UI.VC: Table.VC,
            UI.VCS: Table.VC,
            UI.VP: Table.VP,
            UI.VPS: Table.VP,
            UI.ISSUE: Action.ISSUE,
            UI.VERIFY: Action.VERIFY,
            UI.CHOOSE: Action.CHOOSE,
            UI.IMPORT: Action.IMPORT,
            UI.DISCARD: Action.DISCARD,
        }
        super().__init__()

    def run(self):
        super().cmdloop()

    def preloop(self):
        pass

    def postloop(self):
        pass

    def flush(self, buff):
        buff = json.dumps(buff, indent=INDENT) if type(buff) \
                in (dict, list,) else str(buff)
        sys.stdout.write(buff + '\n')

    def flush_list(self, lst):
        for _ in lst: self.flush(_)

    def dump(self, obj, filename):
        filename = filename + ('.json' \
            if not filename.endswith('.json') else '')
        tmpfile = os.path.join(TMPDIR, filename)
        with open(tmpfile, 'w+') as f:
            json.dump(obj, f)
        return tmpfile

    def resolve_table(self, line, prompt):
        line = line.strip().lower().rstrip('s')
        match line:
            case '':
                ans = self.launch_choice(prompt, [
                    UI.KEYS,
                    UI.DIDS,
                    UI.VCS,
                    UI.VPS,
                ])
                out = self._mapping[ans]
            case (
                    UI.KEY |
                    UI.DID |
                    UI.VC  |
                    UI.VP
                ):
                out = self._mapping[line]
            case (
                    Table.KEY |
                    Table.DID |
                    Table.VC  |
                    Table.VP
                ):
                out = line
            case _:
                err = 'Bad input: %s' % line
                raise BadInput(err)
        return out

    def prepare_issuance_payload(self):
        choices = self._app.fetch_dids()
        if not choices:
            err = 'No DIDs found. Must first create one.'
            raise NothingFound(err)
        did = self.launch_choice('Choose holder DID', choices)
        # TODO: Select credential type and values via user input
        # TODO: This construction assumes than an API spec has been advertized
        # on behalf of the issuer
        payload = {
            'holder': did,
            'vc_type': Vc.DIPLOMA,
            'content': {
                'person_id': '0x666',
                'name': 'Lucrezia',
                'surname': 'Borgia',
                'subject': 'POISONING',
            },
        }
        return payload

    def normalize_diploma_content(self, content):
        # TODO
        out = getattr(Template, Vc.DIPLOMA)
        out['person_identifier'] = content['person_id']
        out['person_family_name'] = content['name']
        out['person_given_name'] = content['surname']
        out['awarding_opportunity_identifier'] = content['subject']
        return out

    def issue_credential(self, line):
        payload = self.prepare_issuance_payload()
        dids = self._app.fetch_dids()
        issuer = self.launch_choice('Choose issuer DID', dids)
        if not self.launch_yn('New credential will be issued. Proceed?'):
            raise Abortion('Issuance aborted')
        try:
            holder = payload['holder']
            vc_type = payload['vc_type']
            content = payload['content']
        except KeyError as err:
            raise IssuanceError(err)
        try:
            content = self.normalize_diploma_content(content)
        except KeyError as err:
            raise IssuanceError(err)
        out = self._app.issue_credential(holder, issuer, vc_type,
                content)
        return out

    def present_credentials(self, line):
        dids = self._app.fetch_aliases(Table.DID)
        if not dids:
            err = 'No DIDs found.'
            raise NothingFound(err)
        holder = self.launch_choice('Choose holder DID', dids)
        vc_choices = self._app.fetch_credentials_by_holder(holder)
        if not vc_choices:
            err = 'No credentials found for the provided holder.'
            raise NothingFound(err)
        vc_selected = self.launch_selection(
            'Select credentials to present', vc_choices)
        if not vc_selected:
            err = 'No credentials selected'
            raise Abortion(err)
        credentials = []
        for alias in vc_selected:
            credential = self._app.fetch_credential(alias)
            vc_file = self.dump(credential, '%s.json' % alias)
            credentials += [vc_file,]
        alias = self._app.create_presentation(holder, credentials)
        return alias

    def select_presentation(self):
        match self.launch_choice('Select presentation to verify', [
            UI.CHOOSE, UI.IMPORT]):
            case UI.CHOOSE:
                vps = self._app.fetch_presentations()
                if not vps:
                    err = 'No presentation found'
                    raise NothingFound(err)
                alias = self.launch_choice('', vps)
                out = self._app.fetch_presentation(alias)
            case UI.IMPORT:
                out = self.import_object()
        return out

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
            raise BadImport(err)
        return out

    def do_list(self, line):
        try:
            table = self.resolve_table(line, prompt='Show list of')
        except BadInput as err:
            self.flush(err)
            return
        entries = self._app.fetch_aliases(table)
        if not entries:
            self.flush('Nothing found')
            return
        self.flush_list(entries)

    def do_count(self, line):
        try:
            table = self.resolve_table(line, prompt='Show number of')
        except BadInput as err:
            self.flush(err)
            return
        nr = self._app.fetch_nr(table)
        self.flush(nr)

    def do_inspect(self, line):
        try:
            table = self.resolve_table(line, prompt='Inspect from')
        except BadInput as err:
            self.flush(err)
            return
        aliases = self._app.fetch_aliases(table)
        if not aliases:
            self.flush('Nothing found')
            return
        alias = self.launch_choice('Choose', aliases)
        entry = self._app.fetch_entry(alias, table)
        self.flush(entry)

    def do_create(self, line):
        ans = self.launch_choice('Create', [
            UI.KEY,
            UI.DID,
        ])
        match self._mapping[ans]:
            case Table.KEY:
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
                    alias = self._app.create_key(algo)
                except CreationError as err:
                    self.flush('Could not create key: %s' % err)
                    return
                self.flush('Created key: %s' % alias)
            case Table.DID:
                keys = self._app.fetch_keys()
                if not keys:
                    self.flush('No keys found. Must first create one.')
                    return
                key = self.launch_choice('Choose key:', keys)
                token = ''
                if self.launch_yn('Do you want to provide an EBSI token?'):
                    token = self.launch_input('Token:')
                if not token and not self.launch_yn(
                    'WARNING: No token provided. The newly created DID will\n' +
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
                    alias = self._app.create_did(key, token, onboard)
                except CreationError as err:
                    self.flush('Could not create DID: %s' % err)
                    return
                self.flush('Created DID: %s' % alias)

    def do_register(self, line):
        dids = self._app.fetch_dids()
        if not dids:
            self.flush('No DIDs found')
            return
        alias = self.launch_choice('Choose DID:', dids)
        token = self.launch_input('Token:')
        self.flush('Registering (takes seconds) ...')
        try:
            self._app.register_did(alias, token)
        except RegistrationError as err:
            err = 'Could not register: %s' % err
            self.flush(err)
            return
        self.flush('Registered %s to the EBSI')

    def do_resolve(self, line):
        alias = self.launch_input('Give DID:')
        self.flush('Resolving ...')
        try:
            self._app.resolve_did(alias)
        except ResolutionError as err:
            self.flush('Could not resolve: %s' % err)
            return
        did = self._app.retrieve_resolved_did(alias)
        self.flush(did)

    def do_issue(self, line):
        try:
            vc = self.issue_credential(line)
        except (IssuanceError, NothingFound,) as err:
            self.flush('Could not issue: %s' % err)
            return
        except Abortion as err:
            self.flush('Issuance aborted: %s' % err)
            return
        self.flush('Issued credential')
        if self.launch_yn('Inspect?'):
            self.flush(vc)
        if not self.launch_yn('Save to disk?'):
            if self.launch_yn('Credential will be lost. Are you sure?'):
                del vc
                return
        alias = self._app.store_credential(vc)
        self.flush('Credential was saved to disk:\n%s' % alias)

    def do_present(self, line):
        try:
            alias = self.present_credentials(line)
        except (NothingFound, CreationError,) as err:
            self.flush('Could not present: %s' % err)
            return
        except Abortion as err:
            self.flush('Presentation aborted: %s' % err)
            return
        self.flush('Presentation saved in disk: %s' % alias)
        if self.launch_yn('Inspect?'):
            vp = self._app.fetch_presentation(alias)
            self.flush(vp)
        if self.launch_yn('Export?'):
            vp = self._app.fetch_presentation(alias)
            try:
                outfile = self.export_object(vp)
            except Abortion:
                self.flush('Aborted export')
                return
            self.flush('Exported to: %s' % outfile)

    def do_verify(self, line):
        try:
            vp = self.select_presentation()
        except BadImport as err:
            self.flush('Could not import: %s' % err)
            return
        except NothingFound as err:
            self.flush('Verification aborted: %s' % err)
            return
        self.flush('Verifying (takes seconds)...')
        try:
            results = self._app.verify_presentation(vp)
        except VerificationError as err:
            self.flush('Could not verify: %s' % err)
            return
        # Flush results
        self.flush('Presentation was %sverified:' % ('' if \
            results['Verified'] else 'NOT '))
        self.flush(results)

    def do_request(self, line):
        action = self.launch_choice('Request', [
            UI.ISSUE,
            UI.VERIFY,
            UI.DISCARD,
        ])
        match self._mapping[action]:
            case Action.ISSUE:
                try:
                    payload = self.prepare_issuance_payload()
                except NothingFound as err:
                    self.flush('Request aborted: %s' % err)
                    return
                # TODO: Choose from known registrar of issuers or reveive from
                # user input
                address = 'http://localhost:7000'
                endpoint = 'api/v1/credentials/issue/'
                try:
                    self.flush('Waiting for response (takes seconds)...')
                    resp = HttpClient(address).post(endpoint, payload)
                except HttpConnectionError as err:
                    self.flush('Could not connect to issuer: %s' % err)
                    return
                # TODO: This handling assumes that an API spec has been
                # aedvertized on behalf of the issuer
                match resp.status_code:
                    case 200:
                        vc = resp.json()['vc']
                        self.flush('Credential received.')
                        if self.launch_yn('Inspect?'):
                            self.flush(vc)
                        if not self.launch_yn('Save to disk?'):
                            if self.launch_yn('Credential will be lost. '
                            + 'Are you sure?'):
                                del vc
                                return
                        alias = self._app.store_credential(vc)
                        self.flush('Credential was saved to disk:\n%s' % alias)
                    case 512:
                        err = resp.json()['err']
                        self.flush('Could not issue: %s' % err)
                    case 400:
                        err = resp.json()['err']
                        self.flush('Could not issue: %s' % err)
                    case _:
                        self.flush('Could not issue:')
                        self.flush(resp.json())             # TODO: Capture error
            case Action.VERIFY:
                try:
                    vp = self.select_presentation()
                except BadImport as err:
                    self.flush('Could not import: %s' % err)
                    return
                except NothingFound as err:
                    self.flush('Verification aborted: %s' % err)
                    return
                # TODO: Choose from known registrar of verifiers or reveive
                # from user input
                address = 'http://localhost:7001'
                endpoint = 'api/v1/credentials/verify/'
                try:
                    self.flush('Waiting for response (takes seconds)...')
                    resp = HttpClient(address).post(endpoint, {
                        'vp': vp,
                    })
                except HttpConnectionError as err:
                    self.flush('Could not connect to issuer: %s' % err)
                    return
                # TODO: This handling assumes that an API spec has been
                # aedvertized on behalf of the verifier
                match resp.status_code:
                    case 200:
                        results = resp.json()['results']
                        self.flush('Presentation was %sverified:' % ('' if \
                            results['Verified'] else 'NOT '))
                        self.flush(results)
                    case 512:
                        err = resp.json()['err']
                        self.flush('Could not verify: %s' % err)
                    case 400:
                        err = resp.json()['err']
                        self.flush('Could not verify: %s' % err)
                    case _:
                        self.flush('Could not verify:')
                        self.flush(resp.json())             # TODO: Capture error
                pass
            case Action.DISCARD:
                self.flush('Request aborted')

    def do_export(self, line):
        try:
            table = self.resolve_table(line, prompt='Export from')
        except BadInput as err:
            self.flush(err)
            return
        aliases = self._app.fetch_aliases(table)
        if not aliases:
            self.flush('Nothing found')
            return
        alias = self.launch_choice('Choose', aliases)
        entry = self._app.fetch_entry(alias, table)
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
        table = self.launch_choice('Saved as', [
            UI.KEY, UI.DID, UI.VC, UI.VP,
        ])
        self._app.store(obj, self._mapping[table])

    def do_remove(self, line):
        try:
            table = self.resolve_table(line, prompt='Remove from')
        except BadInput as err:
            self.flush(err)
            return
        aliases = self._app.fetch_aliases(table)
        if not aliases:
            self.flush('Nothing found')
            return
        selected = self.launch_selection('Select entries to remove',
            aliases)
        if not self.launch_yn('This cannot be undone. Proceed?'):
            self.flush('Removal aborted')
            return
        for alias in selected:
            self._app.remove(alias, table)
            self.flush('Removed %s' % alias)

    def do_clear(self, line):
        try:
            table = self.resolve_table(line, prompt='Clear')
        except BadInput as err:
            self.flush(err)
            return
        if not self.launch_yn('This cannot be undone. Proceed?'):
            self.flush('Aborted')
            return
        nr_entries = self._app.fetch_nr(table)
        self._app.clear(table)
        self.flush(f'Cleared %d %s%s' % (nr_entries, table, 's' if nr_entries
            != 1 else ''))

    def do_EOF(self, line):
        return True

    do_exit = do_EOF
    do_quit = do_EOF
    do_q    = do_EOF
