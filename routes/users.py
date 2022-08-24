from flask import Blueprint, jsonify, session, abort

from Database.Twitch.twitch_user import TwitchUser
from config.config import get_user_roles
from streamer_config import update_config, get_config_by_id, get_configs, get_configs_name

users = Blueprint('users', __name__)
from routes.login_dec import check_admin

from app import api_generator

sharp = api_generator


@sharp.function()
def update(setting_name: str, setting_value: str):
    check_admin()
    me: TwitchUser = session['me']
    exists = get_config_by_id(me.id)
    if not exists:
        return jsonify({"success": False, "message": "config doesn't exists"});
    update_config_setting(exists, setting_name, setting_value)
    return jsonify({'token': exists.to_dict()})


@sharp.function()
def update_admin(user_id: int, setting_name: str, setting_value: str):
    check_admin()
    me: TwitchUser = session['me']
    exists = get_config_by_id(int(user_id))
    if not exists:
        return jsonify({"success": False, "message": "config doesn't exists"});
    update_config_setting(exists, setting_name, setting_value)
    return jsonify({'token': exists.to_dict()})


def update_config_setting(exists, setting_name, setting_value):
    config_date = {}
    config_date[setting_name] = setting_value
    update_config(exists, config_date)


@sharp.function()
def get():
    check_admin()
    me: TwitchUser = session['me']
    exists = get_config_by_id(me.id)
    if not exists:
        return jsonify({"success": False, "message": "config doesn't exists"});
    return jsonify({'token': exists.to_dict()})


@sharp.function()
def get_admin(user_id: int):
    check_admin()
    me: TwitchUser = session['me']
    exists = get_config_by_id(int(user_id))
    if not exists:
        return jsonify({"success": False, "message": "config doesn't exists"});
    return jsonify({'token': exists.to_dict()})


@sharp.function()
def list_admin(name: str, page: int, order_by: bool):
    check_admin()
    if not name or len(name) < 1:
        return get_configs(int(page), order_by)
    return get_configs_name(name, int(page), order_by)


@sharp.function()
def get_me():
    if "me" in session:
        roles = get_user_roles(session["me"]["display_name"])
        return {"me": session['me'], 'roles': roles}
    abort(401)
