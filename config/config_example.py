import sys

consumer_key = ""
consumer_secret = ""
broadcaster = ""
access_token=''
refresh_token=''
flask_secret_key = ''
max_frames_to_scan_per_second = 8
make_clips = False  # Set to false for just watch mode


if len(sys.argv) > 1:
    broadcaster = sys.argv[1]