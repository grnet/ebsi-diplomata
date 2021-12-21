import os
import json
import logging
from django.conf import settings
from ssi_lib import SSIApp, SSIGenerationError, SSIRegistrationError, \
    SSIResolutionError, SSIIssuanceError, SSIVerificationError, \
    SSIVcContentError, Template, Vc


class IdentityError(BaseException):
    pass

class CreationError(BaseException):
    pass

class IssuanceError(BaseException):
    pass

class VerificationError(BaseException):
    pass


VAULT = settings.STORAGE    # TOOD: Use an encrypted secure data vault
KEYFILE = os.path.join(VAULT, 'jwk.json')   # TODO
DIDFILE = os.path.join(VAULT, 'did.json')   # TODO

app = SSIApp(settings.TMPDIR)

def _fetch_key():
    try:
        with open(KEYFILE, 'r') as f:
            out = json.load(f)
    except FileNotFoundError:
        return None
    return out

def _fetch_did(full=False):
    try:
        with open(DIDFILE, 'r') as f:
            did = json.load(f)
    except FileNotFoundError:
        return None
    out = app.extract_alias_from_did(did) if not full \
            else did
    return out

def _store_key(entry):
    alias = app.extract_alias_from_key(entry)
    with open(KEYFILE, 'w+') as f:
        json.dump(entry, f, indent=4)
    return alias

def _store_did(entry):
    alias = app.extract_alias_from_did(entry)
    with open(DIDFILE, 'w+') as f:
        json.dump(entry, f, indent=4)
    return alias

def _generate_key(algo):
    logging.info('Generating %s key (takes seconds) ...' % algo)
    try:
        key = app.generate_key(algo)
    except SSIGenerationError as err:
        raise
    return key

def _generate_did(key, token, onboard=True):
    logging.info('Generating DID (takes seconds) ...')
    try:
        did = app.generate_did(key, token, onboard, 
                load_key=False) # TODO
    except SSIGenerationError as err:
        raise
    if onboard:
        logging.info('Registering DID to EBSI (takes seconds)...')
        try:
            alias = app.extract_alias_from_did(did)
            app.register_did(alias, token)
        except SSIRegistrationError as err:
            raise
        logging.info('DID registered to EBSI')
    return did

def _adapt_credential_content(vc_type, content):
    try:
        # TODO: Remove this
        template = app.resolve_template(vc_type)
    except SSIVcContentError:
        raise
    out = template
    match vc_type:
        case Vc.DIPLOMA:
            # TODO
            out['person_identifier'] = content['person_id']
            out['person_family_name'] = content['name']
            out['person_given_name'] = content['surname']
            out['awarding_opportunity_identifier'] = content['subject']
        case _:
            err = 'Requested credential type does not exist: %s' % vc_type
            raise SSIVcContentError(err)
    return out

def fetch_did():
    alias = _fetch_did(full=False)
    if not alias:
        err = 'No DID found'
        raise IdentityError(err)
    return alias

def create_did(token, algo, onboard):
    try:
        key = _generate_key(algo)
    except SSIGenerationError as err:
        err = 'Could not generate key: %s' % err
        raise CreationError(err)
    alias = _store_key(key)
    logging.info('Created key %s' % alias)
    try:
        did = _generate_did(alias, token, onboard)
    except SSIGenerationError as err:
        err = 'Could not generate DID: %s' % err
        raise CreationError(err)
    except SSIRegistrationError as err:
        err = 'Could not generate DID: %s' % err
        raise CreationError(err)
    alias = _store_did(did)
    logging.info('Created DID %s' % alias)
    return alias

def issue_credential(holder, vc_type, content):
    issuer = _fetch_did(full=False)
    if not issuer:
        err = 'No issuer DID found'
        raise IssuanceError(err)
    try:
        content = _adapt_credential_content(vc_type, 
                content)
    except SSIVcContentError as err:
        raise IssuanceError(err)
    try:
        out = app.issue_credential(holder, issuer, vc_type,
                content)
    except SSIIssuanceError as err:
        raise IssuanceError(err)
    return out

def verify_presentation(vp):
    try:
        out = app.verify_presentation(vp)
    except SSIVerificationError as err:
        raise VerificationError(err)
    return out
