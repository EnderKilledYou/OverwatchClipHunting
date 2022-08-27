import re




def if_slept(text: str):

    return re.search('SLEPT',text)  is not None
