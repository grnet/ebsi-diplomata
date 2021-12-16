import os
from driver import WalletShell
from app import WalletApp
from conf import STORAGE, DBNAME, TMPDIR

if __name__ == '__main__':
    app = WalletApp.create({
        'db': os.path.join(STORAGE, DBNAME),
        'tmp': TMPDIR
    })
    WalletShell(app).run()

