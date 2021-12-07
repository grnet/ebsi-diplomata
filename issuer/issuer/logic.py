from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import json
import os


EBSI_PREFIX = 'did:ebsi:'
EBSI_DIR    = os.path.join(settings.WALTDIR, 'data', 'ebsi')
APPSCRIPTS  = os.path.join(settings.APPDIR, 'scripts')

def run_cmd(args):
    result = subprocess.run(args, stdout=subprocess.PIPE)
    resp = result.stdout.decode('utf-8').rstrip('\n')
    code = result.returncode
    return (resp, code)

def get_did(nr=None, no_ebsi_prefix=False):
    args = ['get-did',]
    if nr:
        args += ['--nr', str(nr)]
    resp, code = run_cmd(args)
    if no_ebsi_prefix:
        resp = resp.lstrip(EBSI_PREFIX)
    return (resp, code)

def issue_vc(*args,):
    resp, code = run_cmd([
        os.path.join(APPSCRIPTS, 'issue-vc-ni.sh'),
        *args,
    ])
    return (resp, code)

def get_did_resource(did, resource):
    with open(os.path.join(EBSI_DIR, did, f'{resource}.json'), 
        'r') as f:
        if resource == 'ebsi_access_token':
            out = f.read()
        else:
            out = json.load(f)
    return out

def resolve_vc_args(payload):
    holder_did = payload['did']
    # TODO: Issuer should here check credentials against the payload
    # submitted by the holder and appropriately fill the following template
    vc_payload = {
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
    vc_args = list(vc_payload.values()) # TODO
    return vc_args


class Issuer(object):

    @classmethod
    def init_from_app(cls, settings):
        return cls()                                        # TODO

    def get_info(self):
        return {'TODO': 'Include here issuer info'}

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

    def issue_credentials(self, payload):
        args = resolve_vc_args(payload)
        resp, code = issue_vc(*args)
        out = {}
        # TODO
        if code == 0:
            vc_file = resp
            with open(vc_file, 'r') as f:
                out = json.load(f)
        else:
            out['error'] = resp
        return out
