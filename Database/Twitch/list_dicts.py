from Database.Twitch.dict_to_class import Dict2Class


def list_dicts(items):
    return map(lambda x: Dict2Class(x.to_dict()), items)
