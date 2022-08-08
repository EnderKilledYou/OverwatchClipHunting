from Ocr.twitch_video_frame_buffer import TwitchVideoFrameBuffer

frame_buffers = {}


def get_frame_buffer(broadcaster: str) -> TwitchVideoFrameBuffer:
    return frame_buffers[broadcaster]


def set_frame_buffer(broadcaster, ocr :TwitchVideoFrameBuffer):
    frame_buffers[broadcaster] = ocr
