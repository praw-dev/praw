"""Provide the Subreddit class."""

import logging

import six

from ...const import API_PATH
from ..listing.mixins import SubredditListingMixin
from .base import RedditBase
from .mixins import MessageableMixin


LOG = logging.getLogger(__name__)


def _modify_relationship(relationship, unlink=False):
    """Return a function for relationship modification.

    Used to support friending (user-to-user), as well as moderating,
    contributor creating, and banning (user-to-subreddit).

    """
    # The API uses friend and unfriend to manage all of these relationships.
    url_key = 'unfriend' if unlink else 'friend'

    def do_relationship(thing, user, **kwargs):
        data = {'name': six.text_type(user),
                'r': six.text_type(thing),
                'type': relationship}
        data.update(kwargs)
        session = thing.reddit_session
        url = session.config[url_key]
        return session.request_json(url, data=data)
    return do_relationship


class Subreddit(RedditBase, MessageableMixin, SubredditListingMixin):
    """A class for Subreddits."""

    _methods = (('accept_moderator_invite', 'AR'),
                ('add_flair_template', 'MFMix'),
                ('clear_flair_templates', 'MFMix'),
                ('configure_flair', 'MFMix'),
                ('delete_flair', 'MFMix'),
                ('delete_image', 'MCMix'),
                ('edit_wiki_page', 'AR'),
                ('get_banned', 'MOMix'),
                ('get_comments', 'UR'),
                ('get_contributors', 'MOMix'),
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

    # Subreddit banned
    add_ban = _modify_relationship('banned')
    remove_ban = _modify_relationship('banned', unlink=True)

    # Subreddit contributors
    add_contributor = _modify_relationship('contributor')
    remove_contributor = _modify_relationship('contributor', unlink=True)
    # Subreddit moderators
    add_moderator = _modify_relationship('moderator')
    remove_moderator = _modify_relationship('moderator', unlink=True)
    # Subreddit muted
    add_mute = _modify_relationship('muted')
    remove_mute = _modify_relationship('muted', unlink=True)

    # Subreddit wiki banned
    add_wiki_ban = _modify_relationship('wikibanned')
    remove_wiki_ban = _modify_relationship('wikibanned', unlink=True)
    # Subreddit wiki contributors
    add_wiki_contributor = _modify_relationship('wikicontributor')
    remove_wiki_contributor = _modify_relationship('wikicontributor',
                                                   unlink=True)

    def __init__(self, reddit, name=None, _data=None):
        """Initialize a Subreddit instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param name: The name of the subreddit.

        """
        if bool(name) == bool(_data):
            raise TypeError('Either `name` or `_data` can be provided.')
        super(Subreddit, self).__init__(reddit, _data)
        if name:
            self.display_name = name
        self._path = API_PATH['subreddit'].format(subreddit=self.display_name)

    def __repr__(self):
        """Return a code representation of the Subreddit."""
        return 'Subreddit(name={!r})'.format(self.display_name)

    def __unicode__(self):
        """Return a string representation of the Subreddit."""
        return self.display_name

    def _info_path(self):
        return API_PATH['subreddit_about'].format(subreddit=self.display_name)

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
