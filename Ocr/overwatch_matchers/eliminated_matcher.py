import re


def if_got_elimed(text: str):
    return re.search('(NATED BY|YOU WERE)', text, re.IGNORECASE) is not None


def if_menu(text: str):
    return re.search('ENTER THE ARCADE', text, re.IGNORECASE) is not None


def if_blocking(text: str):
    return re.search('BLOCKING', text, re.IGNORECASE) is not None


def if_orb_gain(text: str):
    return re.search('GAINED', text, re.IGNORECASE) is not None


def if_objective_defense(text: str):
    return re.search('DEFENSE', text, re.IGNORECASE) is not None
