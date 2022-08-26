import re
HEALED = re.compile('HEALING',re.IGNORECASE)
def if_healing(text: str):

    return HEALED.search(text)  is not None

