"""A subsection of utils for :func:`~.validate_types."""

# flake8: noqa

from ._private_funcs import _remove_extra_attrs
from .validate_types import validate_types
from .validate_defaults import (
    validate_id,
    validate_url,
    validate_path,
)
