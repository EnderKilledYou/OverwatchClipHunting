#licence

You may not use this in any student project or commercially with out my permission. You may not use this to create clips of your stream or anyone elses.

It is for educational purposes only. You may contact me for a commercial licence. 

# Clip Hunter
## Download specific events from streams. 


**First, install** 

`pip install -r Requirements.txt`




### Change config/config_example.py to config/config.py


 
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

### Change config/streamer_configs_example.py to config/streamer_configs.py
```python
# add a default config for quick adding streamers
watch_cli_config = {  # used with added with watch and no config
    'make_clips': True,  # Set to false for just watch mode
    'min_healing_duration': 3,  # set stupid high to ignore
    'min_elims': 2,
    'min_blocking_duration': 2,
    'max_frames_to_scan_per_second': 8,
    # some people need 8, some need 4, some need 16 depending on how jank their stream is
    'min_defense_duration': 99,
    'min_assist_duration': 99,
    'stream_prefers_quality': '720p60',
    'buffer_prefers_quality': 'best',
    'wait_for_mode': False
}
# dedicated configs
streamer_configs = {
    "sapphyrelive": {
        'make_clips': True,  # Set to false for just watch mode
        'min_healing_duration': 3,  # set stupid high to ignore
        'min_elims': 2,
        'min_blocking_duration': 3,
        'min_defense_duration': 3,
        'min_assist_duration': 3,
        'clip_deaths': False,
        'stream_prefers_quality': '720p60',
        'buffer_prefers_quality': 'best',
        'max_frames_to_scan_per_second': 16,
        'wait_for_mode': True,

    }
}


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

Check out [overwatch_events.py](Events/overwatch_events.py) to customize events

## Add Other games

Implement a [ScreenRegion](Ocr/screen_region.py) like  [OverwatchActionScreenRegion](Ocr/overwatch_readers/overwatch_action_screen_region.py)

and a [ScreenReader](Ocr/screen_reader.py) like  [OverewatchScreenReader](Ocr/overwatch_readers/overwatch_screen_reader.py)

and a [FrameTester](Ocr/frames/frame_tester.py)  

another example of [ScreenRegion](Ocr/screen_region.py) is [OverwatchActionScreenRegion](Ocr/overwatch_readers/overwatch_searching_for_game_screen_region.py)

Screen regions are the part of the iamge you want to look at.

Screen readers act on them



## Cli

While it's running, type `quit` to shut down gracefully 
