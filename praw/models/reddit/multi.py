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

    def add_subreddit(self, subreddit, _delete=False, *args, **kwargs):
        """Add a subreddit to the multireddit.

        :param subreddit: The subreddit name or Subreddit object to add

        The additional parameters are passed directly into
        :meth:`~praw.__init__.BaseReddit.request_json`.

        """
        subreddit = str(subreddit)
        url = self._reddit.config['multireddit_add'].format(
            user=self._author, multi=self.name, subreddit=subreddit)
        method = 'DELETE' if _delete else 'PUT'
        data = {'model': dumps({'name': subreddit})}
        self._reddit.request(method, url, data=data, *args, **kwargs)

    def copy(self, to_name):
        """Copy this multireddit.

        Convenience function that utilizes
        :meth:`.MultiredditMixin.copy_multireddit` populating both
        the `from_redditor` and `from_name` parameters.

        """
        return self._reddit.copy_multireddit(self._author, self.name, to_name)

    def delete(self):
        """Delete this multireddit.

        Convenience function that utilizes
        :meth:`.MultiredditMixin.delete_multireddit` populating the `name`
        parameter.

        """
        return self._reddit.delete_multireddit(self.name)

    def edit(self, *args, **kwargs):
        """Edit this multireddit.

        Convenience function that utilizes
        :meth:`.MultiredditMixin.edit_multireddit` populating the `name`
        parameter.

        """
        return self._reddit.edit_multireddit(name=self.name, *args, **kwargs)

    def remove_subreddit(self, subreddit, *args, **kwargs):
        """Remove a subreddit from the user's multireddit."""
        return self.add_subreddit(subreddit, True, *args, **kwargs)

    def rename(self, new_name, *args, **kwargs):
        """Rename this multireddit.

        This function is a handy shortcut to
        :meth:`rename_multireddit` of the _reddit.

        """
        new = self._reddit.rename_multireddit(self.name, new_name, *args,
                                              **kwargs)
        self.__dict__.update(new.__dict__)
        return self
