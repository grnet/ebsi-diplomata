import os

STORAGE     = os.getenv('STORAGE')
HOMEDIR     = os.getenv('HOMEDIR')
TMPDIR      = os.getenv('TMPDIR')
WALTDIR     = os.getenv('WALTDIR')
RESOLVED    = os.path.join(WALTDIR, 'data/did/resolved')

DBNAME  = 'db.json'

EBSI_PRFX = "did:ebsi"
ED25519 = 'Ed25519'
SECP256 = 'Secp256k1'

PROMPT  = "(wallet) "
INTRO = """\

Interactive shell for EBSI-Diplomata Wallet v{}
--------------------------------------------------

Type `q` or `Ctrl-D` to quit.
Type `help` or `?` for an overview 
Type `help <command>` for details
"""
INDENT  = 4

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
    VP      = 'presentation'
    VPS     = 'presentations'
    ISSUE   = 'issuance'
    VERIFY  = 'verification'
    DISCARD = 'discard'

