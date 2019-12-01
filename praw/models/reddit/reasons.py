"""Provide the Reason class."""
from ...const import API_PATH
from ...exceptions import ClientException
from .base import RedditBase


class Reason(RedditBase):
    """An individual Reason object.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``id``                  The id of the removal reason.
    ``title``               The title of the removal reason.
    ``message``             The message of the removal reason.
    ======================= ===================================================
    """

    STR_FIELD = "id"

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        if isinstance(other, str):
            return other == str(self)
        return (
            isinstance(other, self.__class__)
            and str(self) == str(other)
            and other.subreddit == self.subreddit
        )

    def __hash__(self):
        """Return the hash of the current instance."""
        return (
            hash(self.__class__.__name__)
            ^ hash(str(self))
            ^ hash(self.subreddit)
        )

    def __init__(self, reddit, subreddit, reason_id, _data=None):
        """Construct an instance of the Reason object."""
        self.id = reason_id
        self.subreddit = subreddit
        super(Reason, self).__init__(reddit, _data=_data)

    def _fetch(self):
        for reason in self.subreddit.reasons:
            if reason.id == self.id:
                self.__dict__.update(reason.__dict__)
                self._fetched = True
                return
        raise ClientException(
            "/r/{} does not have the reason {}".format(self.subreddit, self.id)
        )


class SubredditReasons:
    """Provide a set of functions to a Subreddit's removal reasons."""

    def __getitem__(self, reason_id):
        """Lazily return the Reason for the subreddit with id ``reason_id``.

        :param reason_id: The id of the removal reason

        This method is to be used to fetch a specific removal reason, like so:

        .. code:: python

           reason = reddit.subreddit('praw_test').reasons['141vv5c16py7d']
           print(reason)

        """
        return Reason(self._reddit, self.subreddit, reason_id)

    def __init__(self, subreddit):
        """Create a SubredditReasons instance.

        :param subreddit: The subreddit whose removal reasons to work with.

        """
        self.subreddit = subreddit
        self._reddit = subreddit._reddit

    def __iter__(self):
        """Return a list of Removal Reasons for the subreddit.

        This method is used to discover all removal reasons for a
        subreddit:

        .. code-block:: python

           for reason in reddit.subreddit('NAME').reasons:
               print(reason)

        """
        response = self.subreddit._reddit.get(
            API_PATH["removal_reasons_list"].format(subreddit=self.subreddit)
        )
        for reason_id, reason_data in response["data"].items():
            yield Reason(
                self._reddit, self.subreddit, reason_id, _data=reason_data
            )

    def add(self, title, message):
        """Add a removal reason to this subreddit.

        :param title: The title of the removal reason
        :param message: The message to send the user.
        :returns: The Reason added.

        The message will be prepended with `Hi u/username,` automatically.

        To add ``'test'`` to the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').reason.add('test','This is a test')

        """
        data = {"title": title, "message": message}
        url = API_PATH["removal_reasons_list"].format(subreddit=self.subreddit)
        reason_id = self.subreddit._reddit.post(url, data=data)
        return Reason(self._reddit, self.subreddit, reason_id)

    def update(self, reason_id, title, message):
        """Update the removal reason from this subreddit by ``reason_id``.

        :param reason_id: The id of the removal reason
        :param title: The removal reason's new title (required).
        :param message: The removal reason's new message (required).

        To update ``'141vv5c16py7d'`` from the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').reason.update(
               '141vv5c16py7d',
               'New Title',
               'New message')

        """
        url = API_PATH["removal_reason"].format(
            subreddit=self.subreddit, id=reason_id
        )
        data = {"title": title, "message": message}
        self.subreddit._reddit.put(url, data=data)

    def delete(self, reason_id):
        """Delete a removal reason from this subreddit.

        :param reason_id: The id of the removal reason to remove

        To delete ``'141vv5c16py7d'`` from the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').reason.delete('141vv5c16py7d')

        """
        url = API_PATH["removal_reason"].format(
            subreddit=self.subreddit, id=reason_id
        )
        self.subreddit._reddit.request("DELETE", url)
