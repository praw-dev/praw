"""Provide the PRAWBase superclass."""
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .. import Reddit


class PRAWBase:
    """Superclass for all models in PRAW."""

    @staticmethod
    def _safely_add_arguments(argument_dict, key, **new_arguments):
        """Replace argument_dict[key] with a deepcopy and update.

        This method is often called when new parameters need to be added to a
        request. By calling this method and adding the new or updated
        parameters we can insure we don't modify the dictionary passed in by
        the caller.

        """
        value = deepcopy(argument_dict[key]) if key in argument_dict else {}
        value.update(new_arguments)
        argument_dict[key] = value

    @classmethod
    def parse(cls, data: Dict[str, Any], reddit: "Reddit") -> Any:
        """Return an instance of ``cls`` from ``data``.

        :param data: The structured data.
        :param reddit: An instance of :class:`.Reddit`.

        """
        return cls(reddit, _data=data)

    def __init__(self, reddit: "Reddit", _data: Optional[Dict[str, Any]]):
        """Initialize a PRAWModel instance.

        :param reddit: An instance of :class:`.Reddit`.

        """
        self._reddit = reddit
        if _data:
            for attribute, value in _data.items():
                setattr(self, attribute, value)
