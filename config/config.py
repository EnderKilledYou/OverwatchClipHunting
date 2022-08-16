import os

from config.streamer_configs import streamer_configs

consumer_key = "rawxqek55j2qtx6uh02rn0l8exru69"
consumer_secret = "3l5q0vrewa3c8wed2g7ytxa5x20e09"
access_token = 'j5dsm2ieknyv34rddy5uln3a1lxxn7'
refresh_token = 'eyu6aat8gmjdublpqumpr7whi2ytx0v9ff769or70apag78l4m'
flask_secret_key = 'woooolooooloo!wooooloooo'
admin_user = ['bestboyfriend4']
if "TESSERACT_DATA_FAST" in os.environ:
    tess_fast_dir = os.environ["TESSERACT_DATA_FAST"]
else:
    tess_fast_dir = r'C:\tmp\tessdata_fast'
broadcasters = list(streamer_configs.keys())
print(broadcasters)
