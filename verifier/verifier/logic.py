from django.conf import settings


class Verifier(object):

    @classmethod
    def init_from_app(cls, settings):
        return cls()    # TODO
