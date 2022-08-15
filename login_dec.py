from functools import wraps
from flask import abort, session, request

import config.config
from bots.bot_user import get_user_by_token
from Database.Twitch.twitch_user import TwitchUser


def requires_admin_user():


    def requires_admin_user_helper(f):
        @wraps(f)
        def check_session(*args, **kws):
            if 'me' not in session:
                abort(401)

            me: TwitchUser = session['me']
            if me.display_name not in config.config.admin_user:
                abort(401)
            return f(*args, **kws)

        return check_session

    return requires_admin_user_helper


def requires_bot_user(f):
    @wraps(f)
    def check_session(*args, **kws):
        if 'api_key' not in request.args:
            abort(401)

        user_token = request.args['api_key']
        user = get_user_by_token(user_token)
        if not user:
            abort(401)
        session['bot'] = user

        return f(*args, **kws)


def requires_logged_in():
    def requires_logged_in_helper(f, token_allowed=False):
        @wraps(f)
        def check_session(*args, **kws):
            """Decorator for defining a new Sharp function.

            Args:
                route (optional): Expose this function at a specific API route, ignores the
                    prefix supplied in the `Sharp(prefix="/api")` constructor.
            """
            current_ip = request.remote_addr
            if 'ip' in session and session['ip'] != current_ip:
                abort(401)
            if token_allowed:
                check_api_user(current_ip)
            elif 'twitch_resp' not in session:
                abort(401)

            return f(*args, **kws)

        return check_session

    return requires_logged_in_helper


def check_api_user(current_ip):
    if 'api_user' in session:
        if get_user_by_token(session['api_user'].token):
            return
        session.pop('api_user', None)

    if 'api_key' in request.args:
        user = get_user_by_token(request.args['api_key'])
        if user:
            session['api_user'] = user
            session['ip'] = current_ip
            return

    abort(401)
