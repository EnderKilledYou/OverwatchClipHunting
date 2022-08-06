import re


def if_prepare_attack(text: str):
    words = text.split(' ')
    return words.count('PREPARE') > 0 and words.count('ATTACK') > 0


def if_prepare_defense(text: str):
    words = text.split(' ')
    return words.count('PREPARE') > 0 and words.count('DEFENSES') > 0
