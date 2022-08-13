import os.path
from os.path import abspath

from flask import Flask, redirect, render_template

from config.config import flask_secret_key


def config_app() -> Flask:
    appx = Flask('ocr', static_url_path='',
                 static_folder='templates',
                 template_folder='templates')
    appx.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitch.sqlite3'
    appx.config['SECRET_KEY'] = flask_secret_key

    return appx


def register_blueprints(app: Flask):
    from twitch.twitch import twitch as twitch_blueprint
    from routes.monitor import monitor as monitor_blueprint
    app.register_blueprint(twitch_blueprint)
    app.register_blueprint(monitor_blueprint)
    from config.db_config import init_db
    init_db()


app = config_app()

register_blueprints(app)

_s = abspath("front_end/src/api/")
if not os.path.exists(_s):
    os.makedirs(_s)

from sharp_api import get_sharp
@app.route('/sharp')
def print_api():

    output_js_filename = f'{_s}/api.js'
    get_sharp().generate(output_js_filename)
    return ""

@app.route('/')
def index():

   return render_template('index.html')
