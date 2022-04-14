import os
import json
from urllib.parse import urljoin
import requests
from ssi_lib import SSI, SSIGenerationError, SSIRegistrationError, \
    SSIResolutionError, SSIIssuanceError, SSIVerificationError, \
    Template, Vc
from conf import TMPDIR, DBNAME, EBSI_PRFX, RESOLVED, WALTDIR, \
    Table
from db import DbConnector, DbConnectionError
from conf import API_PREFIX
import conf


class CreationError(Exception):
    pass


class RegistrationError(Exception):
    pass


class ResolutionError(Exception):
    pass


class HttpConnectionError(Exception):
    pass


class IssuanceError(Exception):
    pass


class VerificationError(Exception):
    pass


class HttpClient(object):

    def _create_url(self, remote, endpoint):
        return urljoin(remote, endpoint.lstrip('/'))

    def _do_request(self, method, url, **kw):
        try:
            resp = getattr(requests, method)(url, **kw)
        except requests.exceptions.ConnectionError as err:
            raise HttpConnectionError(err)
        return resp

    def http_get(self, remote, endpoint, querystring={}, headers={}):
        url = self._create_url(remote, endpoint)
        resp = self._do_request('get', url, json={
            'params': querystring,
        }, headers=headers)
        return resp

    def http_post(self, remote, endpoint, payload, headers={}):
        url = self._create_url(remote, endpoint)
        resp = self._do_request('post', url, json=payload, headers=headers)
        return resp

    def parse_http_response(self, resp):
        code = resp.status_code
        body = resp.json()
        return code, body


