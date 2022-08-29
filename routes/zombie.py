from flask import Blueprint, request
from Database.api_user import add_zombie, get_zombies
from twitch_helpers.twitch_helpers import get_twitch_api

zombie_route = Blueprint('zombie', __name__)
from time import sleep
from Database.Twitch.twitch_clip_instance import get_twitch_clip_instance_by_video_id, add_twitch_clip_instance_from_api
from Database.Twitch.twitch_clip_tag import add_twitch_clip_tag_request

from generic_helpers.something_manager import ThreadedManager
from app import api_generator
sharp = api_generator

