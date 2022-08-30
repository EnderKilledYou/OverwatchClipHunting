import re
from typing import Optional, Match

nated = re.compile('[MI]{1,2}NATE[ED]{1,2}', re.IGNORECASE)


def if_got_elim(text: str) -> bool:
    return (
                       'RTED' in text or 'NATED' in text or 'NATD' in text or 'MNATE' in text or 'MTATD' in text) and 'BY' not in text


def if_got_HOOKED(text: str) -> bool:
    return 'HOOKED +' in text
