import os

STORAGE = os.getenv('STORAGE')
HOMEDIR = os.getenv('HOMEDIR')
TMPDIR  = os.getenv('TMPDIR')

DBNAME  = 'db.json'
DBCONF  = {
    'sort_keys': True,
    'indent': 4,
    'separators': [',', ': '],
}

PROMPT  = "(wallet) "
INTRO = """\

Interactive shell for EBSI-Diplomata Wallet v{}
--------------------------------------------------

Type `q` or `Ctrl-D` to quit.
Type `help` or `?` for an overview 
Type `help <command>` for details
"""
INDENT  = 4

ED25519 = 'Ed25519'
SECP256 = 'Secp256k1'

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

