from typing import Dict


class Dict2Class(object):
    _dict: Dict[any, any]

    def __getattribute__(self, attr):
        return object.__getattribute__(self, attr)


    def __init__(self, my_dict):
        self._dict = my_dict
        for key in my_dict:
            setattr(self, key, my_dict[key])
