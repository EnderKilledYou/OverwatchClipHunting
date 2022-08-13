from flask import Blueprint, jsonify, session

sub_users = Blueprint('sub_users', __name__)

from sharp_api import get_sharp
from users.allowed_users import get_user_by_name, delete_user, add_user, get_user_by_id, disable_user, update_user

sharp = get_sharp()



@sharp.function()
def add(name: str, description: str, twitch_user_id: str):
    exists = get_user_by_name(name)
    if exists:
        return jsonify({"success": False, "message": "user exists"});

    user = add_user(name=name, twitch_user_id=twitch_user_id, description=description, disabled=False)
    return jsonify({'token': user.to_dict()})



@sharp.function()
def update(id: str, description: str):
    exists = get_user_by_id(id)
    if not exists:
        return jsonify({"success": False, "message": "user doesn't exists"});

    update_user(exists, description)
    return jsonify({'token': exists.to_dict()})



@sharp.function()
def delete(name: str):
    exists = get_user_by_name(name)
    if not exists:
        return jsonify({"success": False, "message": "user doesn't exist"});
    delete_user(exists)



@sharp.function()
def disable(id: int):
    exists = get_user_by_id(id)
    if not exists:
        return jsonify({"success": False, "message": "user doesn't exist"});
    disable_user(id)
