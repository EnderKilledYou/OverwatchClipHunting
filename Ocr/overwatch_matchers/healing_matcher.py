import re


def if_healing(text: str):
    return re.search('HEALING', text) is not None
