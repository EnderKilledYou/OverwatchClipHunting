import os

consumer_key = "rawxqek55j2qtx6uh02rn0l8exru69"
consumer_secret = "3l5q0vrewa3c8wed2g7ytxa5x20e09"
access_token = 'j5dsm2ieknyv34rddy5uln3a1lxxn7'
refresh_token = 'eyu6aat8gmjdublpqumpr7whi2ytx0v9ff769or70apag78l4m'
flask_secret_key = 'woooolooooloo!wooooloooo'
admin_user = ['bestboyfriend4']
if "TESSERACT_DATA_FAST" not in os.environ:
    raise RuntimeError("Need tessy data")
tess_fast_dir = os.environ["TESSERACT_DATA_FAST"]

sample_frame_rate = 8
if "SAMPLE_FRAME_RATE" in os.environ:
    sample_frame_rate = int(os.environ["SAMPLE_FRAME_RATE"])
