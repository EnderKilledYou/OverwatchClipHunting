import re


def if_prepare_attack(text: str):
    return 'PREPARE' in text and 'ATTACK' in text


def if_prepare_defense(text: str):
    return 'PREPARE' in text and 'DEFENSE' in text


def if_escort(text: str):
    return 'ESCORT' in text and 'PAY' in text


def if_contested(text: str):
    return 'CONTESTED' in text
