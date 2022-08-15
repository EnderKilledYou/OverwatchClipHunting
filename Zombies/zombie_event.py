import os
import threading
import requests

def send_to_zombie_server(path, data):
    r = requests.post(f'{os.environ}{path}', json=data)
    print(f"Status Code: {r.status_code}, Response: {r.json()}")


def report_zombie_tag(tag, clip):
    if not is_zombie_mode():
        return
    threading.Thread(target=send_to_zombie_server, args=['/zombie_tag', {
        'clip': clip.to_dict(),
        'tag': tag.to_dict()
    }])
    pass


def report_zombie_clip(tag, clip):
    if not is_zombie_mode():
        return
    report_zombie_tag(tag, clip)



def is_zombie_mode():
    return "zombie" in os.environ





def clip_tag(twitch_video_id: str, tag):
    pass
