"""Provide the Multireddit class."""

from json import dumps

from six import text_type

from .mixins.listing import Listing


class Multireddit(Listing):
    """A class for users' Multireddits."""
    @classmethod
    def from_api_response(cls, reddit_session, json_dict):
        """Return an instance of the appropriate class from the json dict."""
        from .models.subreddit import Subreddit
        # The Multireddit response contains the Subreddits attribute as a list
        # of dicts of the form {'name': 'subredditname'}.
        # We must convert each of these into a Subreddit object.
        json_dict['subreddits'] = [Subreddit(reddit_session, item['name'])
                                   for item in json_dict['subreddits']]
        return cls(reddit_session, None, None, json_dict)

    def __init__(self, reddit_session, author=None, name=None,
                 json_dict=None, fetch=False, **kwargs):
        """Construct an instance of the Multireddit object."""
        author = text_type(author) if author \
            else json_dict['path'].split('/')[-3]
        if not name:
            name = json_dict['path'].split('/')[-1]

        info_url = reddit_session.config['multireddit_about'].format(
            user=author, multi=name)
        self.name = name
        self._author = author
        super(Multireddit, self).__init__(reddit_session, json_dict, fetch,
                                          info_url, **kwargs)
        self._url = reddit_session.config['multireddit'].format(
            user=author, multi=name)

    def __repr__(self):
        """Return a code representation of the Multireddit."""
        return 'Multireddit(author=\'{0}\', name=\'{1}\')'.format(
            self._author, self.name)

    def __unicode__(self):
        """Return a string representation of the Multireddit."""
        return self.name

    def _post_populate(self, fetch):
        from .models.redditor import Redditor
        from .models.subreddit import Subreddit
        if fetch:
            # Subreddits are returned as dictionaries in the form
            # {'name': 'subredditname'}. Convert them to Subreddit objects.
            self.subreddits = [Subreddit(self.reddit_session, item['name'])
                               for item in self.subreddits]

            # paths are of the form "/user/{USERNAME}/m/{MULTINAME}"
            author = self.path.split('/')[2]
            self.author = Redditor(self.reddit_session, author)

    def add_subreddit(self, subreddit, _delete=False, *args, **kwargs):
        """Add a subreddit to the multireddit.

        :param subreddit: The subreddit name or Subreddit object to add

        The additional parameters are passed directly into
        :meth:`~praw.__init__.BaseReddit.request_json`.

        """
        subreddit = text_type(subreddit)
        url = self.reddit_session.config['multireddit_add'].format(
            user=self._author, multi=self.name, subreddit=subreddit)
        method = 'DELETE' if _delete else 'PUT'
        self.reddit_session.http.headers['x-modhash'] = \
            self.reddit_session.modhash
        data = {'model': dumps({'name': subreddit})}
        try:
            self.reddit_session.request(url, data=data, method=method,
                                        *args, **kwargs)
        finally:
            del self.reddit_session.http.headers['x-modhash']

    def copy(self, to_name):
        """Copy this multireddit.

        Convenience function that utilizes
        :meth:`.MultiredditMixin.copy_multireddit` populating both
        the `from_redditor` and `from_name` parameters.

        """
        return self.reddit_session.copy_multireddit(self._author, self.name,
                                                    to_name)

    def delete(self):
        """Delete this multireddit.

        Convenience function that utilizes
        :meth:`.MultiredditMixin.delete_multireddit` populating the `name`
        parameter.

        """
        return self.reddit_session.delete_multireddit(self.name)

    def edit(self, *args, **kwargs):
        """Edit this multireddit.

        Convenience function that utilizes
        :meth:`.MultiredditMixin.edit_multireddit` populating the `name`
        parameter.

        """
        return self.reddit_session.edit_multireddit(name=self.name, *args,
                                                    **kwargs)

    def remove_subreddit(self, subreddit, *args, **kwargs):
        """Remove a subreddit from the user's multireddit."""
        return self.add_subreddit(subreddit, True, *args, **kwargs)

    def rename(self, new_name, *args, **kwargs):
        """Rename this multireddit.

        This function is a handy shortcut to
        :meth:`rename_multireddit` of the reddit_session.

        """
        new = self.reddit_session.rename_multireddit(self.name, new_name,
                                                     *args, **kwargs)
        self.__dict__ = new.__dict__
        return self
