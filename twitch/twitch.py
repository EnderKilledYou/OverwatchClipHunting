import routes.streamer
from app import app
from flask import session, redirect, request, url_for, jsonify, Blueprint

twitch = Blueprint('twitch', __name__)


from config.db_config import db
from config.twitch_oauth_config import twitch_oauth
from .twitch_user import TwitchUser
from twitch.twitch_response import TwitchResponse
from .vod import get_current_user


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
        session['twitch_resp'] = resp

        print(resp)
        me: TwitchUser = get_current_user(TwitchResponse(resp))
        session['me'] = me
        twitch_response = get_twitch_user_by_twitch_id(me)

        if twitch_response is None:
            twitch_response = TwitchResponse(resp)


            db.session.commit()
            db.session.flush()
            pass
        else:
            twitch_response.update_from(resp)
            db.session.commit()
            db.session.flush()
        return 'Access Granted (you can paste these into config.py in config): <br />access_token=\'%s\' <br /> refresh_token=\'%s\'' % (
            resp['access_token'],
            resp['refresh_token']
        )
        return jsonify(resp)
    except BaseException as e:
        print(e)
        import traceback
        traceback.print_exc()
        return jsonify({})


def get_twitch_user_by_twitch_id(me):
    twitch_response = TwitchResponse.query.filter_by(twitch_user_id=me.twitch_user_id).first()
    return twitch_response


@twitch.route('/logout')
def logout():
    session.pop('twitch_token', None)
    return redirect(url_for('index'))
