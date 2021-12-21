import sys
from driver import WalletShell
from app import WalletApp
from db import WalletDbConnectionError
from conf import TMPDIR, DBNAME

if __name__ == '__main__':
    try:
        app = WalletApp.create({
            'tmpdir': TMPDIR,
            'dbpath': DBNAME,
        })
    except WalletDbConnectionError as err:
        sys.stdout.write('Could not connect to database: %s\n' \
                % err)
        sys.exit(1)
    WalletShell(app).run()
