from driver import WalletShell
from app import App

if __name__ == '__main__':
    app = App.create()
    WalletShell(app).run()

