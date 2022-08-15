from os.path import abspath

from flask import Flask, render_template

from config.config import flask_secret_key


def config_app() -> Flask:
    appx = Flask('ocr', static_url_path='',
                 static_folder='templates',
                 template_folder='templates')
    appx.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitch.sqlite3'
    appx.config['SECRET_KEY'] = flask_secret_key

    return appx


def register_blueprints(app: Flask):
    from routes.twitch import twitch as twitch_blueprint
    from routes.monitor import monitor as monitor_blueprint
    from routes.clips import clips as clips_blueprint
    from routes.video import video as video_blueprint
    from routes.streamer import streamer as streamer_blueprint
    app.register_blueprint(clips_blueprint)
    app.register_blueprint(streamer_blueprint)
    app.register_blueprint(twitch_blueprint)
    app.register_blueprint(monitor_blueprint)
    app.register_blueprint(video_blueprint)
    from config.db_config import init_db
    init_db()


app = config_app()

register_blueprints(app)



@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(threaded=True)
