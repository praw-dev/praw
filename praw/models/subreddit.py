"""Provide the Subreddit class."""

import logging

from .mixins import Messageable
from ..internal import _get_sorter, _modify_relationship


log = logging.getLogger(__name__)


class Subreddit(Messageable):
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
    add_ban = _modify_relationship('banned', is_sub=True)
    remove_ban = _modify_relationship('banned', unlink=True, is_sub=True)

    # Subreddit contributors
    add_contributor = _modify_relationship('contributor', is_sub=True)
    remove_contributor = _modify_relationship('contributor', unlink=True,
                                              is_sub=True)
    # Subreddit moderators
    add_moderator = _modify_relationship('moderator', is_sub=True)
    remove_moderator = _modify_relationship('moderator', unlink=True,
                                            is_sub=True)
    # Subreddit muted
    add_mute = _modify_relationship('muted', is_sub=True)
    remove_mute = _modify_relationship('muted', is_sub=True, unlink=True)

    # Subreddit wiki banned
    add_wiki_ban = _modify_relationship('wikibanned', is_sub=True)
    remove_wiki_ban = _modify_relationship('wikibanned', unlink=True,
                                           is_sub=True)
    # Subreddit wiki contributors
    add_wiki_contributor = _modify_relationship('wikicontributor', is_sub=True)
    remove_wiki_contributor = _modify_relationship('wikicontributor',
                                                   unlink=True, is_sub=True)

    # Generic listing selectors
    get_controversial = _get_sorter('controversial')
    get_hot = _get_sorter('')
    get_new = _get_sorter('new')
    get_top = _get_sorter('top')

    # Explicit listing selectors
    get_controversial_from_all = _get_sorter('controversial', t='all')
    get_controversial_from_day = _get_sorter('controversial', t='day')
    get_controversial_from_hour = _get_sorter('controversial', t='hour')
    get_controversial_from_month = _get_sorter('controversial', t='month')
    get_controversial_from_week = _get_sorter('controversial', t='week')
    get_controversial_from_year = _get_sorter('controversial', t='year')
    get_rising = _get_sorter('rising')
    get_top_from_all = _get_sorter('top', t='all')
    get_top_from_day = _get_sorter('top', t='day')
    get_top_from_hour = _get_sorter('top', t='hour')
    get_top_from_month = _get_sorter('top', t='month')
    get_top_from_week = _get_sorter('top', t='week')
    get_top_from_year = _get_sorter('top', t='year')

    def __init__(self, reddit_session, subreddit_name=None, json_dict=None,
                 fetch=False, **kwargs):
        """Construct an instance of the Subreddit object."""
        # Special case for when my_subreddits is called as no name is returned
        # so we have to extract the name from the URL. The URLs are returned
        # as: /r/reddit_name/
        if not subreddit_name:
            subreddit_name = json_dict['url'].split('/')[2]

        if fetch and ('+' in subreddit_name or '-' in subreddit_name):
            fetch = False
            log.warn('fetch=True has no effect on multireddits')

        info_url = reddit_session.config['subreddit_about'].format(
            subreddit=subreddit_name)
        self._case_name = subreddit_name
        super(Subreddit, self).__init__(reddit_session, json_dict, fetch,
                                        info_url, **kwargs)
        self.display_name = self._case_name
        self._url = reddit_session.config['subreddit'].format(
            subreddit=self.display_name)
        # '' is the hot listing
        listings = ['new/', '', 'top/', 'controversial/', 'rising/']
        base = reddit_session.config['subreddit'].format(
            subreddit=self.display_name)
        self._listing_urls = [base + x + '.json' for x in listings]

    def __repr__(self):
        """Return a code representation of the Subreddit."""
        return 'Subreddit(subreddit_name=\'{0}\')'.format(self.display_name)

    def __unicode__(self):
        """Return a string representation of the Subreddit."""
        return self.display_name

    def _post_populate(self, fetch):
        if fetch:
            tmp = self._case_name
            self._case_name = self.display_name
            self.display_name = tmp

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
