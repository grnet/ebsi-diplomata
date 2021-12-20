import os
import json
import subprocess
from abc import ABCMeta, abstractmethod
from .conf import Vc, Template


class SSIGenerationError(BaseException):
    pass

class SSIRegistrationError(BaseException):
    pass

class SSIResolutionError(BaseException):
    pass

class SSIContentError(BaseException):
    pass

class SSIIssuanceError(BaseException):
    pass

class SSIVerificationError(BaseException):
    pass

_commands = {
    Vc.DIPLOMA: 'issue-diploma',
    # TODO: Add here more options
}

def run_cmd(args):
    rslt = subprocess.run(args, stdout=subprocess.PIPE)
    resp = rslt.stdout.decode('utf-8').rstrip('\n')
    code = rslt.returncode
    return (resp, code)


class SSIApp(metaclass=ABCMeta):

    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def _extract_alias_from_key(self, entry):
        return entry['kid']

    def _extract_alias_from_did(self, entry):
        return entry['id']

    def _extract_key_from_did(self, entry):
        return entry['verificationMethod'][0]['publicKeyJwk']['kid']

    def _extract_alias_from_vc(self, entry):
        return entry['id']

    def _extract_holder_from_vc(self, entry):
        return entry['credentialSubject']['id']

    def _extract_alias_from_vp(self, entry):
        return entry['id']

    def _extract_holder_from_vp(self, entry):
        return entry['holder']

    def _generate_key(self, algo, outfile):
        res, code = run_cmd([
            'generate-key', '--algo', algo, '--export', outfile,
        ])
        return res, code

    @abstractmethod
    def _fetch_key(self, *args):
        """This depends on the number of asymmetric keys and the way they are
        stored (e.g., an issuer can have one key stored in a data vault while
        a holder owns multiple keys stored in their wallet's database)"""

    def _load_key(self, *args):
        outfile = os.path.join(self.tmpdir, 'jwk.json')
        entry = self._fetch_key(*args)
        if entry:
            with open(outfile, 'w+') as f:
                json.dump(entry, f)
            res, code = run_cmd(['load-key', '--file', outfile,])
            os.remove(outfile)
        else:
            res = 'No key found'
            code = 1
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

    def _validate_vc_content(self, vc_type, content):
        try:
            template = getattr(Template, vc_type)
        except AttributeError as err:
            err = 'Requested credential type does not exist: %s' % vc_type
            raise SSIContentError(err)
        if not template.keys() == content.keys():
            err = 'Provided credential content has wrong key-value pairs'
            raise SSIContentError(err)

    def _issue_vc(self, holder, issuer, vc_type, content, outfile):
        res, code = run_cmd([
            _commands[vc_type],
            '--holder', holder,
            '--issuer', issuer,
            '--export', outfile,
            *content.values(),
        ])
        return res, code

    def _present_credentials(self, holder, credentials):
        args = ['present-credentials', '--holder', holder,]
        for credential in credentials:
            args += ['-c', credential,]
        res, code = run_cmd(args)
        return res, code

    def _extract_presentation_filename(self, buff):
        sep = 'Verifiable presentation was saved to file: '
        if not sep in buff:
            return None
        out = buff.split(sep)[-1].replace('"', '')
        return out

    def _verify_presentation(self, presentation):
        tmpfile = os.path.join(self.tmpdir, 'vp.json')
        with open(tmpfile, 'w+') as f:
            json.dump(presentation, f)
        res, code = run_cmd([
            'verify-credentials', '--presentation', tmpfile,])
        os.remove(tmpfile)
        return res, code

    def _parse_verification_results(self, buff):
        aux = buff.split('Results: ', 1)[-1].replace(':', '').split(' ')
        out = {}
        for i in range(0, len(aux), 2):
            out[aux[i]] = {'true': True, 'false': False}[aux[i + 1]]
        return out

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

    def issue_credential(self, holder, issuer, vc_type, content):
        try:
            self._validate_vc_content(vc_type, content)
        except SSIContentError as err:
            err = 'Invalid credential content provided: %s' % err
            raise SSIIssuanceError(err)
        outfile = os.path.join(self.tmpdir, 'vc.json')
        res, code = self._issue_vc(holder, issuer, vc_type, content,
                outfile)
        if code != 0:
            raise SSIIssuanceError(res)
        with open(outfile, 'r') as f:
            out = json.load(f)
        os.remove(outfile)
        return out

    def generate_presentation(self, holder, credentials, waltdir):
        res, code = self._present_credentials(holder, credentials)
        if code != 0:
            raise SSIGenerationError(res)
        filename = self._extract_presentation_filename(res)
        if not filename:
            raise SSIGenerationError(res)
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
        out = self._parse_verification_results(res)
        return out
