from typing import Dict


class Dict2Class(object):
    _dict: Dict[any, any]

    def __getattribute__(self, attr):
        return object.__getattribute__(self, attr)


    def __init__(self, my_dict):
        self._dict = my_dict
        for key in my_dict:
            if isinstance(my_dict[key],bytes):
                str(my_dict[key], "utf-8")
            else:
                setattr(self, key, my_dict[key])
