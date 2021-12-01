import subprocess
from urllib.parse import urljoin
import requests

def run_cmd(args):
    rslt = subprocess.run(args, stdout=subprocess.PIPE)
    resp = rslt.stdout.decode('utf-8').rstrip('\n')
    code = rslt.returncode
    return (resp, code)


class HttpClient(object):

    def __init__(self, remote):
        self.remote = remote

    @staticmethod
    def _create_url(address, endpoint):
        return urljoin(address, endpoint.strip('/'))

    def _do_request(self, method, url, **kw):
        return getattr(requests, method)(url, **kw)

    def get(self, endpoint):
        url = self._create_url(self.remote, endpoint)
        return self._do_request('get', url)

    def post(self, endpoint, payload):
        url = self._create_url(self.remote, endpoint)
        return self._do_request('post', url, json=payload)

