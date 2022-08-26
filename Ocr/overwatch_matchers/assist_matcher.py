import re

ass = re.compile('ASSIST', re.IGNORECASE)


def if_assist(text: str):
    search = ass.search(text)
    return search is not None
