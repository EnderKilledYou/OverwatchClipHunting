
from sqlalchemy_serializer import SerializerMixin
from twitchAPI import Twitch, AuthScope

from Database.Twitch.dict_to_class import Dict2Class
from Database.encrypted_database_fields import EncryptedFields
from OrmHelpers.BasicWithId import BasicWithId
from config.config import consumer_key, consumer_secret
from config.db_config import db


class TwitchResponse(db.Model, SerializerMixin, EncryptedFields):
    """
        Holds the response from twitch in the data base
    """
    serialize_rules = ()
    serialize_only = ('id', 'twitch_user_id', 'access_token', 'expires_in', 'refresh_token', 'token_type')
    id = db.Column(db.Integer, primary_key=True)
    twitch_user_id = db.Column(db.String(90))
    access_token = db.Column(db.String(900))
    expires_in = db.Column(db.Integer)
    refresh_token = db.Column(db.String(900))
    token_type = db.Column(db.String(900))





    def update_from(self, resp) -> None:
        self.access_token = self.encrypt(resp['access_token'])
        self.expires_in = resp['expires_in']
        self.refresh_token = self.encrypt(resp['refresh_token'])
        self.token_type = resp['token_type']

    
    def get_token(self):
        return self.decrypt(self.access_token)
    
    def get_refreshtoken(self):
        return self.decrypt(self.refresh_token)


twitch_response_helper = BasicWithId(TwitchResponse)



def get_response_by_twitch_id(twitch_user_id) -> TwitchResponse:
    with db.session.begin():
        user = TwitchResponse.query.filter_by(twitch_user_id=twitch_user_id).first()
        if user is None:
            return None
    return Dict2Class(user.to_dict())


def get_twitch_api_from_db(twitch_response: TwitchResponse) -> Twitch:
    twitch_api = Twitch(app_id=consumer_key, app_secret=consumer_secret)
    twitch_api.auto_refresh_auth = True
    twitch_api.set_user_authentication(twitch_response.access_token, [AuthScope.CLIPS_EDIT],
                                       twitch_response.refresh_token,
                                       validate=False)
    twitch_api.refresh_used_token()
    return twitch_api
