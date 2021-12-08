import os

STORAGE     = os.getenv('STORAGE')
HOMEDIR     = os.getenv('HOMEDIR')
TMPDIR      = os.getenv('TMPDIR')
WALTDIR     = os.getenv('WALTDIR')
RESOLVED    = os.path.join(WALTDIR, 'data/did/resolved')

DBNAME  = 'db.json'
DBCONF  = {
    'sort_keys': True,
    'indent': 4,
    'separators': [',', ': '],
}

INDENT  = 4

ED25519 = 'Ed25519'
SECP256 = 'Secp256k1'

EBSI_PRFX = "did:ebsi"

class _Group:
    KEY = 'key'
    DID = 'did'
    VC  = 'vc'

class _Action:
    ISSUE   = 'ISSUE'
    VERIFY  = 'VERIFY'
    DISCARD = 'DISCARD'

class _UI:
    KEY     = 'key'
    KEYS    = 'keys'
    DID     = 'DID'
    DIDS    = 'DIDs'
    VC      = 'credential'
    VCS     = 'credentials'
    ISSUE   = 'issuance'
    VERIFY  = 'verification'
    DISCARD = 'discard'

