PROMPT  = "(wallet) "
INTRO   = """\

Interactive shell for EBSI-Diplomas Wallet v{}
-------------------------------------------------

Type `q` or `Ctrl-D` to quit.
Type `help` or `?` for overview 
Type `help <command>` for details
"""

INDENT  = 4

class Action:
    ISSUE   = 'ISSUE'
    VERIFY  = 'VERIFY'
    CHOOSE  = 'CHOOSE'
    IMPORT  = 'IMPORT'
    DISCARD = 'DISCARD'

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

