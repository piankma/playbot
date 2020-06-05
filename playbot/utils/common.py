import re


def safeget(obj, path, default=""):
    attrs = str(path).split(".")
    result = obj
    for attr in attrs:
        try:
            if isinstance(result, dict):
                result = result[attr]
            elif isinstance(result, (list, tuple)) and re.match(r"^\-?\d+$", attr):
                result = result[int(attr)]
            else:
                result = getattr(result, attr)
        except (AttributeError, KeyError, IndexError):
            return default
    return result


sget = safeget
