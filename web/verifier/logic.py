from django.conf import settings


class Verifier(object):

    @classmethod
    def init_from_app(cls, settings):
        return cls()    # TODO

    def get_info(self):
        return {'TODO': 'Include here verifier info'}

    def verify_credentials(self, payload):
        # TODO: Implement
        tmpfile = os.path.join(settings.TMPDIR, 'vc.json')
        with open(tmpfile, 'w+') as f:
            json.dump(payload, f, indent=4)
        return out
