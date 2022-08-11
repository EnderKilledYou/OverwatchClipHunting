from flask import Blueprint, jsonify, session

bot_users = Blueprint('bot_users', __name__)

from bots.bot_user import BotUser
from flask_events import flask_event
from sharp_api import get_sharp
from twitch.twitch_response import get_response_by_twitch_id, get_twitch_api_from_db
from login_dec import requires_bot_user, requires_admin_user

sharp_api = get_sharp()


@requires_bot_user()
@sharp_api.function()
def request_clip(broadcaster_id: str, clip_type: str):
    bot: BotUser = session['bot']
    twitch_response = get_response_by_twitch_id(bot.twitch_user_id)
    twitch_api = get_twitch_api_from_db(twitch_response)

    created = twitch_api.create_clip(broadcaster_id, True)
    flask_event.emit('clip', created['data'], clip_type)
    return jsonify({'success': True})


@requires_bot_user()
@sharp_api.function()
def request_marker(broadcaster_id: str, description: str):
    bot: BotUser = session['bot']
    twitch_response = get_response_by_twitch_id(bot.twitch_user_id)
    twitch_api = get_twitch_api_from_db(twitch_response)
    twitch_api.create_stream_marker(broadcaster_id, description)
    return jsonify({'success': True})


@requires_admin_user()
@sharp_api.function()
def assign_bot(broadcaster_id: str, description: str):
    bot: BotUser = session['bot']
    twitch_response = get_response_by_twitch_id(bot.twitch_user_id)
    twitch_api = get_twitch_api_from_db(twitch_response)
    twitch_api.create_stream_marker(broadcaster_id, description)
    return jsonify({'success': True})
