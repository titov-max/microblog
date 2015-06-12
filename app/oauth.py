from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
import json


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        print "*" * 10
        print dir(oauth_session)
        print "*" * 10
        print "*" * 10
        print oauth_session.get('me')
        print "*" * 10
        me = oauth_session.get('me').json()
        print "*" * 10
        print me
        print "*" * 10
        return (
            'facebook$' + me['id'],
            me.get('first_name') + ' ' + me.get('last_name'),  # Facebook does not provide
                                            # username, so the email's user
                                            # is used instead
            me.get('email')
        )

class VkSignIn(OAuthSignIn):
    def __init__(self):
        super(VkSignIn, self).__init__('vk')
        self.service = OAuth2Service(
            name='vk',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://oauth.vk.com/authorize',
            access_token_url='https://oauth.vk.com/access_token',
            base_url='https://oauth.vk.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None

        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'redirect_uri': self.get_callback_url(),
                  'grant_type': 'authorization_code'},
            decoder=json.loads
        )
        me = oauth_session.access_token_response.json()
        return (
            'vk$' + str(me.get('user_id')),
            me.get('email').split('@')[0],
            me.get('email')
        )

"""class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            base_url='https://accounts.google.com'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='https://www.googleapis.com/auth/gmail.readonly',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None

        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'redirect_uri': self.get_callback_url(),
                  'grant_type': 'authorization_code'}
        )
        credentials = oauth_session.get('credentials').json()
        return (
            'google$' + credentials.get('user_id'),
            credentials.get('email').split('@')[0],
            credentials.get('email')
        )"""