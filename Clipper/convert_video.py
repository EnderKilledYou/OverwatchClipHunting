from pyffmpeg import FFmpeg


def opencv_video_save_as(video_path, save_path):
    """
    video save as video
    :param video_path:
    :param save_path:
    :return:
    """
    ff = FFmpeg()
    output_file = ff.convert(video_path, save_path)
    print(output_file)
