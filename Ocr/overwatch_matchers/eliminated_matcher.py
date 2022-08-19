import re
natedby = re.compile('(NATED BY|YOU WERE)',re.IGNORECASE)
ifmenu = re.compile('ENTER THE ARCADE',re.IGNORECASE)
ifblocking = re.compile('BLOCKING',re.IGNORECASE)
iforb = re.compile('GAINED',re.IGNORECASE)
ifobjectivedefense = re.compile('DEFENSE',re.IGNORECASE)

def if_got_elimed(text: str):
    return natedby.search(text)


def if_menu(text: str):
    return ifmenu.search(text)

def if_blocking(text: str):
    return ifblocking.search(text)

def if_orb_gain(text: str):
    return iforb.search(text)

def if_objective_defense(text: str):
    return ifobjectivedefense.search(text)