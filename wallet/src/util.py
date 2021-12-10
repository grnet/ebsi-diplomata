from urllib.parse import urljoin
import requests


class HttpClient(object):

    def __init__(self, remote):
        self.remote = remote

    @staticmethod
    def _create_url(address, endpoint):
        return urljoin(address, endpoint.lstrip('/'))

    def _do_request(self, method, url, **kw):
        return getattr(requests, method)(url, **kw)

    def get(self, endpoint):
        url = self._create_url(self.remote, endpoint)
        return self._do_request('get', url)

    def post(self, endpoint, payload):
        url = self._create_url(self.remote, endpoint)
        return self._do_request('post', url, json=payload)

