"""Contains functions dealing with snake case conversions."""

import re
from typing import Any, Dict

_re_camel_to_snake = re.compile(r"([a-z0-9](?=[A-Z])|[A-Z](?=[A-Z][a-z]))")


def camel_to_snake(name: str) -> str:
    """Convert `name` from camelCase to snake_case."""
    return _re_camel_to_snake.sub(r"\1_", name).lower()


def snake_case_keys(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new dictionary with keys converted to snake_case.

    :param dictionary: The dict to be corrected.

    """
    return {camel_to_snake(k): v for k, v in dictionary.items()}
