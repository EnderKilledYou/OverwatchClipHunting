import sys

consumer_key = ""
consumer_secret = ""
broadcaster = ""
access_token=''
refresh_token=''
flask_secret_key = ''
max_frames_to_scan_per_second = 16
make_clips = False  # Set to false for just watch mode
min_healing_duration = 99  # set stupid high to ignore
min_elims = 99
min_blocking_duration = 99
min_defense_duration = 99
min_assist_duration = 99

if len(sys.argv) > 1:
    broadcaster = sys.argv[1]