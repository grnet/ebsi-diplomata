import cmd, sys
import requests
import json

class WalletShell(cmd.Cmd):
    intro = " * Type help or ? to list commands.\n"
    prompt = "(wallet) > "

    def preloop(self):
        print('\nStarted wallet session\n')

    def postloop(self):
        print('\nClosed wallet session\n')

    def do_fetch(self, line):
        resp = requests.get('http://localhost:7000/api/did')
        print(json.dumps(resp.json(), indent=2))

    def do_EOF(self, line):
        """Equivalent to exit."""
        return True

    def do_exit(self, line):
        """Close current wallet session."""
        return self.do_EOF(line)


if __name__ == '__main__':
    WalletShell().cmdloop()
