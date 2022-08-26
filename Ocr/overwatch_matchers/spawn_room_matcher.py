import re

SPAWN = re.compile('PRESS H TO CHANGE HERO', re.IGNORECASE)
TIME = re.compile("TIME ELAPSED", re.IGNORECASE)
SEARCHING = re.compile("SEARCHING", re.IGNORECASE)


def if_in_hero_room(text: str):
    return SPAWN.search(text) is not None


def if_in_queue(text: str):
    return TIME.search(text) is not None or SEARCHING.search(text) is not None
