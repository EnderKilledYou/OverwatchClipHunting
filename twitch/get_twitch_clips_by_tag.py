from Database.Twitch.twitch_clip_tag import TwitchClipTag


def get_twitch_clips_by_tag(tag: str, page: int = 1):
    try:
        TwitchClipTag.query.filter_by(tag=tag).paginate(page=page, per_page=50).items
    except:
        return []
