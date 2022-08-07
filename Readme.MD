# Clip Hunter
## Download specific events from streams. 


**First, install** 

`pip install -r Requirements.txt`



## Edit configs

change config/config_example.p to config/config.py

```python
#config/config.py

consumer_key = "" # From Twitch
consumer_secret = "" # F rom Twitch
broadcasters = ['a','b','c'] 
access_token = '' # From Flask
refresh_token = '' # From Flask
flask_secret_key = '' # Type random shit here
max_frames_to_scan_per_second = 16 # more for more acc (16 is REALLY good almost too good) less for more speed. 4 is min.
make_clips = False  # Set to false for just watch mode, won't talk to twitch api or bug you about it
min_healing_duration = 99  # set stupid high to ignore, or like 4-9 to catch good clips
min_elims = 99 # set stupid high to ignore, or like 2 to catch good clips
min_blocking_duration = 99 # set stupid high to ignore, or like 4-9 to catch good clips
min_defense_duration = 99 # set stupid high to ignore, or like 4-9 to catch good clips
min_assist_duration = 99 # set stupid high to ignore, or like 4-9 to catch good clips
wait_for_mode=True # set this to false to only check at run if they are live. Set to True to wait for them to go live. 
```

## Create a twitch app

[Create A Twitch App](https://dev.twitch.tv/console/apps/create)


Get your consumer_key (client id) and consumer_secret (client secr
et) from there

![img_twitch_config.png](image_twitch_config.png)
Set your call back url to http://localhost:5000/oauth

## Run the flask server to get your python credentials

`python.exe -m flask run`

Go to # [http://localhost:5000/login ](http://localhost:5000/oauth)
(note sometimes it'll say your url doesn't match. just type http://localhost:5000/login in a new window to fix. Always works after)
Login.

Get the access_token and refresh_token.

![image_flask.png](image_flask.png)


**Now you're ready to clip hunt!**


You can just start the beasty by running `python monitor_streamer.py`



You can just start the beasty and overwrite the config's broadcaster by running `python monitor_streamer.py someone`

## Customization

Check out [overwatch_events.py](overwatch_events.py) to customize events

## Add Other games

Implement a [ScreenRegion](Ocr/screen_region.py) like  [OverwatchActionScreenRegion](Ocr/overwatch_action_screen_region.py)

and a [ScreenReader](Ocr/screen_reader.py) like  [OverewatchScreenReader](Ocr/overwatch_screen_reader.py)

and a [FrameTester](Ocr/frame_tester.py)  

another example of [ScreenRegion](Ocr/screen_region.py) is [OverwatchActionScreenRegion](Ocr/overwatch_searching_for_game_screen_region.py)

Screen regions are the part of the iamge you want to look at.

Screen readers act on them



## Cli

While it's running, type `quit` to shut down gracefully