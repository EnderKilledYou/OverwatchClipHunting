import os
from flask import Flask, jsonify
from oauthlib.common import generate_token
from sharp import Sharp, naming


def config_app() -> Flask:
    appx = Flask('ocr', static_url_path='',
                 static_folder='static',
                 template_folder='templates')

    appx.config['SECRET_KEY'] = generate_token()

    return appx


app: Flask = config_app()
api_generator = Sharp(app, prefix="/api", naming=naming.file_based)




def register_blueprints(app: Flask):
    from config.db_config import init_db
    from routes.twitch import twitch as twitch_blueprint
    from routes.monitor import monitor as monitor_blueprint
    from routes.users import users as user_blueprint
    from routes.clips.clips import clips as clips_blueprint
    from routes.clips import search_twitch_clips, add_clip, add_clip_scan, all_clips, clips_search, delete_clips, \
        get_clip_scan_jobs, get_game_ids, list_twitch_clips, store_clip, tags_job
    from routes.video import video as video_blueprint
    from routes.streamer import streamer as streamer_blueprint

    from routes.zombie import zombie_route as zombie_callback_blueprint
    app.register_blueprint(user_blueprint)
    app.register_blueprint(zombie_callback_blueprint)
    app.register_blueprint(clips_blueprint)
    app.register_blueprint(streamer_blueprint)
    app.register_blueprint(twitch_blueprint)
    app.register_blueprint(monitor_blueprint)
    app.register_blueprint(video_blueprint)
    init_db()


app.url_map.strict_slashes = False
register_blueprints(app)


@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "healthy"})


@app.errorhandler(404)
def not_found(e):
    if os.path.exists('./static/index.html'):
        return app.send_static_file("index.html")
    else:
        return "The app didn't install error"


if __name__ == '__main__':
    app.run(threaded=True)

import start_up_flask
