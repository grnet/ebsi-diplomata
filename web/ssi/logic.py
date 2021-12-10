from django.conf import settings
import subprocess
import json
import os

from ssi_lib.walt import run_cmd                # TODO
from ssi_lib import SSIApp, SSICreationError


class IdentityError(BaseException):     # TODO
    pass

class IssuanceError(BaseException):     # TODO
    pass


class SSIParty(SSIApp):

    def __init__(self, dbpath, tmpdir, algo, token='',
            force_did=False):
        super().__init__(dbpath, tmpdir)
        if self.get_nr_dids() == 0 or force_did:
            self.clear_keys()
            self.clear_dids()
            key = self.create_key(algo)
            self.create_did(key, token)

    @classmethod
    def init_from_app(cls, settings):
        config = cls.derive_config(settings)
        return cls.create(config)

    @classmethod
    def create(cls, config):
        dbpath = config['dbpath']
        tmpdir = config['tmpdir']
        algo = config['algo']
        token = config.get('token', '')
        force_did = config.get('force_did', False)
        return cls(dbpath, tmpdir, algo, token, force_did)

    @classmethod
    def derive_config(cls, settings):
        out = {}
        dbpath = os.path.join(settings.STORAGE, 'db.json')      # TODO
        tmpdir = settings.TMPDIR
        algo = os.environ.get('KEYGEN_ALGO', 'Ed25519')         # TODO
        token = os.environ.get('EBSI_TOKEN', '')                # TODO
        force_did = bool(int(os.environ.get('FORCE_DID',
            default=0)))                                        # TODO
        out['dbpath'] = dbpath
        out['tmpdir'] = tmpdir
        out['algo'] = algo
        out['token'] = token
        out['force_did'] = force_did
        return out

    def get_info(self):
        return {'TODO': 'Include here service info'}        # TODO

    def get_did(self, full=False):                          # TODO
        dids = self.get_dids()
        if not dids:
            err = 'No DID found'
            raise IdentityError(err)
        alias = dids[-1]
        if not full:
            return alias
        return super().get_did(alias)

    def issue_credential(self, payload):
        # TODO: Issuer should here fill the following template by comparing the
        # submitted payload against its database. Empty strings lead to the
        # demo defaults of the walt library. 
        vc_content = {
            'holder_did': payload['did'],
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
        # TODO
        tmpfile = os.path.join(settings.TMPDIR, 'vc.json')
        res, code = run_cmd([
            os.path.join(settings.APPDIR, 'ssi',
                'issue-credential-ni.sh'), # TODO
            *vc_content.values(),   # TODO
            self.get_did(),         # TODO
            tmpfile,                # TODO
        ])
        if code != 0:
            err = 'Could not issue credential: %s' % res
            raise IssuanceError(err)
        with open(tmpfile, 'r') as f:
            out = json.load(f)
        os.remove(tmpfile)
        return out

