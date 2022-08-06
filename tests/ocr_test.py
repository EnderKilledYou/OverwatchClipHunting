import json

from Ocr.twitch_video_frame_buffer import TwitchVideoFrameBuffer

ocr = TwitchVideoFrameBuffer('../warn1.mp4', 8)
results = ocr.buffer_twitch_broadcast()
#results2 = list(filter(lambda x: match_eliminated(x.text),results))
print(results)
out_file = open("../ocr3.json", "w")

json.dump(list(map(lambda x: {'ts_second':x.ts_second,'text':x.text,'frame_number':x.frame_number},results)), out_file, indent=6)
out_file.close()