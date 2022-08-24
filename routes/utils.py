



def query_to_list(clips_response):
    clip_list = []
    for i in clips_response:
        clip_list.append(i.to_dict())
    return clip_list
