import re


def if_got_elimed(text: str):
    return 'YOU WERE' in text or 'NATED BY' in text



def if_menu(text: str):
    return 'ENTER THE ARCADE' in text


def if_blocking(text: str):
    return 'BLOCKING' in text


def if_orb_gain(text: str):
    return 'GAINED' in text


def if_objective_defense(text: str):
    return 'DEFENSE' in text
