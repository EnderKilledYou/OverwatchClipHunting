import os

consumer_key = "rawxqek55j2qtx6uh02rn0l8exru69"
consumer_secret = "3l5q0vrewa3c8wed2g7ytxa5x20e09"
access_token = 'j5dsm2ieknyv34rddy5uln3a1lxxn7'
refresh_token = 'eyu6aat8gmjdublpqumpr7whi2ytx0v9ff769or70apag78l4m'
flask_secret_key = 'woooolooooloo!wooooloooo'
admin_users = ['bestboyfriend4']
roles = {'bestboyfriend4': [
    'admin'
]}

if "TESSERACT_DATA_FAST" not in os.environ:
    raise RuntimeError("Need tessy data (env: TESSERACT_DATA_FAST)")
tess_fast_dir = os.environ["TESSERACT_DATA_FAST"]
if not tess_fast_dir.endswith(os.sep):
    tess_fast_dir = tess_fast_dir + os.sep

sample_frame_rate = os.cpu_count() * 2
if "SAMPLE_FRAME_RATE" in os.environ:
    sample_frame_rate = int(os.environ["SAMPLE_FRAME_RATE"])


def get_user_roles(user):
    if user in roles:
        return roles[user]
    return []
