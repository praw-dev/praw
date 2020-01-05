"""A placeholder for the old modaction.py file.

The new file can be found at praw/models/mod_action.py.

Do not import this module, as it is deprecated.
"""

import warnings

from .mod_action import *  # noqa

warnings.warn(
    "The name modaction has been deprecated. "
    "Please import modaction as mod_action. "
    "This feature will be removed on the next major version release.",
    DeprecationWarning,
    stacklevel=2,
)
