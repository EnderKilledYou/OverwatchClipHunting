def list_to_dict(field, items):
    _dict = {}
    for item in items:
        _dict[getattr(item, field)] = item
    return _dict
