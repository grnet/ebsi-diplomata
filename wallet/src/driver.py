import cmd, sys
import json
import os
from ui import MenuHandler
from util import HttpClient
from conf import TMPDIR, WALTDIR, INTRO, PROMPT, INDENT, RESOLVED, \
    STORAGE, _Action, _UI, EBSI_PRFX, ED25519, SECP256
from ssi_lib import SSICreationError as CreationError, \
        SSIResolutionError as ResolutionError
from ssi_lib.conf import _Group   # TODO: Get rid of this?
from ssi_lib.walt import run_cmd    # TODO: Get rid of this

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

class IssuanceError(BaseException):
    pass

class PresentationError(BaseException):
    pass

class VerificationError(BaseException):
    pass


class WalletShell(cmd.Cmd, MenuHandler):
    intro   = INTRO.format(__version__)
    prompt  = PROMPT

    def __init__(self, app):
        self.app = app
        super().__init__()

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

    def _retrieve_resolved_did(self, alias):
        resolved = os.path.join(RESOLVED, 'did-ebsi-%s.json' % \
            alias.lstrip(EBSI_PRFX))
        with open(resolved, 'r') as f:
            out = json.load(f)
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
            self.flush(err)
            return
        entries = self.app.get_aliases(group)
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
        nr = self.app.get_nr(group)
        self.flush(nr)

    def do_inspect(self, line):
        try:
            group = self._resolve_group(line, prompt='Inspect from')
        except BadInputError as err:
            self.flush(err)
            return
        aliases = self.app.get_aliases(group)
        if not aliases:
            self.flush('Nothing found')
            return
        alias = self.launch_single_choice('Choose', aliases)
        entry = self.app.get_entry(alias, group)
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
                    alias = self.app.create_key(algorithm)
                except CreationError as err:
                    self.flush(err)
                    return
                self.flush('Created key: %s' % alias)
            case _Group.DID:
                keys = self.app.get_keys()
                if not keys:
                    self.flush('No keys found. Must first create one.')
                    return
                key = self.launch_single_choice('Choose key:', keys)
                yes = self.launch_yes_no('Do you want to provide a token?')
                token = self.launch_input('Token:') if yes else ''
                if not token:
                    yes = self.launch_yes_no(
                        'WARNING: No token provided. The newly created DID will' +
                        ' not be registered to the EBSI. Proceed?'
                    )
                    if not yes:
                        self.flush('DID creation aborted')
                        return
                onboard = False
                if token:
                    onboard = self.launch_yes_no(
                        'Register the newly created DID to EBSI?')
                yes = self.launch_yes_no(
                    'A new DID will be saved to disk. Proceed?')
                if not yes: 
                    self.flush('DID creation aborted')
                    return
                self.flush('Creating DID (takes seconds) ...')
                try:
                    alias = self.app.create_did(key, token, onboard)
                except CreationError as err:
                    self.flush(err)
                    return
                self.flush('Created DID: %s' % alias)

    def do_resolve(self, line):
        alias = self.launch_input('Give DID:')
        self.flush('Resolving ...')
        try:
            self.app.resolve_did(alias)
        except ResolutionError as err:
            self.flush(err)
            return
        did = self._retrieve_resolved_did(alias)
        self.flush(did)

    def do_issue(self, line):
        dids = self.app.get_aliases(_Group.DID)
        if not dids:
            self.flush('No DIDs found. Must first create one.')
            return
        holder_did = self.launch_single_choice('Choose holder DID', dids)
        issuer_did = self.launch_single_choice('Choose issuer DID', dids)
        yes = self.launch_yes_no('A new credential will be issued. Proceed?')
        if not yes:
            self.flush('Issuance aborted')
            return
        # TODO: Issuer should here fill the following template by comparing the
        # submitted payload against its database. Empty strings lead to the
        # demo defaults of the walt library. 
        vc_content = {
            'holder_did': holder_did,
            'person_identifier': '',
            'person_family_name': '',
            'person_given_name': '',
            'person_date_of_birth': '',
            'awarding_opportunity_id': '',
            'awarding_opportunity_identifier': '',
            'awarding_opportunity_location': '',
            'awarding_opportunity_started_at': '',
            'awarding_opportunity_ended_at': '',
            'awarding_body_preferred_name': '',
            'awarding_body_homepage': '',
            'awarding_body_registraction': '',
            'awarding_body_eidas_legal_identifier': '',
            'grading_scheme_id': '',
            'grading_scheme_title': '',
            'grading_scheme_description': '',
            'learning_achievement_id': '',
            'learning_achievement_title': '',
            'learning_achievement_description': '',
            'learning_achievement_additional_note': '',
            'learning_specification_id': '',
            'learning_specification_ects_credit_points': '',
            'learning_specification_eqf_level': '',
            'learning_specification_iscedf_code': '',
            'learning_specification_nqf_level': '',
            'learning_specification_evidence_id': '',
            'learning_specification_evidence_type': '',
            'learning_specification_verifier': '',
            'learning_specification_evidence_document': '',
            'learning_specification_subject_presence': '',
            'learning_specification_document_presence': '',
        }
        tmpfile = os.path.join(TMPDIR, 'credential.json')
        res, code = run_cmd([
            'issue-credential-ni',  # TODO
            *vc_content.values(),   # TODO
            issuer_did,             # TODO
            tmpfile,                # TODO
        ])
        if code != 0:
            err = 'Could not issue credential: %s' % res
            raise IssuanceError(err)
        with open(tmpfile, 'r') as f:
            credential = json.load(f)
        os.remove(tmpfile)
        yes = self.launch_yes_no('Credential has been issued. Save?')
        if not yes:
            del credential
            self.flush('Credential was lost forever')
            return
        self.app.store_credential(credential)
        self.flush('The following credential was saved to disk:')
        self.flush(credential['id'])

    def create_verifiable_presentation(self, holder_did, vc_files):
        args = ['present-credentials', '--holder-did', holder_did]
        for tmpfile in vc_files:
            args += ['-c', tmpfile,]
        res, code = run_cmd(args)
        if code != 0:
            err = 'Could not create presentation: %s' % res
            raise PresentationError(res)
        sep = 'Verifiable presentation was saved to file: '
        if not sep in res:
            err = 'Could not create presentation: %s' % res
            raise PresentationError(err)
        outfile = os.path.join(WALTDIR, res.split(sep)[-1].replace('"', ''))
        with open(outfile, 'r') as f:
            out = json.load(f)
        os.remove(outfile)
        for tmpfile in vc_files:
            os.remove(tmpfile)
        return out

    def present_crendetials(self, line):
        did_choices = self.app.get_aliases(_Group.DID)
        if not did_choices:
            err = 'No DIDs found. Must create at least one.'
            raise PresentationError(err)
        holder_did = self.launch_single_choice('Choose holder DID', did_choices)
        vc_choices = self.app.get_credentials_by_did(holder_did)
        if not vc_choices:
            err = 'No credentials found for the provided holder DID'
            raise PresentationError(err)
        selected = self.launch_multiple_choices(
            'Select credentials to verify', vc_choices)
        credentials = [self.app.get_credential(alias) for alias in
            selected]
        if not credentials:
            err = 'Presentation aborted'
            raise PresentationError(err)
        vc_files = []
        for cred in credentials:
            tmpfile = self.dump(cred, '%s.json' % cred['id'])
            vc_files += [tmpfile,]
        try:
            out = self.create_verifiable_presentation(holder_did,
                    vc_files)
        except PresentationError as err:   # TODO: SSI exception?
            raise PresentationError(err)
        return out

    def do_verify(self, line):
        # Produce presentation
        try:
            presentation = self.present_crendetials(line)
        except PresentationError as err:
            self.flush('Could not present: %s' % err)
            return
        # Verify presentation
        self.flush('Verifying (takes seconds)...')
        tmpfile = self.dump(presentation, 'presentation.json')
        res, code = run_cmd([
            'verify-credentials', '--presentation', tmpfile,])
        os.remove(tmpfile)
        if code != 0:
            err = 'Could not verify: %s' % res
            raise VerificationError(err)
        # Parse results
        aux = res.split('Results: ', 1)[-1].replace(':', '').split(' ')
        results = {}
        for i in range(0, len(aux), 2):
            results[aux[i]] = {'true': True, 'false': False}[aux[i + 1]]
        # Flush results
        verified = results['Verified']
        message = 'Presentation was %sverified:' % ('' if verified else 'NOT ')
        self.flush(message)
        self.flush(results)

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
                    self.flush('No DIDs found. Must first create one.')
                    return
                did = self.launch_single_choice('Choose DID', choices)
                # TODO: Choose from known registar of issuers?
                remote = 'http://localhost:7000'
                endpoint = 'api/v1/credentials/issue/'
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
                resp = resp.json()
                if 'message' in resp:           # TODO: Check code instead
                    self.flush(resp['message'])# TODO
                    return
                credential = resp.json()        # TODO: Validate structure
                # TODO: Ask before saving
                self.app.store_credential(credential)
                self.flush('The following credential was saved to disk:')
                self.flush(credential['id'])
            case _Action.VERIFY:
                # choices = self.app.get_aliases(_Group.VC)
                # if not choices:
                #     self.flush('No credentials found')
                #     return
                # alias = self.launch_single_choice('Choose credential', 
                #     choices)
                # credential = self.app.get_entry(alias, _Group.VC)
                # # TODO: Choose from known registar of verifiers?
                # remote = 'http://localhost:7001'
                # endpoint = 'api/v1/credentials/verify/'
                # # TODO: Construction of payload presupposes that an API
                # # spec is known on behalf of the verifier
                # payload = {
                #     'credential': credential,
                # }
                # resp = HttpClient(remote).post(endpoint, payload)
                # # TODO
                # self.flush(resp.json())
                did_choices = self.app.get_aliases(_Group.DID)
                if not did_choices:
                    self.flush('No DIDs found. Must create at least one.')
                    return
                did = self.launch_single_choice('Choose DID', did_choices)
                vc_choices = self.app.get_credentials_by_did(did)
                if not vc_choices:
                    self.flush('No credentials found for the provided DID')
                    return
                selected = self.launch_multiple_choices(
                    'Select credentials to present', vc_choices)
                credentials = [self.app.get_credential(alias) for alias in
                    selected]
                if not credentials:
                    self.flush('Aborted')  # TODO
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
                self.flush('Request aborted')

    def do_export(self, line):
        try:
            group = self._resolve_group(line, prompt='Export from')
        except BadInputError as err:
            self.flush(err)
            return
        aliases = self.app.get_aliases(group)
        if not aliases:
            self.flush('Nothing found')
            return
        alias = self.launch_single_choice('Choose', aliases)
        filename = ''
        while filename in ('', None):
            filename = self.launch_input('Give filename:')
            if filename is not None:
                filename = filename.strip()
        outfile = os.path.join(STORAGE, filename)
        if os.path.isfile(outfile):
            if not self.launch_yes_no('File exists. Overwrite?'):
                self.flush('Aborted')
                return
        with open(outfile, 'w+') as f:
            entry = self.app.get_entry(alias, group)
            json.dump(entry, f, indent=INDENT)
        self.flush('Exported to: %s' % outfile)

    def do_import(self, line):
        infile = self.launch_input('Give absolute path to file:')
        try:
            with open(infile, 'r') as f:
                obj = json.load(f)
        except (FileNotFound, json.decoder.JSONDecodeError) as err:
            self.flush('Could not import: %s' % str(err))
            return
        self.flush('Imported:')
        self.flush(obj)
        yes = self.launch_yes_no('Store in database?')
        if not yes:
            del obj
            self.flush('Imported object deleted from memory')
            return
        group = self.launch_single_choice('Store as', [
            _UI.KEY, _UI.DID, _UI.VC
        ])
        self.app.store(obj, group)

    def do_remove(self, line):
        try:
            group = self._resolve_group(line, prompt='Remove from')
        except BadInputError as err:
            self.flush(err)
            return
        aliases = self.app.get_aliases(group)
        if not aliases:
            self.flush('Nothing found')
            return
        chosen = self.launch_multiple_choices('Choose entries to remove',
            aliases)
        yes = self.launch_yes_no('This cannot be undone. Are you sure?')
        if not yes:
            self.flush('Removal aborted')
            return
        for alias in chosen:
            self.app.remove(alias, group)
            self.flush('Removed %s' % alias)

    def do_clear(self, line):
        try:
            group = self._resolve_group(line, prompt='Clear')
        except BadInputError as err:
            self.flush(err)
            return
        yes = self.launch_yes_no('This cannot be undone. Are you sure?')
        if not yes:
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

