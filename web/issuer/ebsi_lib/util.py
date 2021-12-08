import subprocess

def run_cmd(args):
    result = subprocess.run(args, stdout=subprocess.PIPE)
    resp = result.stdout.decode('utf-8').rstrip('\n')
    code = result.returncode
    return (resp, code)
