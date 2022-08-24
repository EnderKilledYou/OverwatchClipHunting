from app import app


from Database.MissingRecordError import MissingRecordError
from Database.Twitch.twitch_clip_tag import TwitchClipTag
from config.db_config import db



def update_tag_and_bag_filename(id: int, filename_str) -> TwitchClipTag:
    with db.session.begin():
        item: TwitchClipTag = TwitchClipTag.query.filter_by(id=id).first()
        if not item:
            raise MissingRecordError("can't update a t and b that doesn't exist")

        item.file_name = filename_str
        item.has_file = filename_str is not None

    db.session.flush()
    return item
