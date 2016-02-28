"""Provide the ReportableMixin class."""
from ..redditmodel import RedditModel


class ReportableMixin(RedditModel):
    """Interface for RedditModel classes that can be reported."""

    def report(self, reason=None):
        """Report this object to the moderators.

        :param reason: The user-supplied reason for reporting a comment
            or submission. Default: None (blank reason)
        :returns: The json response from the server.

        """
        url = self.reddit_session.config['report']
        data = {'id': self.fullname}
        if reason:
            data['reason'] = reason
        return self.reddit_session.request_json(url, data=data)
