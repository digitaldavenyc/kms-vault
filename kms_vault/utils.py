

def get_section(obj, keys):
    for key in keys:
        if key not in obj:
            obj[key] = {}
        obj = obj[key]
    return obj


def walk(obj, func):
    if not isinstance(obj, dict):
        raise TypeError('should be a dict')
    for key, value in obj.items():
        if isinstance(value, dict):
            walk(value, func)
        else:
            obj[key] = func(value)
