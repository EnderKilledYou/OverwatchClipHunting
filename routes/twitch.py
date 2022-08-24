import sys


from flask import session, redirect, request, url_for, jsonify, Blueprint, abort

from Database.Twitch.dict_to_class import Dict2Class
from cloud_logger import cloud_error_logger
from config.config import admin_users
from routes.route_cache import config

twitch = Blueprint('twitch', __name__)

from config.db_config import db
from config.twitch_oauth_config import twitch_oauth
from Database.Twitch.twitch_user import TwitchUser
from Database.Twitch.twitch_response import TwitchResponse
from twitch_helpers.vod import get_current_user


@twitch_oauth.tokengetter
def get_twitch_token(token=None):
    return session.get('twitch_token')


@twitch.route('/login')
def login():
    return twitch_oauth.authorize(callback=url_for('twitch.authorized', _external=True))


@twitch.route('/oauth')
def authorized():
    try:
        resp = twitch_oauth.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error'],
                request.args['error_description']
            )
        me = get_current_user(resp)
        if me["display_name"] not in admin_users:
            abort(401)
        session['twitch_resp'] = resp

        session['me'] = me
        twitch_response = get_twitch_user_by_twitch_display_name(me["display_name"])

        if twitch_response is not None:
            update_from_api(twitch_response.id, resp)
        else:
            twitch_response = create_from_api(resp,me["display_name"])

        return redirect("/")
    except BaseException as e:
        cloud_error_logger(e, file=sys.stderr)
        import traceback
        traceback.print_exc()
        return jsonify({})


def create_from_api(api_resp,twitch_user_id):
    with db.session.begin():
        twitch_response = TwitchResponse()
        twitch_response.update_from(api_resp)
        twitch_response.twitch_user_id = twitch_user_id
        db.session.commit()
        db.session.flush()
        dict_class = Dict2Class(twitch_response.to_dict())
    return dict_class


def update_from_api(id, api_resp):
    with db.session.begin():
        twitch_response = TwitchResponse.query.filter_by(id=id).first()
        twitch_response.update_from(api_resp)

        db.session.commit()
        db.session.flush()
        dict_class = Dict2Class(twitch_response.to_dict())
    return dict_class


def get_twitch_user_by_twitch_display_name(display_name):
    with db.session.begin():
        twitch_response = TwitchResponse.query.filter_by(twitch_user_id=display_name).first()
        if twitch_response is None:
            return None
        dict_class = Dict2Class(twitch_response.to_dict())
    return dict_class


@twitch.route('/logout')
def logout():
    session.pop('twitch_token', None)
    return redirect(url_for('index'))
