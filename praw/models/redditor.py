"""Provide the Redditor class."""
from json import dumps

from six import text_type

from .mixins import GildableMixin, InboxableMixin, MessageableMixin
from ..errors import ClientException
from ..internal import _get_redditor_listing


class Redditor(GildableMixin, MessageableMixin):
    """A class representing the users of reddit."""

    _methods = (('get_multireddit', 'MultiMix'),
                ('get_multireddits', 'MultiMix'))

    get_comments = _get_redditor_listing('comments')
    get_hidden = _get_redditor_listing('hidden')
    get_overview = _get_redditor_listing('')
    get_saved = _get_redditor_listing('saved')
    get_submitted = _get_redditor_listing('submitted')

    def __init__(self, reddit_session, user_name=None, json_dict=None,
                 fetch=False, **kwargs):
        """Construct an instance of the Redditor object."""
        if not user_name:
            user_name = json_dict['name']
        info_url = reddit_session.config['user_about'].format(user=user_name)
        # name is set before calling the parent constructor so that the
        # json_dict 'name' attribute (if available) has precedence
        self._case_name = user_name
        super(Redditor, self).__init__(reddit_session, json_dict,
                                       fetch, info_url, **kwargs)
        self.name = self._case_name
        self._url = reddit_session.config['user'].format(user=self.name)
        self._mod_subs = None

    def __repr__(self):
        """Return a code representation of the Redditor."""
        return 'Redditor(user_name=\'{0}\')'.format(self.name)

    def __unicode__(self):
        """Return a string representation of the Redditor."""
        return self.name

    def _post_populate(self, fetch):
        if fetch:
            tmp = self._case_name
            self._case_name = self.name
            self.name = tmp

    def friend(self, note=None, _unfriend=False):
        """Friend the user.

        :param note: A personal note about the user. Requires reddit Gold.
        :param _unfriend: Unfriend the user. Please use :meth:`unfriend`
            instead of setting this parameter manually.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['friend_v1'].format(user=self.name)
        # This endpoint wants the data to be a string instead of an actual
        # dictionary, although it is not required to have any content for adds.
        # Unfriending does require the 'id' key.
        if _unfriend:
            data = {'id': self.name}
        else:
            # We cannot send a null or empty note string.
            data = {'note': note} if note else {}
        method = 'DELETE' if _unfriend else 'PUT'
        return self.reddit_session.request_json(url, data=dumps(data),
                                                method=method)

    def get_blocked(self):
        """Return a UserList of Redditors with whom the user has blocked."""
        url = self.reddit_session.config['blocked']
        return self.reddit_session.request_json(url)

    def get_cached_moderated_reddits(self):
        """Return a cached dictionary of the user's moderated reddits.

        This list is used internally. Consider using the `get_my_moderation`
        function instead.

        """
        if self._mod_subs is None:
            self._mod_subs = {'mod': self.reddit_session.get_subreddit('mod')}
            for sub in self.reddit_session.get_my_moderation(limit=None):
                self._mod_subs[text_type(sub).lower()] = sub
        return self._mod_subs

    def get_disliked(self, *args, **kwargs):
        """Return a listing of the Submissions the user has downvoted.

        This method points to :meth:`get_downvoted`, as the "disliked" name
        is being phased out.
        """
        return self.get_downvoted(*args, **kwargs)

    def get_downvoted(self, *args, **kwargs):
        """Return a listing of the Submissions the user has downvoted.

        :returns: get_content generator of Submission items.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        As a default, this listing is only accessible by the user. Thereby
        requiring either user/pswd authentication or OAuth authentication with
        the 'history' scope. Users may choose to make their voting record
        public by changing a user preference. In this case, no authentication
        will be needed to access this listing.

        """
        return _get_redditor_listing('downvoted')(self, *args, **kwargs)

    def get_friend_info(self):
        """Return information about this friend, including personal notes.

        The personal note can be added or overwritten with :meth:friend, but
            only if the user has reddit Gold.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['friend_v1'].format(user=self.name)
        data = {'id': self.name}
        return self.reddit_session.request_json(url, data=data, method='GET')

    def get_liked(self, *args, **kwargs):
        """Return a listing of the Submissions the user has upvoted.

        This method points to :meth:`get_upvoted`, as the "liked" name
        is being phased out.
        """
        return self.get_upvoted(*args, **kwargs)

    def get_upvoted(self, *args, **kwargs):
        """Return a listing of the Submissions the user has upvoted.

        :returns: get_content generator of Submission items.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        As a default, this listing is only accessible by the user. Thereby
        requirering either user/pswd authentication or OAuth authentication
        with the 'history' scope. Users may choose to make their voting record
        public by changing a user preference. In this case, no authentication
        will be needed to access this listing.

        """
        return _get_redditor_listing('upvoted')(self, *args, **kwargs)

    def mark_as_read(self, messages, unread=False):
        """Mark message(s) as read or unread.

        :returns: The json response from the server.

        """
        ids = []
        if isinstance(messages, InboxableMixin):
            ids.append(messages.fullname)
        elif hasattr(messages, '__iter__'):
            for message in messages:
                if not isinstance(message, InboxableMixin):
                    raise ClientException('Invalid message type: {0}'
                                          .format(type(message)))
                ids.append(message.fullname)
        else:
            raise ClientException('Invalid message type: {0}'
                                  .format(type(messages)))
        retval = self.reddit_session._mark_as_read(ids, unread=unread)
        return retval

    def unfriend(self):
        """Unfriend the user.

        :returns: The json response from the server.

        """
        return self.friend(_unfriend=True)
