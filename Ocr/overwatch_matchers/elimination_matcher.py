import re
from typing import Optional, Match


def if_got_elim(text: str) -> Optional[Match[str]]:
    return 'NATED' in text or 'NATD' in text or 'MNATE' in text or 'MTATD' in text

