import os
import json
import logging
from django.conf import settings
from ssi_lib import SSI, SSIGenerationError, SSIRegistrationError, \
    SSIResolutionError, SSIIssuanceError, SSIVerificationError, \
    Template, Vc
from core.models import Alumnus, Credential


class IdentityError(Exception):
    pass


class CreationError(Exception):
    pass


class IssuanceError(Exception):
    pass


class VerificationError(Exception):
    pass


VAULT = settings.STORAGE    # TOOD: Use an encrypted secure data vault
KEYFILE = os.path.join(VAULT, 'jwk.json')
DIDFILE = os.path.join(VAULT, 'did.json')

_ssi = SSI(settings.TMPDIR)


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
    out = _ssi.extract_alias_from_did(did) if not full \
        else did
    return out


def _store_key(entry):
    alias = _ssi.extract_alias_from_key(entry)
    with open(KEYFILE, 'w+') as f:
        json.dump(entry, f, indent=4)
    return alias


def _store_did(entry):
    alias = _ssi.extract_alias_from_did(entry)
    with open(DIDFILE, 'w+') as f:
        json.dump(entry, f, indent=4)
    return alias


def _generate_key(algo):
    logging.info('Generating %s key (takes seconds) ...' % algo)
    try:
        key = _ssi.generate_key(algo)
    except SSIGenerationError as err:
        raise
    return key


def _generate_did(key, token, onboard=True):
    logging.info('Generating DID (takes seconds) ...')
    try:
        did = _ssi.generate_did(key, token, onboard,
                                load_key=False)  # TODO
    except SSIGenerationError as err:
        raise
    if onboard:
        logging.info('Registering DID to EBSI (takes seconds)...')
        try:
            alias = _ssi.extract_alias_from_did(did)
            _ssi.register_did(alias, token)
        except SSIRegistrationError as err:
            raise
        logging.info('DID registered to EBSI')
    return did


def _normalize_diploma_content(user_data, content):
    # Issuer should here compare the submitted content and retrieved user data
    # against the database and accordingly resolve the content of the diploma
    # to be issued (This typically means transformation and completion of the
    # provided content).
    # TODO: Unaltered values of the original template (empty strings) lead
    # during issuance to the default demo values of the walt-ssikit backend.
    # This does not affect cryptographic correctness and protocol execution but
    # evidently leads to credentials that do not correspond to reality. Make
    # sure that all pairs of the original template are visited and properly
    # modified within the present reality context.
    out = getattr(Template, Vc.DIPLOMA)
    out['person_identifier'] = user_data['afm']
    out['person_family_name'] = user_data['last_name']
    out['person_given_name'] = user_data['first_name']
    out['person_date_of_birth'] = user_data['birthdate'] or ''
    out['awarding_opportunity_identifier'] = content['subject']
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


def issue_credential(holder, vc_type, content, user_data):
    issuer = _fetch_did(full=False)
    if not issuer:
        err = 'No issuer DID found'
        raise IssuanceError(err)
    try:
        content = _normalize_diploma_content(user_data, content)
    except KeyError as err:
        err = 'Malformed diploma content provided: %s' % err
        raise IssuanceError(err)
    try:
        vc = _ssi.issue_credential(holder, issuer, vc_type,
                                   content)
    except SSIIssuanceError as err:
        raise IssuanceError(err)
    try:
        # TODO: Should detect via DID
        alumnus = Alumnus.objects.get(extern_id=user_data['extern_id'])
    except Alumnus.DoesNotExist as err:
        err = 'Could not detect alumnus: %s' % err
        raise IssuanceError(err)
    Credential.objects.create(holder=alumnus, body=vc)
    return vc


def verify_presentation(vp):
    try:
        out = _ssi.verify_presentation(vp)
    except SSIVerificationError as err:
        raise VerificationError(err)
    return out
