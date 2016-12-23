"""Provide the Subreddit class."""
from copy import deepcopy
from json import dumps
import time

from prawcore import Redirect
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from ...const import API_PATH
from ..util import stream_generator
from ..listing.generator import ListingGenerator
from ..listing.mixins import SubredditListingMixin
from .base import RedditBase
from .mixins import MessageableMixin
from .wikipage import WikiPage


class Subreddit(RedditBase, MessageableMixin, SubredditListingMixin):
    """A class for Subreddits.

    To obtain an instance of this class for subreddit ``/r/redditdev`` execute:

    .. code:: python

       subreddit = reddit.subreddit('redditdev')

    While ``/r/all`` is not a real subreddit, it can still be treated like
    one. The following outputs the titles of the 25 hottest submissions in
    ``/r/all``:

    .. code:: python

       for submission in reddit.subreddit('all').hot(limit=25):
           print(submission.title)

    Multiple subreddits can be combined like so:

    .. code:: python

       for submission in reddit.subreddit('redditdev+learnpython').top('all'):
           print(submission)

    Subreddits can be filtered from combined listings as follows:

    .. code:: python

       for submission in reddit.subreddit('all-redditdev').new():
           print(submission)

    """

    STR_FIELD = 'display_name'
    MESSAGE_PREFIX = '#'

    @staticmethod
    def _create_or_update(_reddit, allow_images=None, allow_top=None,
                          collapse_deleted_comments=None,
                          comment_score_hide_mins=None, description=None,
                          domain=None, exclude_banned_modqueue=None,
                          header_hover_text=None, hide_ads=None, lang=None,
                          key_color=None, link_type=None, name=None,
                          over_18=None, public_description=None,
                          public_traffic=None, show_media=None,
                          show_media_preview=None, spam_comments=None,
                          spam_links=None, spam_selfposts=None, sr=None,
                          submit_link_label=None, submit_text=None,
                          submit_text_label=None, subreddit_type=None,
                          suggested_comment_sort=None, title=None,
                          wiki_edit_age=None, wiki_edit_karma=None,
                          wikimode=None, **other_settings):
        # pylint: disable=invalid-name,too-many-locals
        model = {'allow_images': allow_images,
                 'allow_top': allow_top,
                 'collapse_deleted_comments': collapse_deleted_comments,
                 'comment_score_hide_mins': comment_score_hide_mins,
                 'description': description,
                 'domain': domain,
                 'exclude_banned_modqueue': exclude_banned_modqueue,
                 'header-title': header_hover_text,  # Remap here - better name
                 'hide_ads': hide_ads,
                 'key_color': key_color,
                 'lang': lang,
                 'link_type': link_type,
                 'name': name,
                 'over_18': over_18,
                 'public_description': public_description,
                 'public_traffic': public_traffic,
                 'show_media': show_media,
                 'show_media_preview': show_media_preview,
                 'spam_comments': spam_comments,
                 'spam_links': spam_links,
                 'spam_selfposts': spam_selfposts,
                 'sr': sr,
                 'submit_link_label': submit_link_label,
                 'submit_text': submit_text,
                 'submit_text_label': submit_text_label,
                 'suggested_comment_sort': suggested_comment_sort,
                 'title': title,
                 'type': subreddit_type,
                 'wiki_edit_age': wiki_edit_age,
                 'wiki_edit_karma': wiki_edit_karma,
                 'wikimode': wikimode}

        model.update(other_settings)

        _reddit.post(API_PATH['site_admin'], data=model)

    @staticmethod
    def _subreddit_list(subreddit, other_subreddits):
        if other_subreddits:
            return ','.join([str(subreddit)] +
                            [str(x) for x in other_subreddits])
        return str(subreddit)

    @property
    def banned(self):
        """An instance of :class:`.SubredditRelationship`.

        For example to ban a user try:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').banned.add('NAME', reason='a reason')

        """
        if self._banned is None:
            self._banned = SubredditRelationship(self, 'banned')
        return self._banned

    @property
    def contributor(self):
        """An instance of :class:`.ContributorRelationship`."""
        if self._contributor is None:
            self._contributor = ContributorRelationship(self, 'contributor')
        return self._contributor

    @property
    def filters(self):
        """An instance of :class:`.SubredditFilters`."""
        if self._filters is None:
            self._filters = SubredditFilters(self)
        return self._filters

    @property
    def flair(self):
        """An instance of :class:`.SubredditFlair`.

        Provides the interface for interacting with a subreddit's flair. For
        example to list all the flair for a subreddit which you have the
        ``flair`` moderator permission on try:

        .. code-block:: python

           for flair in reddit.subreddit('NAME').flair():
               print(flair)

        """
        if self._flair is None:
            self._flair = SubredditFlair(self)
        return self._flair

    @property
    def mod(self):
        """An instance of :class:`.SubredditModeration`."""
        if self._mod is None:
            self._mod = SubredditModeration(self)
        return self._mod

    @property
    def moderator(self):
        """An instance of :class:`.ModeratorRelationship`."""
        if self._moderator is None:
            self._moderator = ModeratorRelationship(self, 'moderator')
        return self._moderator

    @property
    def muted(self):
        """An instance of :class:`.SubredditRelationship`."""
        if self._muted is None:
            self._muted = SubredditRelationship(self, 'muted')
        return self._muted

    @property
    def quaran(self):
        """An instance of :class:`.SubredditQuarantine`.

        This property is named ``quaran`` because ``quarantine`` is an
        Subreddit attribute returned by Reddit to indicate whether or not a
        Subreddit is quarantined.

        """
        if self._quarantine is None:
            self._quarantine = SubredditQuarantine(self)
        return self._quarantine

    @property
    def stream(self):
        """An instance of :class:`.SubredditStream`."""
        if self._stream is None:
            self._stream = SubredditStream(self)
        return self._stream

    @property
    def stylesheet(self):
        """An instance of :class:`.SubredditStylesheet`."""
        if self._stylesheet is None:
            self._stylesheet = SubredditStylesheet(self)
        return self._stylesheet

    @property
    def wiki(self):
        """An instance of :class:`.SubredditWiki`."""
        if self._wiki is None:
            self._wiki = SubredditWiki(self)
        return self._wiki

    def __init__(self, reddit, display_name=None, _data=None):
        """Initialize a Subreddit instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param display_name: The name of the subreddit.

        .. note:: This class should not be initialized directly instead obtain
           an instance via: ``reddit.subreddit('subreddit_name')``

        """
        if bool(display_name) == bool(_data):
            raise TypeError(
                'Either `display_name` or `_data` must be provided.')
        super(Subreddit, self).__init__(reddit, _data)
        if display_name:
            self.display_name = display_name
        self._banned = self._contributor = self._filters = self._flair = None
        self._mod = self._moderator = self._muted = self._quarantine = None
        self._stream = self._stylesheet = self._wiki = None
        self._path = API_PATH['subreddit'].format(subreddit=self)

    def _info_path(self):
        return API_PATH['subreddit_about'].format(subreddit=self)

    def random(self):
        """Return a random Submission."""
        url = API_PATH['subreddit_random'].format(subreddit=self)
        try:
            self._reddit.get(url, params={'unique': self._reddit._next_unique})
        except Redirect as redirect:
            path = redirect.path
        return self._submission_class(self._reddit, url=urljoin(
            self._reddit.config.reddit_url, path))

    def search(self, query, sort='relevance', syntax='cloudsearch',
               time_filter='all', **generator_kwargs):
        """Return a ListingGenerator for items that match ``query``.

        :param query: The query string to search for.
        :param sort: Can be one of: relevance, hot, top, new,
            comments. (default: relevance).
        :param syntax: Can be one of: cloudsearch, lucene, plain
            (default: cloudsearch).
        :param time_filter: Can be one of: all, day, hour, month, week, year
            (default: all).

        For more information on building a search query see:
            https://www.reddit.com/wiki/search

        For example to search all subreddits for ``praw`` try:

        .. code:: python

           for submission in reddit.subreddit('all').search('praw'):
               print(submission.title)

        """
        self.validate_time_filter(time_filter)
        not_all = self.display_name.lower() != 'all'
        self._safely_add_arguments(generator_kwargs, 'params', q=query,
                                   restrict_sr=not_all, sort=sort,
                                   syntax=syntax, t=time_filter)
        url = API_PATH['search'].format(subreddit=self)
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def sticky(self, number=1):
        """Return a Submission object for a sticky of the subreddit.

        :param number: Specify which sticky to return. 1 appears at the top
            (Default: 1).

        Raises ``prawcore.NotFound`` if the sticky does not exist.

        """
        url = API_PATH['about_sticky'].format(subreddit=self)
        try:
            self._reddit.get(url, params={'num': number})
        except Redirect as redirect:
            path = redirect.path
        return self._submission_class(self._reddit, url=urljoin(
            self._reddit.config.reddit_url, path))

    def submissions(self, start=None, end=None, extra_query=None):
        """Yield submissions created between timestamps ``start`` and ``end``.

        :param start: A UNIX timestamp indicating the earliest creation time of
            submission yielded during the call. A value of ``None`` will
            consider all submissions older than ``end`` (Default: None).
        :param end: A UNIX timestamp indicating the latest creation time of a
            submission yielded during the call. A value of ``None`` will
            consider all submissions newer than ``start`` (Default: None).
        :param extra_query: A cloudsearch query that will be combined via
            ``(and timestamp:start..end EXTRA_QUERY)`` to futher filter
            results (Default: None).

        Submissions are yielded newest first.

        **Example**: If you want to obtain all submissions to ``/r/politics``
        on November 8, 2016 PST. First you need to determine the start and end
        dates as UNIX timestamps. Using http://www.epochconverter.com/ those
        timestamps are 1478592000, and 1478678400 respectively. The following
        outputs all such submissions' titles.

        .. code:: python

           subreddit = reddit.subreddit('politics')
           for submission in subreddit.submissions(1478592000, 1478678400):
               print(submission.title)

        As of this writing there are 809 results.

        """
        utc_offset = 28800
        now = int(time.time())
        start = max(int(start) + utc_offset if start else 0, 0)
        end = min(int(end) if end else now, now) + utc_offset

        found_new_submission = True
        last_ids = set()
        params = {}
        while found_new_submission:
            query = 'timestamp:{}..{}'.format(start, end)
            if extra_query:
                query = '(and {} {})'.format(query, extra_query)

            current_ids = set()
            found_new_submission = False
            for submission in self.search(query, limit=None, params=params,
                                          sort='new'):
                current_ids.add(submission.id)
                end = min(end, int(submission.created))
                if submission.id not in last_ids:
                    found_new_submission = True
                yield submission
                params['after'] = submission.fullname
            last_ids = current_ids

    def submit(self, title, selftext=None, url=None, resubmit=True,
               send_replies=True):
        """Add a submission to the subreddit.

        :param title: The title of the submission.
        :param selftext: The markdown formatted content for a ``text``
            submission.
        :param url: The URL for a ``link`` submission.
        :param resubmit: When False, an error will occur if the URL has already
            been submitted (Default: True).
        :param send_replies: When True, messages will be sent to the submission
            author when comments are made to the submission (Default: True).
        :returns: A :class:`~.Submission` object for the newly created
            submission.

        Either ``selftext`` or ``url`` can be provided, but not both.

        For example to submit a URL to ``/r/reddit_api_test`` do:

        .. code:: python

           url = 'https://praw.readthedocs.io'
           reddit.subreddit('reddit_api_test').submit(url=url)

        """
        if bool(selftext) == bool(url):
            raise TypeError('Either `selftext` or `url` must be provided.')

        data = {'sr': str(self), 'resubmit': bool(resubmit),
                'sendreplies': bool(send_replies), 'title': title}
        if selftext is not None:
            data.update(kind='self', text=selftext)
        else:
            data.update(kind='link', url=url)
        return self._reddit.post(API_PATH['submit'], data=data)

    def subscribe(self, other_subreddits=None):
        """Subscribe to the subreddit.

        :param other_subreddits: When provided, also subscribe to the provided
            list of subreddits.

        """
        data = {'action': 'sub', 'skip_inital_defaults': True,
                'sr_name': self._subreddit_list(self, other_subreddits)}
        self._reddit.post(API_PATH['subscribe'], data=data)

    def traffic(self):
        """Return a dictionary of the subreddit's traffic statistics.

        Raises ``prawcore.NotFound`` when the traffic stats aren't available to
        the authenticated user, that is, they are not public and the
        authenticated user is not a moderator of the subreddit.

        """
        return self._reddit.get(API_PATH['about_traffic']
                                .format(subreddit=self))

    def unsubscribe(self, other_subreddits=None):
        """Unsubscribe from the subreddit.

        :param other_subreddits: When provided, also unsubscribe to the
            provided list of subreddits.

        """
        data = {'action': 'unsub',
                'sr_name': self._subreddit_list(self, other_subreddits)}
        self._reddit.post(API_PATH['subscribe'], data=data)


