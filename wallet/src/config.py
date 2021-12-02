import os

STORAGE = os.getenv('STORAGE')
TMPDIR  = os.path.join(STORAGE, 'tmp')

DBNAME  = 'db.json'
DBCONF  = {
    'sort_keys': True,
    'indent': 4,
    'separators': [',', ': '],
}

INTRO   = "Type help or ? to list commands.\n"
PROMPT  = "(wallet) "

class _Group:
    KEY = 'key'
    DID = 'did'
    VC  = 'vc'

class _Action:
    ISSUE   = 'ISSUE'
    VERIFY  = 'VERIFY'
    DISCARD = 'DISCARD'

class _UI:
    KEY = 'Keys'
    DID = 'DIDs'
    VC  = 'Credentials'
    ISSUE   = 'issuance'
    VERIFY  = 'verification'
    DISCARD = 'discard'

