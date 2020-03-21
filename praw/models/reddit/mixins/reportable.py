"""Provide the ReportableMixin class."""
from ....const import API_PATH


class ReportableMixin:
    """Interface for RedditBase classes that can be reported."""

    def report(self, reason, admin=False, explanation=""):
        """Report this object to the moderators of its subreddit.

        :param reason: The reason for reporting.
        :param admin: Report to Reddit admins instead of moderatiors.
        :param explanation: When reporting to admins, include this text as a
            more-detailed explanation of the problem (Optional).

        .. note:: Only instances of :class:`.Submission` and :class:`.Comment`
            can be reported to a subreddit's moderators.

        Raises :class:`.RedditAPIException` if ``reason`` is longer than 100
        characters.

        Example usage:

        .. code-block:: python

           submission = reddit.submission(id='5or86n')
           submission.report('report reason')

           comment = reddit.comment(id='dxolpyc')
           comment.report('report reason', admin=True)

           subreddit = reddit.subreddit('test')
           subreddit.report('report reason', admin=True)

        """
        if (
            self.__class__.__name__.lower() not in ["submission", "comment"]
            and not admin
        ):
            raise TypeError(
                "{}s can only be reported to admins.".format(
                    self.__class__.__name__
                )
            )
        data = {"id": self.fullname, "reason": reason}
        if admin:
            data.update(
                {
                    "reason": "site_reason_selected",
                    "site_reason": reason,
                    "custom_text": explanation,
                }
            )
        self._reddit.post(API_PATH["report"], data=data)
