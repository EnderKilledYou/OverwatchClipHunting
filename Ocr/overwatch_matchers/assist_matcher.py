import re


def if_assist(text: str):
    return re.search('ASSIST', text, re.IGNORECASE) is not None
