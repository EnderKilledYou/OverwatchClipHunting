import cryptocode

from sqlalchemy_serializer import SerializerMixin

from config.db_config import db


class EncryptedFields:
    def decrypt(self, text):
        return text
        return cryptocode.decrypt(text, "wow")

    def encrypt(self, text):
        return text
        return cryptocode.encrypt(text, "wow")



class TwitchResponse(db.Model, SerializerMixin, EncryptedFields):
    serialize_rules = ()
    serialize_only = ('id', 'twitch_user_id', 'access_token', 'expires_in', 'refresh_token', 'token_type')
    id = db.Column(db.Integer, primary_key=True)
    twitch_user_id = db.Column(db.String)
    access_token = db.Column(db.String)
    expires_in = db.Column(db.Integer)
    refresh_token = db.Column(db.String)
    token_type = db.Column(db.String)

    def __init__(self, resp) -> None:
        self.update_from(resp)

    def update_from(self, resp) -> None:
        self.access_token = self.encrypt(resp['access_token'])
        self.expires_in = resp['expires_in']
        self.refresh_token = self.encrypt(resp['refresh_token'])
        self.token_type = resp['token_type']

    def get_token(self):
        return self.decrypt(self.access_token)

    def get_refreshtoken(self):
        return self.decrypt(self.refresh_token)
