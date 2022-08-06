import re
HEALED = re.compile('HEALED',re.IGNORECASE)
def if_healed(text: str):
    return HEALED.search(text)



