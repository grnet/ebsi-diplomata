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
ISSUE_ENDPOINT      = 'api/v1/credentials/issue/'
VERIFIER_ADDRESS    = 'http://localhost:7001'
VERIFY_ENDPOINT     = 'api/v1/credentials/verify/'


