import sys
from driver import WalletShell
from app import WalletApp
from db import WalletDbConnectionError
import conf

if __name__ == '__main__':
    try:
        app = WalletApp.create({
            'tmpdir': conf.TMPDIR,
            'dbpath': conf.DBNAME,
        })
    except WalletDbConnectionError as err:
        sys.stdout.write('Could not connect to database: %s\n' \
                % err)
        sys.exit(1)
    WalletShell(app).run()