class SubredditFilters(object):
    """Provide functions to interact with the special Subreddit's filters.

    Members of this class should be utilized via ``Subreddit.fiters``. For
    example to add a filter run:

    .. code:: python

       reddit.subreddit('all').filters.add('subreddit_name')

    """

    def __init__(self, subreddit):
        """Create a SubredditFilters instance.

        :param subreddit: The special subreddit whose filters to work with.

        As of this writing filters can only be used with the special subreddits
        ``all`` and ``mod``.

        """
        self.subreddit = subreddit

    def __iter__(self):
        """Iterate through the special subreddit's filters.

        This method should be invoked as:

        .. code:: python

           for subreddit in reddit.subreddit('NAME').filters:
               ...

        """
        url = API_PATH['subreddit_filter_list'].format(
            special=self.subreddit, user=self.subreddit._reddit.user.me())
        params = {'unique': self.subreddit._reddit._next_unique}
        response_data = self.subreddit._reddit.get(url, params=params)
        for subreddit in response_data.subreddits:
            yield subreddit

    def add(self, subreddit):
        """Add ``subreddit`` to the list of filtered subreddits.

        :param subreddit: The subreddit to add to the filter list.

        Items from subreddits added to the filtered list will no longer be
        included when obtaining listings for ``/r/all``.

        Alternatively, you can filter a subreddit temporarily from a special
        listing in a manner like so:

        .. code:: python

           reddit.subreddit('all-redditdev-learnpython')

        Raises ``prawcore.NotFound`` when calling on a non-special subreddit.

        """
        url = API_PATH['subreddit_filter'].format(
            special=self.subreddit, user=self.subreddit._reddit.user.me(),
            subreddit=subreddit)
        self.subreddit._reddit.request(
            'PUT', url, data={'model': dumps({'name': subreddit})})

    def remove(self, subreddit):
        """Remove ``subreddit`` from the list of filtered subreddits.

        :param subreddit: The subreddit to remove from the filter list.

        Raises ``prawcore.NotFound`` when calling on a non-special subreddit.

        """
        url = API_PATH['subreddit_filter'].format(
            special=self.subreddit, user=self.subreddit._reddit.user.me(),
            subreddit=subreddit)
        self.subreddit._reddit.request('DELETE', url, data={})


