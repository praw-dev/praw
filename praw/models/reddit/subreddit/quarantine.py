"""Provide the SubredditQuarantine class."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from prawcore import Redirect

from praw.const import API_PATH

if TYPE_CHECKING:
    from praw import models


class SubredditQuarantine:
    """Provides subreddit quarantine related methods.

    To opt-in into a quarantined subreddit:

    .. code-block:: python

        reddit.subreddit("test").quaran.opt_in()

    """

    def __init__(self, subreddit: models.Subreddit) -> None:
        """Initialize a :class:`.SubredditQuarantine` instance.

        :param subreddit: The :class:`.Subreddit` associated with the quarantine.

        """
        self.subreddit = subreddit

    def opt_in(self) -> None:
        """Permit your user access to the quarantined subreddit.

        Usage:

        .. code-block:: python

            subreddit = reddit.subreddit("QUESTIONABLE")
            next(subreddit.hot())  # Raises prawcore.Forbidden

            subreddit.quaran.opt_in()
            next(subreddit.hot())  # Returns Submission

        """
        data = {"sr_name": self.subreddit}
        with contextlib.suppress(Redirect):
            self.subreddit._reddit.post(API_PATH["quarantine_opt_in"], data=data)

    def opt_out(self) -> None:
        """Remove access to the quarantined subreddit.

        Usage:

        .. code-block:: python

            subreddit = reddit.subreddit("QUESTIONABLE")
            next(subreddit.hot())  # Returns Submission

            subreddit.quaran.opt_out()
            next(subreddit.hot())  # Raises prawcore.Forbidden

        """
        data = {"sr_name": self.subreddit}
        with contextlib.suppress(Redirect):
            self.subreddit._reddit.post(API_PATH["quarantine_opt_out"], data=data)
