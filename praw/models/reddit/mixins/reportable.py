"""Provide the ReportableMixin class."""


class ReportableMixin(object):
    """Interface for classes that can be reported."""

    def report(self, reason=None):
        """Report this object to the moderators.

        :param reason: The user-supplied reason for reporting a comment
            or submission. Default: None (blank reason)
        :returns: The json response from the server.

        """
        url = self._reddit.config['report']
        data = {'id': self.fullname}
        if reason:
            data['reason'] = reason
        return self._reddit.request(url, data=data)
