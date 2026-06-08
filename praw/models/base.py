"""Provide the PRAWBase superclass."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import praw


class PRAWBase:
    """Superclass for all models in PRAW."""

    @staticmethod
    def _safely_add_arguments(*, arguments: dict[str, Any], key: str, **new_arguments: Any) -> None:
        """Replace arguments[key] with a deepcopy and update.

        This method is often called when new parameters need to be added to a request.
        By calling this method and adding the new or updated parameters we can insure we
        don't modify the dictionary passed in by the caller.

        """
        value = deepcopy(arguments[key]) if key in arguments else {}
        value.update(new_arguments)
        arguments[key] = value

    @staticmethod
    def _to_local_datetime(timestamp: float) -> datetime:
        """Return ``timestamp`` as a timezone-aware :class:`datetime.datetime`.

        :param timestamp: A `Unix Time`_ value, in seconds.

        The returned object is localized to the system's timezone.

        .. _unix time: https://en.wikipedia.org/wiki/Unix_time

        """
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone()

    @classmethod
    def parse(cls, data: dict[str, Any], reddit: praw.Reddit) -> PRAWBase:
        """Return an instance of ``cls`` from ``data``.

        :param data: The structured data.
        :param reddit: An instance of :class:`.Reddit`.

        """
        return cls(reddit, _data=data)

    def __init__(self, reddit: praw.Reddit, _data: dict[str, Any] | None) -> None:
        """Initialize a :class:`.PRAWBase` instance.

        :param reddit: An instance of :class:`.Reddit`.

        """
        self._reddit = reddit
        if _data:
            for attribute, value in _data.items():
                setattr(self, attribute, value)
