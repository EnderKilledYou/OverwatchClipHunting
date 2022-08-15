from flask import Blueprint, jsonify, session

sub_users = Blueprint('sub_users', __name__)
from login_dec import requires_logged_in
from sharp_api import get_sharp
from Database.api_user import get_user_by_name, add_user_with_token, get_subuser_count, delete_user, reset_token

sharp = get_sharp()


@requires_logged_in()
@sharp.function()
def list():
    pass


@requires_logged_in()
@sharp.function()
def add(name: str, description: str):
    me = session['me']
    exists = get_user_by_name(name, me.twitch_user_id)
    if exists:
        return jsonify({"success": False, "message": "user exists"});
    count = get_subuser_count()
    if count > 3:
        return jsonify({"success": False, "message": "Too many users, delete one"});

    user = add_user_with_token(name=name, twitch_user_id=me.twitch_user_id, description=description)
    return jsonify({'user': user, 'token': user.token})


@requires_logged_in()
@sharp.function()
def delete(name: str):
    me = session['me']
    exists = get_user_by_name(name, me.twitch_user_id)
    if not exists:
        return jsonify({"success": False, "message": "user doesn't exist"});
    delete_user(exists)


@requires_logged_in()
@sharp.function()
def reset(name: str):
    me = session['me']
    exists = get_user_by_name(name, me.twitch_user_id)
    if not exists:
        return jsonify({"success": False, "message": "user doesn't exist"});
    reset_token(exists)
