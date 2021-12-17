import os
import sys
from driver import WalletShell
from app import WalletApp
from db import WalletDbConnectionError
from conf import STORAGE, DBNAME, TMPDIR

if __name__ == '__main__':
    try:
        app = WalletApp.create({
            'db': os.path.join(STORAGE, DBNAME),
            'tmp': TMPDIR
        })
    except WalletDbConnectionError as err:    # TODO
        err = 'Could not connect to database: %s' % err
        sys.stdout.write('%s\n' % err)
        sys.exit(1)
    WalletShell(app).run()

