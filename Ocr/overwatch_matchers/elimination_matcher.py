import re
from typing import Optional, Match


def if_got_elim(text: str) -> bool:
    return 'RTED' in text or 'NATED' in text or 'NATD' in text or 'MNATE' in text or 'MTATD' in text


def if_got_HOOKED(text: str) -> bool:
    return 'HOOKED +' in text
