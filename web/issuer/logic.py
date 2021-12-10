from django.conf import settings
import subprocess
import json
import os

from ssi_lib.walt import run_cmd
from ssi_lib import SSIApp, SSICreationError


class IssuanceError(BaseException):     # TODO
    pass

class IdentityError(BaseException):     # TODO
    pass


class Issuer(SSIApp):

    def __init__(self, *args):
        super().__init__(
            dbpath=os.path.join(settings.STORAGE, 'db.json'),           # TODO
            tmpdir=settings.TMPDIR,                                     # TODO
        )
        if any((
            bool(int(os.environ.get('ISSUER_FORCE_DID', default=0))),   # TODO
            self.get_nr_dids() == 0,
        )):
            algo = os.getenv('ISSUER_KEYGEN_ALGO')
            token = os.getenv('ISSUER_EBSI_TOKEN', '')                  # TODO
            self.clear_keys()
            self.clear_dids()
            key = self.create_key(algo)
            try:
                self.create_did(key, token)
            except SSICreationError as err:
                raise

    @classmethod
    def init_from_app(cls, settings):
        return cls()                                        # TODO

    def get_info(self):
        return {'TODO': 'Include here issuer info'}         # TODO

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
        tmpfile = os.path.join(TMPDIR, 'vc.json')
        res, code = run_cmd([
            os.path.join(settings.APPDIR, 'issuer', 'issue-credential-ni'), # TODO
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

