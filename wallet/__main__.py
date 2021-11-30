import cmd, sys
import requests
import json
import os
import subprocess

def run_cmd(args):
    result = subprocess.run(args, stdout=subprocess.PIPE)
    resp = result.stdout.decode('utf-8').rstrip('\n')
    code = result.returncode
    return (resp, code)

def get_did(nr=None, no_ebsi_prefix=False):
    args = ['get-did',]
    if nr:
        args += ['--nr', str(nr)]
    resp, code = run_cmd(args)
    if no_ebsi_prefix:
        resp = resp.lstrip(EBSI_PREFIX)
    return (resp, code)

def load_did():
    resp, code = get_did()
    STORAGE = os.getenv('STORAGE')  # TODO
    if code == 0:
        _path = os.path.join(STORAGE, 'did', '1', 'repr.json')
        with open(_path, 'r') as f:
            out = json.load(f)
    else:
        out = {'error': resp}
    return out

class WalletShell(cmd.Cmd):
    intro = " * Type help or ? to list commands.\n"
    prompt = "(wallet) > "

    def preloop(self):
        print('\nStarted wallet session\n')

    def postloop(self):
        print('\nClosed wallet session\n')

    def do_info(self, line):
        """Show wallet info"""
        # TODO
        did = load_did()
        print(json.dumps(did, indent=2))

    def do_issue(self, line):
        """Request credentials issuance"""
        resp, code = get_did()
        # TODO
        if code != 0:
            print('ERROR: ', resp)
            return
        did = resp
        resp = requests.post('http://localhost:7000/api/vc', json={
            'did': did,
        })
        # TODO: Store credentials
        print(json.dumps(resp.json(), indent=2))

    def do_EOF(self, line):
        """Equivalent to exit."""
        return True

    def do_exit(self, line):
        """Close current wallet session."""
        return self.do_EOF(line)


if __name__ == '__main__':
    WalletShell().cmdloop()
