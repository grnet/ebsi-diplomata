import sys
from app import WalletApp
from driver import WalletShell

if __name__ == '__main__':
    try:
        app = WalletApp.create()
    except RuntimeError as err:
        sys.stdout.write('%s\n' % err)
        sys.exit(1)
    WalletShell(app).run()
