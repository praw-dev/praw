"""Provide the SubredditQuarantine class."""

from prawcore import Redirect

from ....const import API_PATH


class SubredditQuarantine:
    """Provides subreddit quarantine related methods.

    To opt-in into a quarantined subreddit:

    .. code-block:: python

        reddit.subreddit('test').quaran.opt_in()

    """

    def __init__(self, subreddit):
        """Create a SubredditQuarantine instance.

        :param subreddit: The subreddit associated with the quarantine.

        """
        self.subreddit = subreddit

    def opt_in(self):
        """Permit your user access to the quarantined subreddit.

        Usage:

        .. code-block:: python

           subreddit = reddit.subreddit('QUESTIONABLE')
           next(subreddit.hot())  # Raises prawcore.Forbidden

           subreddit.quaran.opt_in()
           next(subreddit.hot())  # Returns Submission

        """
        data = {"sr_name": self.subreddit}
        try:
            self.subreddit._reddit.post(
                API_PATH["quarantine_opt_in"], data=data
            )
        except Redirect:
            pass

    def opt_out(self):
        """Remove access to the quarantined subreddit.

        Usage:

        .. code-block:: python

           subreddit = reddit.subreddit('QUESTIONABLE')
           next(subreddit.hot())  # Returns Submission

           subreddit.quaran.opt_out()
           next(subreddit.hot())  # Raises prawcore.Forbidden

        """
        data = {"sr_name": self.subreddit}
        try:
            self.subreddit._reddit.post(
                API_PATH["quarantine_opt_out"], data=data
            )
        except Redirect:
            pass
