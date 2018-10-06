"""Provide the RemovalReason class."""
from ...const import API_PATH
from .base import RedditBase


class RemovalReason(RedditBase):
    """A removal reason for a subreddit."""

    STR_FIELD = 'id'

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        if isinstance(other, str):
            return other == str(self)
        return (isinstance(other, self.__class__) and
                str(self) == str(other))

    def __hash__(self):
        """Return the hash of the current instance."""
        return hash(str(self))

    def __init__(self, reddit, subreddit,
                 id,  # pylint: disable=redefined-builtin
                 title, message, _data=None):
        """Construct an instance of the RemovalReason object."""
        self.subreddit = subreddit
        self.id = id  # pylint: disable=invalid-name
        self.title = title
        self.message = message
        super(RemovalReason, self).__init__(reddit, _data)

    def delete(self):
        """Delete a removal reason from its subreddit."""
        url = API_PATH['removal_reason_update'].format(
            id=self.id, subreddit=self.subreddit)
        self._reddit.request('DELETE', url)

        # Update the list to match.
        self.subreddit.removal_reasons._reasons.remove(self)

    def edit(self, title=None, message=None):
        """Edit a removal reason."""
        if title is None:
            title = self.title
        if message is None:
            message = self.message
        url = API_PATH['removal_reason_update'].format(
            id=self.id, subreddit=self.subreddit)
        self._reddit.request('PUT', url, {"title": title, "message": message})
        self.title = title
        self.message = message


class SubredditRemovalReasons(object):
    """Provides management functions for a subreddit's removal reasons."""

    def __getitem__(self, id):  # pylint:disable=invalid-name,redefined-builtin
        """Return a :class:`.RemovalReason` from this subreddit by ID.

        :param id: The ID of the removal reason
        """
        for reason in self._reasons:
            if reason.id == id:
                return reason
        raise KeyError('/r/{} does not have a removal reason of ID {}'
                       .format(self.subreddit, id))

    def __init__(self, subreddit):
        """Create a SubredditRemovalReasons instance.

        :param subreddit: The subreddit whose removal reasons are
            affected
        """
        self.subreddit = subreddit
        self._reddit = subreddit._reddit
        raw = self._reddit.get(
            API_PATH['removal_reasons'].format(subreddit=self.subreddit))
        # The returned object has a dictionary called "data", followed by
        # a list called "order" which has dictionary keys in iteration
        # order, so start by getting the corresponding values:
        data = (raw["data"][k] for k in raw["order"])
        # then convert them to our model:
        self._reasons = [RemovalReason(self._reddit,
                                       self.subreddit,
                                       reason["id"],
                                       reason["title"],
                                       reason["message"])
                         for reason in data]

    def __iter__(self):
        """Iterate over the removal reasons for this subreddit, in order."""
        return iter(self._reasons)

    def add(self, title, message):
        """Add a removal reason to this subreddit.

        :param title: The title of the removal reason
        :param message: The body of the removal reason
        :returns: The RemovalReason added
        """
        url = API_PATH['removal_reasons'].format(subreddit=self.subreddit)
        response = self._reddit.post(url, {"title": title, "message": message})
        reason = RemovalReason(self._reddit,
                               self.subreddit,
                               response["id"],
                               title,
                               message)
        self._reasons.append(reason)
        return reason