class WalletApp(SSI, HttpClient):

    def __init__(self, tmpdir, db):
        try:
            self._db = DbConnector(db)
        except DbConnectionError as err:
            err = 'Could not connect to database: %s' % err
            raise RuntimeError(err)
        self.auth_token = None          # TODO: Use secure cache
        super().__init__(tmpdir)

    @classmethod
    def create(cls):
        tmpdir = conf.TMPDIR
        dbname = conf.DBNAME
        return cls(tmpdir, dbname)

    def _fetch_key(self, alias):
        return self._db.fetch_entry(alias, Table.KEY)

    def fetch_aliases(self, table):
        return self._db.fetch_aliases(table)

    def fetch_keys(self):
        return self._db.fetch_aliases(Table.KEY)

    def fetch_dids(self):
        return self._db.fetch_aliases(Table.DID)

    def fetch_credentials(self):
        return self._db.fetch_aliases(Table.VC)

    def fetch_presentations(self):
        return self._db.fetch_aliases(Table.VP)

    def fetch_credentials_by_holder(self, alias):
        return self._db.fetch_credentials_by_holder(
            alias)

    def fetch_nr(self, table):
        return self._db.fetch_nr(table)

    def fetch_nr_keys(self):
        return self._db.fetch_nr(Table.KEY)

    def fetch_nr_dids(self):
        return self._db.fetch_nr(Table.DID)

    def fetch_nr_credentials(self):
        return self._db.fetch_nr(Table.VC)

    def fetch_nr_presentations(self):
        return self._db.fetch_nr(Table.VP)

    def fetch_entry(self, alias, table):
        return self._db.fetch_entry(alias, table)

    def fetch_key(self, alias):
        return self._fetch_key(alias)

    def fetch_did(self, alias):
        return self._db.fetch_entry(alias, Table.DID)

    def fetch_credential(self, alias):
        return self._db.fetch_entry(alias, Table.VC)

    def fetch_presentation(self, alias):
        return self._db.fetch_entry(alias, Table.VP)

    def store_key(self, entry):
        alias = self.extract_alias_from_key(entry)
        return self._db.store_key(alias, entry)

    def store_did(self, entry):
        alias = self.extract_alias_from_did(entry)
        key = self.extract_key_from_did(entry)
        return self._db.store_did(alias, key, entry)

    def store_credential(self, entry):
        alias = self.extract_alias_from_vc(entry)
        holder = self.extract_holder_from_vc(entry)
        return self._db.store_vc(alias, holder, entry)

    def store_presentation(self, entry):
        alias = self.extract_alias_from_vp(entry)
        holder = self.extract_holder_from_vp(entry)
        return self._db.store_vp(alias, holder, entry)

    def store_auth_token(self, token):
        self.auth_token = token         # TODO: Use secure cache

    def get_auth_token(self):
        return self.auth_token          # TODO: Use secure cache

    def clear_auth_token(self):
        self.auth_token = None          # TODO: Use secure cache

    def remove(self, alias, table):
        self._db.remove(alias, table)

    def clear(self, table):
        self._db.clear(table)

    def clear_keys(self):
        self._db.clear(Table.KEY)

    def clear_dids(self):
        self._db.clear(Table.DID)

    def clear_credentials(self):
        self._db.clear(Table.VC)

    def clear_presentations(self):
        self._db.clear(Table.VP)

    def create_key(self, algo):
        try:
            key = self.generate_key(algo)
        except SSIGenerationError as err:
            err = 'Could not generate key: %s' % err
            raise CreationError(err)
        alias = self.store_key(key)
        return alias

    def register_did(self, alias, token):
        try:
            super().register_did(alias, token)
        except SSIRegistrationError as err:
            raise RegistrationError(err)

    def resolve_did(self, alias):
        try:
            super().resolve_did(alias)
        except SSIResolutionError as err:
            raise ResolutionError(err)

    def create_did(self, key, token, onboard=True):
        try:
            did = self.generate_did(key, token, onboard)
        except SSIGenerationError as err:
            err = 'Could not generate DID: %s' % err
            raise CreationError(err)
        if onboard:
            try:
                alias = self.extract_alias_from_did(did)
                super().register_did(alias, token)
            except SSIRegistrationError as err:
                err = 'Could not register: %s' % err
                raise CreationError(err)
        alias = self.store_did(did)
        return alias

    def retrieve_resolved_did(self, alias):
        resolved = os.path.join(RESOLVED, 'did-ebsi-%s.json' %
                                alias.lstrip(EBSI_PRFX))
        with open(resolved, 'r') as f:
            did = json.load(f)
        return did

    def prepare_issuance_payload(self, holder, subject):
        return {
            'holder': holder,
            'vc_type': Vc.DIPLOMA,
            'content': {
                'subject': subject,
            }
        }

    def mock_issuer(self, issuer, payload):
        holder = payload['holder']
        vc_type = payload['vc_type']
        content = payload['content']
        # Normalize diploma content according to template
        aux = content
        content = getattr(Template, Vc.DIPLOMA)
        content['person_identifier'] = aux['person_id']
        content['person_family_name'] = aux['name']
        content['person_given_name'] = aux['surname']
        content['awarding_opportunity_identifier'] = aux['subject']
        # Issue and return diploma
        out = self.issue_credential(holder, issuer, vc_type,
                                    content)
        return out

    def request_issuance(self, remote, endpoint, holder, subject):
        payload = self.prepare_issuance_payload(holder, subject)
        token = self.get_auth_token()
        resp = self.http_post(remote, endpoint, payload, headers={
            'Authorization': 'Token %s' % token,
        })
        return resp

    def create_presentation(self, holder, credentials,
                            waltdir=WALTDIR):
        try:
            vp = self.generate_presentation(holder, credentials,
                                            waltdir)
        except SSIGenerationError as err:
            err = 'Could not generate presentation: %s' % err
            raise CreationError(err)
        alias = self.store_presentation(vp)
        return alias

    def verify_presentation(self, vp):
        try:
            results = super().verify_presentation(vp)
        except SSIVerificationError as err:
            raise VerificationError(err)
        return results

    def request_verification(self, remote, endpoint, presentation):
        payload = {'presentation': presentation}
        resp = self.http_post(remote, endpoint, payload)
        return resp

    def request_auth_token(self, remote, code):
        resp = self.http_get(
            remote, f'{API_PREFIX}/token/?code=%s' % str(code))
        return resp

    def request_user(self, remote):
        token = self.get_auth_token()
        resp = self.http_get(remote, f'{API_PREFIX}/users/current/', headers={
            'Authorization': 'Token %s' % token,
        })
        return resp
