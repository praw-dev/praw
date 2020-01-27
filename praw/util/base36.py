"""Provides a function to convert from int to base36."""


def int_to_base36(num):
    """Convert a positive integer into a base36 string.

    :param num: The number to convert
    :returns: A base36 string
    """
    assert num >= 0
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    res = ""
    while not res or num > 0:
        num, i = divmod(num, 36)
        res = digits[i] + res
    return res.lower()
