import re


def count_elim_on_frame(text: str):
    return re.search("NATED",text) is not None
