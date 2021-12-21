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

