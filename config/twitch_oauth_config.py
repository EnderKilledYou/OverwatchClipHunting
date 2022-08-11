from config.config import consumer_key, consumer_secret
from flask_oauthlib.client import OAuth, OAuthRemoteApp

oauth = OAuth()

twitch_oauth: OAuthRemoteApp = oauth.remote_app('twitch',
                                base_url='https://id.twitch.tv/oauth2/',
                                request_token_url=None,
                                access_token_method='POST',
                                access_token_url='https://id.twitch.tv/oauth2/token',
                                authorize_url='https://id.twitch.tv/oauth2/authorize',
                                consumer_key=consumer_key,
                                consumer_secret=consumer_secret,
                                request_token_params={'scope': ["user_read",'clips:edit','channel:read:editors']}
                                )
