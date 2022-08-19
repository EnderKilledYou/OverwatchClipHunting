import re


def if_in_hero_room(text: str):
    return text.count('PRESS H TO CHANGE HERO') > 0


def if_in_queue(text: str):
    return text.count("TIME ELAPSED") > 0 or text.count("SEARCHING") > 0
