import os
import threading
import requests


def send_to_zombie_server(path, data):
    r = requests.post(f'{os.environ["zombie"]}{path}', json=data)
    print(f"Status Code: {r.status_code}, Response: {r.json()}")


def report_zombie_tag(tag, clip):
    if not is_zombie_mode():
        return
    threading.Thread(target=send_to_zombie_server, args=['/zombie_tag', {
        'clip': clip.to_dict(),
        'tag': tag.to_dict()
    }])
    pass


def ask_zombie_master(tag, clip):
    if not is_zombie_mode():
        return
    r = requests.get(f'{os.environ["zombie"]}/zombie_work')
    print(f"Status Code: {r.status_code}, Response: {r.json()}")


def acquire_zombie(streamer):
    r = requests.post(f'{os.environ["zombie"]}/zombie_acquire', json={
        'zombie_streamer': streamer
    })
    print(f"Status Code: {r.status_code}, Response: {r.json()}")


def report_zombie_clip(tag, clip):
    if not is_zombie_mode():
        return
    report_zombie_tag(tag, clip)


def is_zombie_mode():
    return "zombie" in os.environ


def clip_tag(twitch_video_id: str, tag):
    pass
