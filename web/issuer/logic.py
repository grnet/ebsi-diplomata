from django.conf import settings
import subprocess
import json
import os
from .ebsi_lib import run_cmd


def get_did(nr=None, no_ebsi_prefix=False):
    args = ['get-did',]
    if nr:
        args += ['--nr', str(nr)]
    resp, code = run_cmd(args)
    if no_ebsi_prefix:
        resp = resp.lstrip(settings.EBSI_PRFX)
    return (resp, code)

class IssuanceError(BaseException):
    pass

class Issuer(object):

    @classmethod
    def init_from_app(cls, settings):
        return cls()                                        # TODO

    def get_info(self):
        return {'TODO': 'Include here issuer info'}         # TODO

    def get_did(self):
        resp, code = get_did()                              # TODO
        # TODO
        if code == 0:
            _path = os.path.join(settings.STORAGE, 'did', 
                '1', 'repr.json')                           # TODO
            with open(_path, 'r') as f:
                out = json.load(f)
        else:
            out = {'error': resp}
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

