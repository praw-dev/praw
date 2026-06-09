"""Provide the ReportableMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from praw.const import API_PATH

if TYPE_CHECKING:
    import praw


class ReportableMixin:
    """Interface for :class:`.RedditBase` classes that can be reported."""

    if TYPE_CHECKING:
        # Provided by the host class (:class:`.RedditBase`).
        _reddit: praw.Reddit

        @property
        def fullname(self) -> str: ...  # noqa: D102

    def report(self, reason: str) -> None:
        """Report this object to the moderators of its subreddit.

        :param reason: The reason for reporting.

        :raises: :class:`.RedditAPIException` if ``reason`` is longer than 100
            characters.

        Example usage:

        .. code-block:: python

            submission = reddit.submission("5or86n")
            submission.report("report reason")

            comment = reddit.comment("dxolpyc")
            comment.report("report reason")

        """
        self._reddit.post(API_PATH["report"], data={"id": self.fullname, "reason": reason})