class SubredditFlair(object):
    """Provide a set of functions to interact with a Subreddit's flair."""

    def __call__(self, redditor=None, **generator_kwargs):
        """Return a generator for Redditors and their associated flair.

        :param redditor: Yield at most a single :class:`~.Redditor`
            instance.

        This method is intended to be used like:

        .. code-block:: python

           for flair in reddit.subreddit('NAME').flair(limit=None):
               print(flair)

        """
        Subreddit._safely_add_arguments(generator_kwargs, 'params',
                                        name=redditor)
        url = API_PATH['flairlist'].format(subreddit=self.subreddit)
        return ListingGenerator(self.subreddit._reddit, url,
                                **generator_kwargs)

    def __init__(self, subreddit):
        """Create a SubredditFlair instance.

        :param subreddit: The subreddit whose flair to work with.

        """
        self.subreddit = subreddit
        self.templates = SubredditFlairTemplates(subreddit)

    def __iter__(self):
        """Iterate through the Redditors and their associated flair.

        .. warning:: (Deprecated) This method will be removed in PRAW 5. Prefer
                     iterating over ``subreddit.flair`` instead of
                     ``subreddit.flair``.

        """
        url = API_PATH['flairlist'].format(subreddit=self.subreddit)
        params = {'unique': self.subreddit._reddit._next_unique}
        for item in ListingGenerator(self.subreddit._reddit, url, None,
                                     params=params):
            yield item

    def configure(self, position='right', self_assign=False,
                  link_position='left', link_self_assign=False,
                  **settings):
        """Update the subreddit's flair configuration.

        :param position: One of left, right, or False to disable (default:
            right).
        :param self_assign: (boolean) Permit self assignment of user flair
            (default: False).
        :param link_position: One of left, right, or False to disable
            (default: left).
        :param link_self_assign: (boolean) Permit self assignment
               of link flair (default: False).

        Additional keyword arguments can be provided to handle new settings as
        Reddit introduces them.

        """
        data = {'flair_enabled': bool(position),
                'flair_position': position or 'right',
                'flair_self_assign_enabled': self_assign,
                'link_flair_position': link_position or '',
                'link_flair_self_assign_enabled': link_self_assign}
        data.update(settings)
        url = API_PATH['flairconfig'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def delete(self, redditor):
        """Delete flair for a Redditor.

        :param redditor: An instance of :class:`.Redditor`, or the name of a
            Redditor.

        .. note:: To delete the flair of many Redditors at once, please see
                  :meth:`~praw.models.reddit.subreddit.SubredditFlair.update`.

        """
        url = API_PATH['deleteflair'].format(subreddit=self.subreddit)
        return self.subreddit._reddit.post(url, data={'name': str(redditor)})

    def delete_all(self):
        """Delete all Redditor flair in the Subreddit.

        :returns: List of dictionaries indicating the success or failure of
            each delete.

        """
        return self.update(x['user'] for x in self)

    def set(self, redditor=None, text='', css_class='', thing=None):
        """Set flair for a Redditor.

        :param redditor: (Required) An instance of Redditor or a string that is
            the name of a Redditor.
        :param text: The flair text to associate with the Redditor or
            Submission (Default: '').
        :param css_class: The css class to associate with the flair html
            (Default: '').

        This method can only be used by an authenticated user who is a
        moderator of the associated Subreddit.

        .. warning:: The use of this method to set the flair of a
                     :class:`.Submission` is deprecated and will be removed in
                     PRAW 5. Use :meth:`.flair` instead.

        .. warning:: The use of the keyword argument ``thing`` is deprecated
                     and will be removed in PRAW 5. Use ``redditor`` instead.

        Example:

        .. code:: python

           reddit.subreddit('redditdev').flair.set('bboe', 'PRAW author')

        """
        # PRAW5 REMOVE
        if bool(redditor) == bool(thing):
            raise TypeError('`redditor` must be provided.')
        if redditor is None:
            redditor = thing

        data = {'css_class': css_class, 'text': text}
        if redditor.__class__.__name__ == 'Submission':  # PRAW5 REMOVE
            data['link'] = redditor.fullname
        else:
            data['name'] = str(redditor)
        url = API_PATH['flair'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def update(self, flair_list, text='', css_class=''):
        """Set or clear the flair for many Redditors at once.

        :param redditor_flair_list: Each item in this list should be either: a
            Redditor name string, a Redditor, or a dictionary containing the
            keys ``user``, ``flair_text``, and ``flair_css_class``. The
            ``user`` key should map to a Redditor name string, or a
            Redditor. When a dictionary isn't provided, or the dictionary is
            missing one of ``flair_text``, or ``flair_css_class`` attributes
            the default values will come from the the following arguments.
        :param text: The flair text to use when not explicitly provided in
            ``flair_list`` (Default: '').
        :param css_class: The css class to use when not explicitly provided in
            ``flair_list`` (Default: '').
        :returns: List of dictionaries indicating the success or failure of
            each update.

        """
        lines = []
        for item in flair_list:
            if isinstance(item, dict):
                fmt_data = (str(item['user']), item.get('flair_text', text),
                            item.get('flair_css_class', css_class))
            else:
                fmt_data = (str(item), text, css_class)
            lines.append('"{}","{}","{}"'.format(*fmt_data))

        response = []
        url = API_PATH['flaircsv'].format(subreddit=self.subreddit)
        while len(lines):
            data = {'flair_csv': '\n'.join(lines[:100])}
            response.extend(self.subreddit._reddit.post(url, data=data))
            lines = lines[100:]
        return response


class SubredditFlairTemplates(object):
    """Provide functions to interact with a Subreddit's flair templates."""

    @staticmethod
    def flair_type(is_link):
        """Return LINK_FLAIR or USER_FLAIR depending on ``is_link`` value."""
        return 'LINK_FLAIR' if is_link else 'USER_FLAIR'

    def __init__(self, subreddit):
        """Create a SubredditFlairTemplate instance.

        :param subreddit: The subreddit whose flair templates to work with.

        """
        self.subreddit = subreddit

    def __iter__(self):
        """Iterate through the user flair templates."""
        url = API_PATH['flairselector'].format(subreddit=self.subreddit)
        data = {'unique': self.subreddit._reddit._next_unique}
        for template in self.subreddit._reddit.post(url, data=data)['choices']:
            yield template

    def add(self, text, css_class='', text_editable=False, is_link=False):
        """Add a flair template to the associated subreddit.

        :param text: The flair template's text (required).
        :param css_class: The flair template's css_class (default: '').
        :param text_editable: (boolean) Indicate if the flair text can be
            modified for each Redditor that sets it (default: False).
        :param is_link: (boolean) When True, add a link flair template rather
            than a Redditor flair template (default: False).

        """
        url = API_PATH['flairtemplate'].format(subreddit=self.subreddit)
        data = {'css_class': css_class, 'flair_type': self.flair_type(is_link),
                'text': text, 'text_editable': bool(text_editable)}
        self.subreddit._reddit.post(url, data=data)

    def clear(self, is_link=False):
        """Remove all flair templates from the subreddit.

        :param is_link: (boolean) When True, clear all link flair templates
            rather than a Redditor flair templates (default: False).

        """
        url = API_PATH['flairtemplateclear'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(
            url, data={'flair_type': self.flair_type(is_link)})

    def delete(self, template_id):
        """Remove a flair template provided by ``template_id``."""
        url = API_PATH['flairtemplatedelete'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(
            url, data={'flair_template_id': template_id})

    def update(self, template_id, text, css_class='', text_editable=False):
        """Update the flair templated provided by ``template_id``.

        :param template_id: The flair template to update.
        :param text: The flair template's new text (required).
        :param css_class: The flair template's new css_class (default: '').
        :param text_editable: (boolean) Indicate if the flair text can be
            modified for each Redditor that sets it (default: False).

        """
        url = API_PATH['flairtemplate'].format(subreddit=self.subreddit)
        data = {'css_class': css_class, 'flair_template_id': template_id,
                'text': text, 'text_editable': bool(text_editable)}
        self.subreddit._reddit.post(url, data=data)


class SubredditModeration(object):
    """Provides a set of moderation functions to a Subreddit."""

    @staticmethod
    def _handle_only(only, generator_kwargs):
        if only is not None:
            if only == 'submissions':
                only = 'links'
            RedditBase._safely_add_arguments(
                generator_kwargs, 'params', only=only)

    def __init__(self, subreddit):
        """Create a SubredditModeration instance.

        :param subreddit: The subreddit to moderate.

        """
        self.subreddit = subreddit

    def accept_invite(self):
        """Accept an invitation as a moderator of the community."""
        url = API_PATH['accept_mod_invite'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    @staticmethod
    def approve(thing):
        """DEPRECATED.

        .. warning:: (Deprecated) This method will be removed in PRAW 5. Prefer
                     calling ``comment.mod.approve()``,
                     ``submission.mod.approve()``.

        """
        thing.mod.approve()

    @staticmethod
    def distinguish(thing, how='yes', sticky=False):
        """DEPRECATED.

        .. warning:: (Deprecated) This method will be removed in PRAW 5. Prefer
                     calling ``comment.mod.distinguish()``,
                     ``submission.mod.distinguish()``.

        """
        thing.mod.distinguish(how=how, sticky=sticky)

    def edited(self, only=None, **generator_kwargs):
        """Return a ListingGenerator for edited comments and submissions.

        :param only: If specified, one of `comments`, or 'submissions' to yield
            only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit, API_PATH['about_edited'].format(
                subreddit=self.subreddit), **generator_kwargs)

    @staticmethod
    def ignore_reports(thing):
        """DEPRECATED.

        .. warning:: (Deprecated) This method will be removed in PRAW 5. Prefer
                     calling ``comment.mod.ignore_reports()``,
                     ``submission.mod.ignore_reports()``.

        """
        thing.mod.ignore_reports()

    def inbox(self, **generator_kwargs):
        """Return a ListingGenerator for moderator messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        See ``unread`` for unread moderator messages.

        """
        return ListingGenerator(
            self.subreddit._reddit, API_PATH['moderator_messages'].format(
                subreddit=self.subreddit), **generator_kwargs)

    def log(self, action=None, mod=None, **generator_kwargs):
        """Return a ListingGenerator for moderator log entries.

        :param action: If given, only return log entries for the specified
            action.
        :param mod: If given, only return log entries for actions made by the
            passed in Redditor.

        """
        params = {'mod': str(mod) if mod else mod, 'type': action}
        Subreddit._safely_add_arguments(generator_kwargs, 'params',
                                        **params)
        return ListingGenerator(
            self.subreddit._reddit, API_PATH['about_log'].format(
                subreddit=self.subreddit), **generator_kwargs)

    def modqueue(self, only=None, **generator_kwargs):
        """Return a ListingGenerator for comments/submissions in the modqueue.

        :param only: If specified, one of `comments`, or 'submissions' to yield
            only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit, API_PATH['about_modqueue'].format(
                subreddit=self.subreddit), **generator_kwargs)

    @staticmethod
    def remove(thing, spam=False):
        """DEPRECATED.

        .. warning:: (Deprecated) This method will be removed in PRAW 5. Prefer
                     calling ``comment.mod.remove()``,
                     ``submission.mod.remove()``.

        """
        thing.mod.remove(spam=spam)

    def reports(self, only=None, **generator_kwargs):
        """Return a ListingGenerator for reported comments and submissions.

        :param only: If specified, one of `comments`, or 'submissions' to yield
            only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit, API_PATH['about_reports'].format(
                subreddit=self.subreddit), **generator_kwargs)

    def settings(self):
        """Return a dictionary of the subreddit's current settings."""
        url = API_PATH['subreddit_settings'].format(subreddit=self.subreddit)
        return self.subreddit._reddit.get(url)['data']

    def spam(self, only=None, **generator_kwargs):
        """Return a ListingGenerator for spam comments and submissions.

        :param only: If specified, one of `comments`, or 'submissions' to yield
            only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit, API_PATH['about_spam'].format(
                subreddit=self.subreddit), **generator_kwargs)

    @staticmethod
    def undistinguish(thing):
        """DEPRECATED.

        .. warning:: (Deprecated) This method will be removed in PRAW 5. Prefer
                     calling ``comment.mod.undistinguish()``,
                     ``submission.mod.undistinguish()``.

        """
        thing.mod.undistinguish()

    @staticmethod
    def unignore_reports(thing):
        """DEPRECATED.

        .. warning:: (Deprecated) This method will be removed in PRAW 5. Prefer
                     calling ``comment.mod.unignore_reports()``,
                     ``submission.mod.unignore_reports()``.

        """
        thing.mod.unignore_reports()

    def unmoderated(self, **generator_kwargs):
        """Return a ListingGenerator for unmoderated submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self.subreddit._reddit, API_PATH['about_unmoderated'].format(
                subreddit=self.subreddit), **generator_kwargs)

    def unread(self, **generator_kwargs):
        """Return a ListingGenerator for unread moderator messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        See ``inbox`` for all messages.

        """
        return ListingGenerator(
            self.subreddit._reddit, API_PATH['moderator_unread'].format(
                subreddit=self.subreddit), **generator_kwargs)

    def update(self, **settings):
        """Update the subreddit's settings.

        :param allow_images: Allow users to upload images using the native
            image hosting. Only applies to link-only subreddits.
        :param allow_top: Allow the subreddit to appear on ``/r/all`` as well
            as the default and trending lists.
        :param collapse_deleted_comments: Collapse deleted and removed comments
            on comments pages by default.
        :param comment_score_hide_mins: The number of minutes to hide comment
            scores.
        :param description: Shown in the sidebar of your subreddit.
        :param domain: Domain name with a cname that points to
            {subreddit}.reddit.com.
        :param exclude_banned_modqueue: Exclude posts by site-wide banned users
            from modqueue/unmoderated.
        :param header_hover_text: The text seen when hovering over the snoo.
        :param hide_ads: Don't show ads within this subreddit. Only applies to
            gold-user only subreddits.
        :param key_color: A 6-digit rgb hex color (e.g. `#AABBCC`), used as a
            thematic color for your subreddit on mobile.
        :param lang: A valid IETF language tag (underscore separated).
        :param link_type: The types of submissions users can make.
            One of ``any``, ``link``, ``self``.
        :param over_18: Viewers must be over 18 years old (i.e. NSFW).
        :param public_description: Public description blurb. Appears in search
            results and on the landing page for private subreddits.
        :param public_traffic: Make the traffic stats page public.
        :param show_media: Show thumbnails on submissions.
        :param show_media_preview: Expand media previews on comments pages.
        :param spam_comments: Spam filter strength for comments.
            One of ``all``, ``low``, ``high``.
        :param spam_links: Spam filter strength for links.
            One of ``all``, ``low``, ``high``.
        :param spam_selfposts: Spam filter strength for selfposts.
            One of ``all``, ``low``, ``high``.
        :param sr: The fullname of the subreddit whose settings will be
            updated.
        :param submit_link_label: Custom label for submit link button
            (None for default).
        :param submit_text: Text to show on submission page.
        :param submit_text_label: Custom label for submit text post button
            (None for default).
        :param subreddit_type: One of ``archived``, ``employees_only``,
            ``gold_only``, ``gold_restricted``, ``private``, ``public``,
            ``restricted``.
        :param suggested_comment_sort: All comment threads will use this
            sorting method by default. Leave None, or choose one of
            ``confidence``, ``controversial``, ``new``, ``old``, ``qa``,
            ``random``, ``top``.
        :param title: The title of the subreddit.
        :param wiki_edit_age: Account age, in days, required to edit and create
            wiki pages.
        :param wiki_edit_karma: Subreddit karma required to edit and create
            wiki pages.
        :param wikimode: One of  ``anyone``, ``disabled``, ``modonly``.

        Additional keyword arguments can be provided to handle new settings as
        Reddit introduces them.

        Unspecified settings will maintain their current value.

        """
        current_settings = self.settings()
        fullname = current_settings.pop('subreddit_id')

        # These attributes come out using different names than they go in.
        remap = {'allow_top': 'default_set',
                 'lang': 'language',
                 'link_type': 'content_options'}
        for (new, old) in remap.items():
            current_settings[new] = current_settings.pop(old)

        current_settings.update(settings)
        return Subreddit._create_or_update(_reddit=self.subreddit._reddit,
                                           sr=fullname, **current_settings)


class SubredditQuarantine(object):
    """Provides submission and comment streams."""

    def __init__(self, subreddit):
        """Create a SubredditQuarantine instance.

        :param subreddit: The subreddit associated with the quarantine.

        """
        self.subreddit = subreddit

    def opt_in(self):
        """Permit your user access to the quarantined subreddit.

        Usage:

        .. code:: python

           subreddit = reddit.subreddit('QUESTIONABLE')
           next(subreddit.hot())  # Raises prawcore.Forbidden

           subreddit.quaran.opt_in()
           next(subreddit.hot())  # Returns Submission

        """
        data = {'sr_name': self.subreddit}
        try:
            self.subreddit._reddit.post(API_PATH['quarantine_opt_in'],
                                        data=data)
        except Redirect:
            pass

    def opt_out(self):
        """Remove access to the quarantined subreddit.

        Usage:

        .. code:: python

           subreddit = reddit.subreddit('QUESTIONABLE')
           next(subreddit.hot())  # Returns Submission

           subreddit.quaran.opt_out()
           next(subreddit.hot())  # Raises prawcore.Forbidden

        """
        data = {'sr_name': self.subreddit}
        try:
            self.subreddit._reddit.post(API_PATH['quarantine_opt_out'],
                                        data=data)
        except Redirect:
            pass


class SubredditRelationship(object):
    """Represents a relationship between a redditor and subreddit.

    Instances of this class can be iterated through in order to discover the
    Redditors that make up the relationship.

    For example, banned users of a subreddit can be iterated through like so:

    .. code-block:: python

       for ban in reddit.subreddit('redditdev').banned():
           print('{}: {}'.format(ban, ban.note))

    """

    def __call__(self, redditor=None, **generator_kwargs):
        """Return a generator for Redditors belonging to this relationship.

        :param redditor: Yield at most a single :class:`~.Redditor`
            instance. This is useful to confirm if a relationship exists, or to
            fetch the metadata associated with a particular relationship.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        Subreddit._safely_add_arguments(generator_kwargs, 'params',
                                        user=redditor)
        url = API_PATH['list_{}'.format(self.relationship)].format(
            subreddit=self.subreddit)
        return ListingGenerator(self.subreddit._reddit, url,
                                **generator_kwargs)

    def __init__(self, subreddit, relationship):
        """Create a SubredditRelationship instance.

        :param subreddit: The subreddit for the relationship.
        :param relationship: The name of the relationship.

        """
        self.relationship = relationship
        self.subreddit = subreddit

    def __iter__(self):
        """Iterate through the Redditors belonging to this relationship.

        .. warning:: (Deprecated) This method will be removed in PRAW 5. Prefer
                     calling ``subreddit.banned(limit=None)`` instead of
                     ``subreddit.banned`` and similar for other relationships.

        """
        url = API_PATH['list_{}'.format(self.relationship)].format(
            subreddit=self.subreddit)
        params = {'unique': self.subreddit._reddit._next_unique}
        for item in self.subreddit._reddit.get(url, params=params):
            yield item

    def add(self, redditor, **other_settings):
        """Add ``redditor`` to this relationship.

        :param redditor: A string or :class:`~.Redditor` instance.

        """
        data = {'name': str(redditor), 'type': self.relationship}
        data.update(other_settings)
        url = API_PATH['friend'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def remove(self, redditor):
        """Remove ``redditor`` from this relationship.

        :param redditor: A string or :class:`~.Redditor` instance.

        """
        data = {'name': str(redditor), 'type': self.relationship}
        url = API_PATH['unfriend'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)


class ContributorRelationship(SubredditRelationship):
    """Provides methods to interact with a Subreddit's contributors.

    Contributors of a subreddit can be iterated through like so:

    .. code-block:: python

       for contributor in reddit.subreddit('redditdev').contributors():
           print(contributor)

    """

    def leave(self):
        """Abdicate the contributor position."""
        self.subreddit._reddit.post(API_PATH['leavecontributor'],
                                    data={'id': self.subreddit.fullname})


class ModeratorRelationship(SubredditRelationship):
    """Provides methods to interact with a Subreddit's moderators.

    Moderators of a subreddit can be iterated through like so:

    .. code-block:: python

       for moderator in reddit.subreddit('redditdev').moderators():
           print(moderator)

    """

    @staticmethod
    def _handle_permissions(permissions, other_settings):
        if isinstance(permissions, list):
            other_settings = deepcopy(other_settings) if other_settings else {}
            if permissions:
                permissions = ['+{}'.format(x) for x in permissions]
            else:
                # A single permission prefixed with `-` must be provided in
                # order to have no permissions set. `-all` unfortunately is
                # treated as if no permissions are passed thus resulting in
                # full permissions.
                permissions = ['-access']
            other_settings['permissions'] = ','.join(permissions)
        return other_settings

    def add(self, redditor, permissions=None, **other_settings):
        """Add or invite ``redditor`` to be a moderator of the subreddit.

        :param redditor: A string or :class:`~.Redditor` instance.
        :param permissions: When provided (not `None`), permissions should be a
            list of strings specifying which subset of permissions to grant. An
            empty list `[]` indicates no permissions, and when not provided
            `None`, indicates full permissions.

        An invite will be sent unless the user making this call is an admin
        user.

        """
        other_settings = self._handle_permissions(permissions, other_settings)
        super(ModeratorRelationship, self).add(redditor, **other_settings)

    def invite(self, redditor, permissions=None, **other_settings):
        """Invite ``redditor`` to be a moderator of the subreddit.

        :param redditor: A string or :class:`~.Redditor` instance.
        :param permissions: When provided (not `None`), permissions should be a
            list of strings specifying which subset of permissions to grant. An
            empty list `[]` indicates no permissions, and when not provided
            `None`, indicates full permissions.

        """
        data = self._handle_permissions(permissions, other_settings)
        data.update({'name': str(redditor), 'type': 'moderator_invite'})
        url = API_PATH['friend'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def leave(self):
        """Abdicate the moderator position (use with care)."""
        self.subreddit._reddit.post(API_PATH['leavemoderator'],
                                    data={'id': self.subreddit.fullname})

    def update(self, redditor, permissions=None):
        """Update the moderator permissions for ``redditor``.

        :param redditor: A string or :class:`~.Redditor` instance.
        :param permissions: When provided (not `None`), permissions should be a
            list of strings specifying which subset of permissions to grant. An
            empty list `[]` indicates no permissions, and when not provided
            `None`, indicates full permissions.

        """
        url = API_PATH['setpermissions'].format(subreddit=self.subreddit)
        data = self._handle_permissions(
            permissions, {'name': str(redditor), 'type': 'moderator'})
        self.subreddit._reddit.post(url, data=data)

    def update_invite(self, redditor, permissions=None):
        """Update the moderator invite permissions for ``redditor``.

        :param redditor: A string or :class:`~.Redditor` instance.
        :param permissions: When provided (not `None`), permissions should be a
            list of strings specifying which subset of permissions to grant. An
            empty list `[]` indicates no permissions, and when not provided
            `None`, indicates full permissions.

        """
        url = API_PATH['setpermissions'].format(subreddit=self.subreddit)
        data = self._handle_permissions(
            permissions, {'name': str(redditor), 'type': 'moderator_invite'})
        self.subreddit._reddit.post(url, data=data)


class SubredditStream(object):
    """Provides submission and comment streams."""

    def __init__(self, subreddit):
        """Create a SubredditStream instance.

        :param subreddit: The subreddit associated with the streams.

        """
        self.subreddit = subreddit

    def comments(self):
        """Yield new comments as they become available.

        Comments are yielded oldest first. Up to 100 historical comments will
        initially be returned.

        """
        return stream_generator(self.subreddit.comments)

    def submissions(self):
        """Yield new submissions as they become available.

        Submissions are yielded oldest first. Up to 100 historical submissions
        will initially be returned.

        """
        return stream_generator(self.subreddit.new)


class SubredditStylesheet(object):
    """Provides a set of stylesheet functions to a Subreddit."""

    JPEG_HEADER = b'\xff\xd8\xff'

    def __call__(self):
        """Return the subreddit's stylesheet."""
        url = API_PATH['about_stylesheet'].format(subreddit=self.subreddit)
        return self.subreddit._reddit.get(url)

    def __init__(self, subreddit):
        """Create a SubredditStylesheet instance.

        :param subreddit: The subreddit associated with the stylesheet.

        """
        self.subreddit = subreddit

    def _upload_image(self, image_path, data):
        with open(image_path, 'rb') as image:
            header = image.read(len(self.JPEG_HEADER))
            image.seek(0)
            data['img_type'] = 'jpg' if header == self.JPEG_HEADER else 'png'
            url = API_PATH['upload_image'].format(subreddit=self.subreddit)
            return self.subreddit._reddit.post(
                url, data=data, files={'file': image})

    def delete_header(self):
        """Remove the current subreddit header image.

        Succeeds even if there is no header image.

        """
        url = API_PATH['delete_sr_header'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def delete_image(self, name):
        """Remove the named image from the subreddit.

        Succeeds even if the named image does not exist.

        """
        url = API_PATH['delete_sr_image'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data={'img_name': name})

    def update(self, stylesheet, reason=None):
        """Update the subreddit's stylesheet.

        :param stylesheet: The CSS for the new stylesheet.

        """
        data = {'op': 'save', 'reason': reason,
                'stylesheet_contents': stylesheet}
        url = API_PATH['subreddit_stylesheet'].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def upload(self, name, image_path):
        """Upload an image to the Subreddit.

        :param name: The name to use for the image. If an image already exists
            with the same name, it will be replaced.
        :param image_path: A path to a jpeg or png image.
        :returns: A dictionary containing a link to the uploaded image under
            the key ``img_src``.

        """
        return self._upload_image(image_path,
                                  {'name': name, 'upload_type': 'img'})

    def upload_header(self, image_path):
        """Upload an image to be used as the Subreddit's header image.

        :param image_path: A path to a jpeg or png image.
        :returns: A dictionary containing a link to the uploaded image under
            the key ``img_src``.

        """
        return self._upload_image(image_path, {'upload_type': 'header'})


class SubredditWiki(object):
    """Provides a set of moderation functions to a Subreddit."""

    def __getitem__(self, page_name):
        """Lazily return the WikiPage for the subreddit named ``page_name``."""
        return WikiPage(self.subreddit._reddit, self.subreddit,
                        page_name.lower())

    def __init__(self, subreddit):
        """Create a SubredditModeration instance.

        :param subreddit: The subreddit to moderate.

        """
        self.banned = SubredditRelationship(subreddit, 'wikibanned')
        self.contributors = SubredditRelationship(subreddit, 'wikicontributor')
        self.subreddit = subreddit

    def __iter__(self):
        """Iterate through the pages of the wiki."""
        response = self.subreddit._reddit.get(
            API_PATH['wiki_pages'].format(subreddit=self.subreddit),
            params={'unique': self.subreddit._reddit._next_unique})
        for page_name in response['data']:
            yield WikiPage(self.subreddit._reddit, self.subreddit, page_name)

    def create(self, name, content, reason=None, **other_settings):
        """Create a new wiki page.

        :param name: The name of the new WikiPage. This name will be normalied.
        :param content: The content of the new WikiPage.
        :param reason: (Optional) The reason for the creation.
        :param other_settings: Additional keyword arguments to pass.

        """
        name = name.replace(' ', '_').lower()
        new = WikiPage(self.subreddit._reddit, self.subreddit, name)
        new.edit(content=content, reason=reason, **other_settings)
        return new

    def revisions(self, **generator_kwargs):
        """Return a generator for recent wiki revisions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        url = API_PATH['wiki_revisions'].format(subreddit=self.subreddit)
        return WikiPage._revision_generator(
            self.subreddit, url, generator_kwargs)
