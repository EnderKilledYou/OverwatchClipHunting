import re

SLEPT = re.compile('SLEPT',re.IGNORECASE)


def if_slept(text: str):

    return SLEPT.search(text)
