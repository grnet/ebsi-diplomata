import os
from driver import WalletShell
from conf import STORAGE, DBNAME, TMPDIR
from ssi_lib import SSIApp

if __name__ == '__main__':
    app = SSIApp.create({
        'db': os.path.join(STORAGE, DBNAME),
        'tmp': TMPDIR
    })
    WalletShell(app).run()

