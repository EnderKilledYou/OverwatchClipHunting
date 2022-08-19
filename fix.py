import json_fix
import json

from twitchAPI import Twitch

class_checker = lambda obj: isinstance(obj, Twitch)
class_checker_bytes = lambda obj: isinstance(obj, bytes)
class_checker_default = lambda obj: isinstance(obj, object)

# then assign it to a function that does the converting
json.override_table[class_checker] = lambda obj_of_that_class: "Twitch Api"
json.override_table[class_checker_bytes] = lambda obj_of_that_class: str(obj_of_that_class, "utf-8")
json.override_table[class_checker_default] = lambda obj_of_that_class: obj_of_that_class.to_dict() if hasattr(
    obj_of_that_class, 'to_dict') else str(obj_of_that_class)
