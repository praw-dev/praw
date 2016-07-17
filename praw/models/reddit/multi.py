"""Provide the Multireddit class."""
from json import dumps

from ...const import API_PATH
from ..listing.mixins import SubredditListingMixin
from .base import RedditBase
from .redditor import Redditor
from .subreddit import Subreddit


class Multireddit(RedditBase, SubredditListingMixin):
    """A class for users' Multireddits."""

    STR_FIELD = 'path'

    def __init__(self, reddit, _data):
        """Construct an instance of the Multireddit object."""
        super(Multireddit, self).__init__(reddit, _data)
        self._author = Redditor(reddit, self.path.split('/', 3)[2])
        if 'subreddits' in self.__dict__:
            self.subreddits = [Subreddit(reddit, x['name'])
                               for x in self.subreddits]

    def _info_path(self):
        return API_PATH['multireddit_about'].format(multi=self.name,
                                                    user=self._author)

    def add(self, subreddit):
        """Add a subreddit to this multireddit.

        :param subreddit: The subreddit to add to this multi.

        """
        url = API_PATH['multireddit_update'].format(
            multi=self.name, user=self._author, subreddit=subreddit)
        self._reddit.request(
            'put', url, data={'model': dumps({'name': str(subreddit)})})

    def copy(self, to_name):
        """Copy this multireddit.

        Convenience function that utilizes
        :meth:`.MultiredditMixin.copy_multireddit` populating both
        the `from_redditor` and `from_name` parameters.

        """
        return self._reddit.copy_multireddit(self._author, self.name, to_name)

    def delete(self):
        """Delete this multireddit."""
        self._reddit.request('delete', API_PATH['multireddit_about'].format(
            multi=self.name, user=self._author))

    def edit(self, *args, **kwargs):
        """Edit this multireddit.

        Convenience function that utilizes
        :meth:`.MultiredditMixin.edit_multireddit` populating the `name`
        parameter.

        """
        return self._reddit.edit_multireddit(name=self.name, *args, **kwargs)

    def remove(self, subreddit):
        """Remove a subreddit from this multireddit.

        :param subreddit: The subreddit to remove from this multi.

        """
        url = API_PATH['multireddit_update'].format(
            multi=self.name, user=self._author, subreddit=subreddit)
        self._reddit.request(
            'delete', url, data={'model': dumps({'name': str(subreddit)})})

    def rename(self, new_name, *args, **kwargs):
        """Rename this multireddit.

        This function is a handy shortcut to
        :meth:`rename_multireddit` of the _reddit.

        """
        new = self._reddit.rename_multireddit(self.name, new_name, *args,
                                              **kwargs)
        self.__dict__.update(new.__dict__)
        return self
