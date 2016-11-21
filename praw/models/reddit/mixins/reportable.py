"""Provide the ReportableMixin class."""
from ....const import API_PATH


class ReportableMixin(object):
    """Interface for RedditBase classes that can be reported."""

    def report(self, reason):
        """Report this object to the moderators of its subreddit.

        :param reason: The reason for reporting.

        """
        self._reddit.post(API_PATH['report'],
                          data={'id': self.fullname, 'reason': reason})
