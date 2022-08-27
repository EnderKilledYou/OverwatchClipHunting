import re
from typing import Optional, Match


def if_got_elim(text: str) -> Optional[Match[str]]:
    return re.search('[MI]{1,2}NATE[ED]{1,2}', text, re.IGNORECASE) is not None
