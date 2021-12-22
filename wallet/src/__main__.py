import sys
from app import WalletApp
from db import DbConnectionError
from conf import TMPDIR, DBNAME
from driver import WalletShell

if __name__ == '__main__':
    try:
        app = WalletApp(TMPDIR, DBNAME)
    except RuntimeError as err:
        sys.stdout.write('%s\n' % err)
        sys.exit(1)
    WalletShell(app).run()
