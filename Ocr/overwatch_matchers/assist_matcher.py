import re
ass = re.compile('ASSIST', re.IGNORECASE)

def if_assist(text: str):

    return ass.search(text)
