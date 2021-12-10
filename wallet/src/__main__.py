import os
from driver import WalletShell
from app import App
from conf import STORAGE, DBNAME

if __name__ == '__main__':
    app = App.create({
        'db': os.path.join(STORAGE, DBNAME)
    })
    WalletShell(app).run()

