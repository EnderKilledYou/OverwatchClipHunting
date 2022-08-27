import re



def if_prepare_attack(text: str):
    return re.search('PREPARE', text) is not None and re.search('ATTACK', text) is not None


def if_prepare_defense(text: str):
    return re.search('PREPARE', text) is not None and re.search('DEFENSE', text) is not None


def if_escort(text: str):
    return re.search('ESCORT', text) is not None and  re.search('PAY', text) is not None


def if_contested(text: str):
    return re.search('CONTESTED', text) is not None
