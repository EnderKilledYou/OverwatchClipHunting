from flask import Flask

from config.config import flask_secret_key



def config_app() -> Flask:
    appx = Flask('ocr')
    appx.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitch.sqlite3'
    appx.config['SECRET_KEY'] = flask_secret_key

    return appx


def register_blueprints(app: Flask):
    from twitch.twitch import twitch as twitch_blueprint
    app.register_blueprint(twitch_blueprint)
    from config.db_config import db
    db.create_all()

app = config_app()

register_blueprints(app)


