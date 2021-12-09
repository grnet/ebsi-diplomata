from django.conf import settings
import subprocess
import json
import os
from ebsi_lib import run_cmd, EbsiApp
from ebsi_lib.conf import _Group, SECP256, ED25519
from ebsi_lib.app import CreationError


class IssuanceError(BaseException):
    pass

class Issuer(EbsiApp):

    def __init__(self, *args):
        super().__init__()
        if any((
            bool(int(os.environ.get('ISSUER_FORCE_DID', default=0))),   # TODO
            self.get_nr(_Group.DID) == 0,
        )):
            algorithm = os.getenv('ISSUER_KEYGEN_ALGO', ED25519)        # TODO
            token = os.getenv('ISSUER_EBSI_TOKEN', '')                  # TODO
            self.clear(_Group.KEY)
            self.clear(_Group.DID)
            key = self.create_key(algorithm)
            try:
                self.create_did(key, token)
            except CreationError as err:
                raise

    @classmethod
    def init_from_app(cls, settings):
        return cls()                                        # TODO

    def get_info(self):
        return {'TODO': 'Include here issuer info'}         # TODO

    def get_did(self):
        dids = self.get_aliases(_Group.DID)
        if not dids:
            out = {'message': 'No DIDs found'}
        else:
            alias = dids[-1]
            out = self.get_entry(alias, _Group.DID)
        return out

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
        res, code = run_cmd([
            os.path.join(settings.APPDIR, 'issuer', 'issue-vc-ni'),
            *vc_content.values(),
        ])
        if code != 0:
            err = 'Could not issue credential: %s' % res
            raise IssuanceError(err)
        tmpfile = res                   # Credential export
        with open(tmpfile, 'r') as f:
            out = json.load(f)
        os.remove(tmpfile)
        return out

