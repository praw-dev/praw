"""Provide the ReportableMixin class."""
from ....const import API_PATH


class ReportableMixin(object):
    """Interface for RedditBase classes that can be reported."""

    def report(self, reason):
        """Report this object to the moderators of its subreddit.

        :param reason: The reason for reporting.

        Example usage:

        .. code:: python

           submission = reddit.submission(id='5or86n')
           submission.report('report reason')

           comment = reddit.comment(id='dxolpyc')
           comment.report('report reason')

        """
        self._reddit.post(
            API_PATH["report"], data={"id": self.fullname, "reason": reason}
        )
