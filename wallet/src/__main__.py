import os
import sys
import sqlite3
from driver import WalletShell
from app import WalletApp
from conf import STORAGE, DBNAME, TMPDIR

class WalletDbError(BaseException):
    pass

def init_wallet_db():
    from os.path import dirname
    import sqlite3
    from conf import SQL_DBNAME as db
    rootdir = dirname(dirname(os.path.abspath(__file__)))
    try:
        con = sqlite3.connect(db)
        with open(os.path.join(rootdir, 'init-db.sql'), 'r') as f:
            script = f.read()
        cur = con.cursor()
        cur.executescript(script)
    except sqlite3.DatabaseError as err:
        raise WalletDbError(err)
    finally:
        if con:
            con.close()

if __name__ == '__main__':
    init_wallet_db()            # TODO: Integrate this with db connector
    app = WalletApp.create({
        'db': os.path.join(STORAGE, DBNAME),
        'tmp': TMPDIR
    })
    WalletShell(app).run()

