"""Provide the Subreddit class."""
from ...const import API_PATH
from ..listing.mixins import SubredditListingMixin
from .base import RedditBase
from .mixins import MessageableMixin


class Subreddit(RedditBase, MessageableMixin, SubredditListingMixin):
    """A class for Subreddits."""

    EQ_FIELD = 'display_name'

    _methods = (('accept_moderator_invite', 'AR'),
                ('add_flair_template', 'MFMix'),
                ('clear_flair_templates', 'MFMix'),
                ('configure_flair', 'MFMix'),
                ('delete_flair', 'MFMix'),
                ('delete_image', 'MCMix'),
                ('edit_wiki_page', 'AR'),
                ('get_banned', 'MOMix'),
                ('get_comments', 'UR'),
                ('get_edited', 'MOMix'),
                ('get_flair', 'UR'),
                ('get_flair_choices', 'AR'),
                ('get_flair_list', 'MFMix'),
                ('get_moderators', 'UR'),
                ('get_mod_log', 'MLMix'),
                ('get_mod_queue', 'MOMix'),
                ('get_mod_mail', 'MOMix'),
                ('get_muted', 'MOMix'),
                ('get_random_submission', 'UR'),
                ('get_reports', 'MOMix'),
                ('get_settings', 'MCMix'),
                ('get_spam', 'MOMix'),
                ('get_sticky', 'UR'),
                ('get_stylesheet', 'MOMix'),
                ('get_traffic', 'UR'),
                ('get_unmoderated', 'MOMix'),
                ('get_wiki_banned', 'MOMix'),
                ('get_wiki_contributors', 'MOMix'),
                ('get_wiki_page', 'UR'),
                ('get_wiki_pages', 'UR'),
                ('leave_contributor', 'MSMix'),
                ('leave_moderator', 'MSMix'),
                ('search', 'UR'),
                ('select_flair', 'AR'),
                ('set_flair', 'MFMix'),
                ('set_flair_csv', 'MFMix'),
                ('set_settings', 'MCMix'),
                ('set_stylesheet', 'MCMix'),
                ('submit', 'SubmitMixin'),
                ('subscribe', 'SubscribeMixin'),
                ('unsubscribe', 'SubscribeMixin'),
                ('update_settings', 'MCMix'),
                ('upload_image', 'MCMix'))

    def __init__(self, reddit, name=None, _data=None):
        """Initialize a Subreddit instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param name: The name of the subreddit.

        """
        if bool(name) == bool(_data):
            raise TypeError('Either `name` or `_data` must be provided.')
        super(Subreddit, self).__init__(reddit, _data)
        if name:
            self.display_name = name
        self._path = API_PATH['subreddit'].format(subreddit=self.display_name)
        self._prepare_relationships()

    def _info_path(self):
        return API_PATH['subreddit_about'].format(subreddit=self.display_name)

    def _prepare_relationships(self):
        for relationship in ['banned', 'contributor', 'moderator', 'muted',
                             'wikibanned', 'wikicontributor']:
            setattr(self, relationship,
                    SubredditRelationship(self, relationship))

    def clear_all_flair(self):
        """Remove all user flair on this subreddit.

        :returns: The json response from the server when there is flair to
            clear, otherwise returns None.

        """
        csv = [{'user': x['user']} for x in self.get_flair_list(limit=None)]
        if csv:
            return self.set_flair_csv(csv)
        else:
            return


class SubredditRelationship(object):
    """Represents a relationship between a redditor and subreddit."""

    def __init__(self, subreddit, relationship):
        """Create an SubredditRelationship instance.

        :param subreddit: The subreddit for the relationship.
        :param relationship: The name of the relationship.

        """
        self.relationship = relationship
        self.subreddit = subreddit
        self._unique_counter = 0

    def __iter__(self):
        """Iterate through the Redditors belonging to this relationship."""
        url = API_PATH[self.relationship].format(subreddit=str(self.subreddit))
        params = {'unique': self._unique_counter}
        self._unique_counter += 1
        for item in self.subreddit._reddit.get(url, params=params):
            yield item

    def add(self, redditor):
        """Add ``redditor`` to this relationship.

        :param redditor: A string or :class:`~.Redditor` instance.

        """
        data = {'name': str(redditor), 'r': str(self.subreddit),
                'type': self.relationship}
        return self.subreddit._reddit.post(API_PATH['friend'], data=data)

    def remove(self, redditor):
        """Remove ``redditor`` from this relationship.

        :param redditor: A string or :class:`~.Redditor` instance.

        """
        data = {'name': str(redditor), 'r': str(self.subreddit),
                'type': self.relationship}
        return self.subreddit._reddit.post(API_PATH['unfriend'], data=data)
