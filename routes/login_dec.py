from functools import wraps
from flask import abort, session, request


from Database.Twitch.twitch_user import TwitchUser
from config.config import admin_users


def check_admin():
    if 'me' not in session:
        abort(401)

    me = session['me']
    if me['display_name'] not in admin_users:
        abort(401)
def requires_admin_user():
    def requires_admin_user_helper(f):
        @wraps(f)
        def check_session(*args, **kws):
            if 'me' not in session:
                abort(401)

            me: TwitchUser = session['me']
            if me.display_name not in admin_users:
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

            elif 'twitch_resp' not in session:
                abort(401)

            return f(*args, **kws)

        return check_session

    return requires_logged_in_helper
