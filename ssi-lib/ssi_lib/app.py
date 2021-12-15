import os
import json
import subprocess
from .db import DbConnector
from .conf import _Group, _Vc


class SSIGenerationError(BaseException):
    pass

class SSIRegistrationError(BaseException):
    pass

class SSIResolutionError(BaseException):
    pass

class SSIIssuanceError(BaseException):
    pass

class SSIVerificationError(BaseException):
    pass

_commands = {
    _Vc.DIPLOMA: 'issue-diploma',
    # TODO: Add here more options
}

def run_cmd(args):
    rslt = subprocess.run(args, stdout=subprocess.PIPE)
    resp = rslt.stdout.decode('utf-8').rstrip('\n')
    code = rslt.returncode
    return (resp, code)


class SSIApp(object):

    def __init__(self, dbpath, tmpdir):
        self._db = DbConnector(dbpath)
        self.tmpdir = tmpdir

    @classmethod
    def create(cls, config):
        dbpath = config['db']
        tmpdir = config['tmp']
        return cls(dbpath, tmpdir)

    def _generate_key(self, algo, outfile):
        res, code = run_cmd([
            'generate-key', '--algo', algo, '--export', outfile,
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

    def _issue_credential(self, holder, issuer, command, arguments,
            outfile):
        res, code = run_cmd([
            command,
            '--holder', holder,
            '--issuer', issuer,
            '--export', outfile,
            *arguments,
        ])
        return res, code

    def _generate_presentation(self, holder, credentials):
        args = ['present-credentials', '--holder', holder]
        for credential in credentials:
            args += ['-c', credential,]
        res, code = run_cmd(args)
        return res, code

    def _verify_presentation(self, presentation):
        tmpfile = os.path.join(self.tmpdir, 'vp.json')
        with open(tmpfile, 'w+') as f:
            json.dump(presentation, f)
        res, code = run_cmd([
            'verify-credentials', '--presentation', tmpfile,])
        os.remove(tmpfile)
        return res, code

    def get_aliases(self, group):
        return self._db.get_aliases(group)

    def get_keys(self):
        return self._db.get_aliases(_Group.KEY)

    def get_dids(self):
        return self._db.get_aliases(_Group.DID)

    def get_credentials(self):
        return self._db.get_aliases(_Group.VC)

    def get_presentations(self):
        return self._db.get_aliases(_Group.VP)

    def get_credentials_by_did(self, alias):
        return self._db.get_credentials_by_did(alias)

    def get_nr(self, group):
        return self._db.get_nr(group)

    def get_nr_keys(self):
        return self._db.get_nr(_Group.KEY)

    def get_nr_dids(self):
        return self._db.get_nr(_Group.DID)

    def get_nr_credentials(self):
        return self._db.get_nr(_Group.VC)

    def get_nr_presentations(self):
        return self._db.get_nr(_Group.VP)

    def get_entry(self, alias, group):
        return self._db.get_entry(alias, group)

    def get_key(self, alias):
        return self._db.get_entry(alias, _Group.KEY)

    def get_did(self, alias):
        return self._db.get_entry(alias, _Group.DID)

    def get_credential(self, alias):
        return self._db.get_entry(alias, _Group.VC)

    def get_presentation(self, alias):
        return self._db.get_entry(alias, _Group.VP)

    def store(self, obj, group):
        return self._db.store(obj, group)

    def store_key(self, obj):
        return self._db.store(obj, _Group.KEY)

    def store_did(self, obj):
        return self._db.store(obj, _Group.DID)

    def store_credential(self, obj):
        return self._db.store(obj, _Group.VC)

    def store_presentation(self, obj):
        return self._db.store(obj, _Group.VP)

    def remove(self, alias, group):
        self._db.remove(alias, group)

    def clear(self, group):
        self._db.clear(group)

    def clear_keys(self):
        self._db.clear(_Group.KEY)

    def clear_dids(self):
        self._db.clear(_Group.DID)

    def clear_credentials(self):
        self._db.clear(_Group.VC)

    def clear_presentations(self):
        self._db.clear(_Group.VP)

    def generate_key(self, algo):
        outfile = os.path.join(self.tmpdir, 'jwk.json')
        res, code = self._generate_key(algo, outfile)
        if code != 0:
            raise SSIGenerationError(res)
        with open(outfile, 'r') as f:
            out = json.load(f)
        os.remove(outfile)
        return out

    def generate_did(self, key, token, onboard=True):
        res, code = self._load_key(key)
        if code != 0:
            err = 'Could not load key: %s' % res
            raise SSIGenerationError(err)
        outfile = os.path.join(self.tmpdir, 'did.json')
        res, code = self._generate_did(key, outfile)
        if code != 0:
            raise SSIGenerationError(res)
        with open(outfile, 'r') as f:
            out = json.load(f)
        os.remove(outfile)
        return out

    def register_did(self, alias, token):
        if not token:
            err = 'No token provided'
            raise SSIRegistrationError(err)
        res, code = self._register_did(alias, token)
        if code != 0:
            raise SSIRegistrationError(res)

    def resolve_did(self, alias):
        res, code = self._resolve_did(alias)
        if code != 0:
            raise SSIResolutionError(res)

    def _complete_credentials_form(self, template, content):
        match template:
            case _Vc.DIPLOMA:
                # TODO: Issuer should here complete the following form by
                # comparing the submitted content against its database. Empty 
                # strings lead to the demo defaults of the walt-ssi library. 
                # IMPORTANT: Order of key-value pairs matters!!!
                form = {
                    'person_identifier': content['person_id'],
                    'person_family_name': content['name'],
                    'person_given_name': content['surname'],
                    'person_date_of_birth': '',
                    'awarding_opportunity_id': '',
                    'awarding_opportunity_identifier': content['subject'],
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
            case _:
                raise NotImplementedError('TODO')
        arguments = form.values()
        return arguments

    def issue_credential(self, holder, issuer, template, content):
        command = _commands[template]
        arguments = self._complete_credentials_form(template, content)
        outfile = os.path.join(self.tmpdir, 'vc.json')
        res, code = self._issue_credential(holder, issuer,
                command, arguments, outfile)
        if code != 0:
            raise SSIIssuanceError(res)
        with open(outfile, 'r') as f:
            out = json.load(f)
        os.remove(outfile)
        return out

    def generate_presentation(self, holder, credentials, waltdir):
        res, code = self._generate_presentation(holder, credentials)
        if code != 0:
            raise SSIGenerationError(res)
        sep = 'Verifiable presentation was saved to file: '
        if not sep in res:
            raise SSIGenerationError(res)
        filename = res.split(sep)[-1].replace('"', '')
        outfile = os.path.join(waltdir, filename)
        with open(outfile, 'r') as f:
            out = json.load(f)
        os.remove(outfile)
        for tmpfile in credentials:
            os.remove(tmpfile)
        return out

    def verify_presentation(self, presentation):
        res, code = self._verify_presentation(presentation)
        if code != 0:
            raise SSIVerificationError(res)
        # Parse results
        aux = res.split('Results: ', 1)[-1].replace(':', '').split(' ')
        results = {}
        for i in range(0, len(aux), 2):
            results[aux[i]] = {'true': True, 'false': False}[aux[i + 1]]
        return results
