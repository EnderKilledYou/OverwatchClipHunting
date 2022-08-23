from flask import Blueprint

clips = Blueprint('clips', __name__)
from app import api_generator
sharp = api_generator

from . import *

