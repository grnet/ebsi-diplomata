from oauth.login.base import OAuthLoginHandler
from oauth.clients.google import GoogleOAuthClient
from ssi.models import User, Alumnus


class GoogleLoginHandler(OAuthLoginHandler):

    def __init__(self, oauth):
        super().__init__(oauth, GoogleOAuthClient)

    def _extract_user_info(self, profile):
        sub = profile['sub']
        name, last_name = profile['name'].split(' ')  # Google peculiarity
        assert profile['family_name'] == last_name
        info = {}
        info['sub'] = sub
        info['first_name'] = name
        info['last_name'] = profile["family_name"]
        info['father_name'] = profile.get('father_name', None)
        info['mother_name'] = profile.get('mother_name', None)
        info['birthyear'] = profile.get('birthyear', 1990)
        info['birthdate'] = profile.get('birthdate', None)
        info['email'] = profile.get('email', None)
        info['phone'] = profile.get('phone_number', None)
        info['vatin'] = sub
        return info

    def _extract_user_data(self, info):
        data = {}
        data['extern_id'] = info['sub']
        data['first_name'] = info['first_name']
        data['last_name'] = info['last_name']
        data['father_name'] = info['father_name']
        data['mother_name'] = info['mother_name']
        data['birthyear'] = info['birthyear']
        data['afm'] = info['sub']
        return data

    def _get_or_create_user(self, data):
        try:
            alumnus = Alumnus.objects.get(extern_id=data['extern_id'])
        except Alumnus.DoesNotExist:
            user = User.objects.create(
                auth_provider=self.name,
                role=User.ALUMNUS
            )
            alumnus = Alumnus.objects.create(user=user, **data)
        else:
            user = alumnus.user
        return user

