"""Provide the Multireddit class."""
from json import dumps

from ..listing.mixins import SubredditListingMixin
from .base import RedditBase


class Multireddit(RedditBase, SubredditListingMixin):
    """A class for users' Multireddits.

    @Classmethod
    def from_api_response(cls, reddit, json_dict):
        from .models.subreddit import Subreddit
        # The Multireddit response contains the Subreddits attribute as a list
        # of dicts of the form {'name': 'subredditname'}.
        # We must convert each of these into a Subreddit object.
        json_dict['subreddits'] = [Subreddit(reddit, item['name'])
                                   for item in json_dict['subreddits']]
        return cls(reddit, None, None, json_dict)

    def _transform_data(self):
        # Subreddits are returned as dictionaries in the form
        # {'name': 'subredditname'}. Convert them to Subreddit objects.
        self.subreddits = [Subreddit(self._reddit, item['name'])
                           for item in self.subreddits]

        # paths are of the form "/user/{USERNAME}/m/{MULTINAME}"
        author = self.path.split('/')[2]
        self.author = Redditor(self._reddit, author)

    """

    def __init__(self, reddit, author=None, name=None, json_dict=None,
                 fetch=False, **kwargs):
        """Construct an instance of the Multireddit object."""
        author = str(author) if author \
            else json_dict['path'].split('/')[-3]
        if not name:
            name = json_dict['path'].split('/')[-1]

        info_url = reddit.config['multireddit_about'].format(
            user=author, multi=name)
        self.name = name
        self._author = author
        super(Multireddit, self).__init__(reddit, json_dict, fetch, info_url,
                                          **kwargs)
        self._url = reddit.config['multireddit'].format(
            user=author, multi=name)

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
