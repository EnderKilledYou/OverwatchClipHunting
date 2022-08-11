from flask import Flask

from config.config import flask_secret_key


def config_app() -> Flask:
    appx = Flask('ocr', static_url_path='',
                 static_folder='templates',
                 template_folder='web_templates')
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


