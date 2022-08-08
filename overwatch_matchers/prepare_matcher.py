import re

PREPARE = re.compile('PREPARE', re.IGNORECASE)
ATTACK = re.compile('ATTACK', re.IGNORECASE)
DEFENSE = re.compile('DEFENSE', re.IGNORECASE)
ESCORT = re.compile('ESCORT', re.IGNORECASE)
PAY = re.compile('PAY', re.IGNORECASE)
CONTESTED = re.compile('CONTESTED', re.IGNORECASE)


def if_prepare_attack(text: str):
    words = text.split(' ')
    return PREPARE.search(text) and ATTACK.search(text)


def if_prepare_defense(text: str):
    return PREPARE.search(text) and DEFENSE.search(text)


def if_escort(text: str):
    return ESCORT.search(text) and PAY.search(text)


def if_contested(text: str):
    return CONTESTED.search(text)

