import vlc

# importing time module
import time


# creating vlc media player object
media_player :vlc.MediaPlayer = vlc.MediaPlayer()

# media object
media :vlc.Media = vlc.Media("1mp4.mkv")

# setting media to the media player
media_player.set_media(media)

# start playing video
media_player.play()

# wait so the video can be played for 5 seconds
# irrespective for length of video
time.sleep(5)

# setting position
media_player.set_position(0.3)

media_player.next_frame()
media_player.video_take_snapshot()

# getting position
value = media_player.get_position()

# printing value
print("Current media Position: ")
print(value)