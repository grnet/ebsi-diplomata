import os

STORAGE     = os.getenv('STORAGE')
HOMEDIR     = os.getenv('HOMEDIR')
TMPDIR      = os.getenv('TMPDIR')
WALTDIR     = os.getenv('WALTDIR')
RESOLVED    = os.path.join(WALTDIR, 'data/did/resolved')
DBNAME      = os.getenv('DBNAME')
EBSI_PRFX   = 'did:ebsi'
Ed25519     = 'Ed25519'
Secp256k1   = 'Secp256k1'
RSA         = 'RSA'

class Table:
    KEY     = 'key'
    DID     = 'did'
    VC      = 'vc'
    VP      = 'vp'


ISSUER_ADDRESS      = 'http://localhost:7000'
VERIFIER_ADDRESS    = 'http://localhost:7001'

API_PREFIX          = 'api/v1'

ISSUE_ENDPOINT      = f'{API_PREFIX}/credentials/issue/'
LOGIN_ENDPOINT      = f'{API_PREFIX}/google/login/'
TOKEN_ENDPOINT      = f'{API_PREFIX}/token/?code=%s'
VERIFY_ENDPOINT     = f'{API_PREFIX}/credentials/verify/'
