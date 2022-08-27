import re





def if_in_hero_room(text: str):
    return 'PRESS H TO CHANGE HERO' in text


def if_in_queue(text: str):
    return "TIME ELAPSED" in text or "SEARCHING" in text
