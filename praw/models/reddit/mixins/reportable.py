"""Provide the ReportableMixin class."""
from ....const import API_PATH


class ReportableMixin:
    """Interface for RedditBase classes that can be reported."""

    def report(self, reason):
        """Report this object to the moderators of its subreddit.

        :param reason: The reason for reporting.

        .. note:: Only instances of :class:`.Submission` and :class:`.Comment`
            can be reported to a subreddit's moderators.

        Raises :class:`.RedditAPIException` if ``reason`` is longer than 100
        characters.

        Example usage:

        .. code-block:: python

           submission = reddit.submission(id='5or86n')
           submission.report('report reason')

           comment = reddit.comment(id='dxolpyc')
           comment.report('report reason')

        """
        if self.__class__.__name__.lower() not in ["submission", "comment"]:
            raise TypeError(
                "{}s can not be reported to moderators.".format(
                    self.__class__.__name__
                )
            )
        data = {"id": self.fullname, "reason": reason}
        self._reddit.post(API_PATH["report"], data=data)

    def report_admin(self, reason, explanation=""):
        """Report this object to the Reddit admins.

        :param reason: The reason for reporting.
        :param explanation: A more-detailed explanation of the problem
            (Optional).

        Example usage:

        .. code-block:: python

           submission = reddit.submission(id='5or86n')
           submission.report_admin('report reason')

           comment = reddit.comment(id='dxolpyc')
           comment.report_admin('report reason', explanation="Some reason")

           redditor = reddit.redditor("spez")
           redditor.report_admin("report reason")

           subreddit = reddit.subreddit('test')
           subreddit.report_admin('report reason', explanation="A reason")


        """
        self._reddit.post(
            API_PATH["report"],
            data={
                "id": self.fullname,
                "reason": "site_reason_selected",
                "site_reason": reason,
                "custom_text": explanation,
            },
        )
