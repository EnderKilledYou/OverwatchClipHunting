import re





def if_in_hero_room(text: str):
    return re.search('PRESS H TO CHANGE HERO',text) is not None


def if_in_queue(text: str):
    return re.search("TIME ELAPSED",text) is not None or re.search("SEARCHING",text) is not None
