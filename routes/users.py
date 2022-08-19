from flask import Blueprint, jsonify, session

from Database.Twitch.twitch_user import TwitchUser
from streamer_config import update_config, get_config_by_id, get_configs, get_configs_name

streamer_config = Blueprint('streamer_config', __name__)
from routes.login_dec import requires_logged_in, requires_admin_user

from app import api_generator
sharp = api_generator


@requires_logged_in()
@sharp.function()
def update(setting_name: str, setting_value: str):
    me: TwitchUser = session['me']
    exists = get_config_by_id(me.id)
    if not exists:
        return jsonify({"success": False, "message": "config doesn't exists"});
    update_config_setting(exists, setting_name, setting_value)
    return jsonify({'token': exists.to_dict()})


@requires_admin_user()
@sharp.function()
def update_admin(user_id: int, setting_name: str, setting_value: str):
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

@requires_logged_in()
@sharp.function()
def get():
    me: TwitchUser = session['me']
    exists = get_config_by_id(me.id)
    if not exists:
        return jsonify({"success": False, "message": "config doesn't exists"});
    return jsonify({'token': exists.to_dict()})

@requires_admin_user()
@sharp.function()
def get_admin(user_id: int):
    me: TwitchUser = session['me']
    exists = get_config_by_id(int(user_id))
    if not exists:
        return jsonify({"success": False, "message": "config doesn't exists"});
    return jsonify({'token': exists.to_dict()})

@requires_admin_user()
@sharp.function()
def list_admin(name: str,page:int,order_by:bool):
    if not name or len(name)< 1:
        return get_configs(int(page),order_by)
    return get_configs_name(name,int(page),order_by)
    exists = get_config_by_id(int(user_id))
    if not exists:
        return jsonify({"success": False, "message": "config doesn't exists"});
    return jsonify({'token': exists.to_dict()})