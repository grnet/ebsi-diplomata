import os

STORAGE     = os.getenv('STORAGE')
HOMEDIR     = os.getenv('HOMEDIR')
TMPDIR      = os.getenv('TMPDIR')
WALTDIR     = os.getenv('WALTDIR')
RESOLVED    = os.path.join(WALTDIR, 'data/did/resolved')

DBNAME  = os.getenv('DBNAME')

EBSI_PRFX   = 'did:ebsi'

Ed25519     = 'Ed25519'
Secp256k1   = 'Secp256k1'
RSA         = 'RSA'

PROMPT  = "(wallet) "
INTRO = """\

Interactive shell for EBSI-Diplomata Wallet v{}
--------------------------------------------------

Type `q` or `Ctrl-D` to quit.
Type `help` or `?` for an overview 
Type `help <command>` for details
"""
INDENT  = 4

class Action:
    ISSUE   = 'ISSUE'
    VERIFY  = 'VERIFY'
    CHOOSE  = 'CHOOSE'
    IMPORT  = 'IMPORT'
    DISCARD = 'DISCARD'

class Table:
    KEY     = 'key'
    DID     = 'did'
    VC      = 'vc'
    VP      = 'vp'

class UI:
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
    CHOOSE  = 'Choose from database'
    IMPORT  = 'Import from file'
    DISCARD = 'discard'

