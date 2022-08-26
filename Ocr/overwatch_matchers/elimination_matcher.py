import re
from typing import Optional, Match

nated = re.compile('[MI]{1,2}NATE[ED]{1,2}', re.IGNORECASE)


def if_got_elim(text: str) -> Optional[Match[str]]:
    return nated.search(text) is not None
