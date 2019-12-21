"""Private functions used by the validate_types family of functions."""


def _remove_extra_attrs(dictionary):
    for attr in ("expected_types", "variable_name", "ignore_none"):
        try:
            dictionary.pop(attr)
        except KeyError:
            pass
    return dictionary
