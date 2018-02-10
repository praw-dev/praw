"""Provide the Submission class."""
from ...const import API_PATH, urljoin
from ...exceptions import ClientException
from ..comment_forest import CommentForest
from ..listing.mixins import SubmissionListingMixin
from .base import RedditBase
from .mixins import ThingModerationMixin, UserContentMixin
from .redditor import Redditor
from .subreddit import Subreddit


class Submission(RedditBase, SubmissionListingMixin, UserContentMixin):
    """A class for submissions to reddit."""

    STR_FIELD = 'id'

    @staticmethod
    def id_from_url(url):
        """Return the ID contained within a submission URL.

        :param url: A url to a submission in one of the following formats (http
            urls will also work):
            * https://redd.it/2gmzqe
            * https://reddit.com/comments/2gmzqe/
            * https://www.reddit.com/r/redditdev/comments/2gmzqe/praw_https/

        Raise :class:`.ClientException` if URL is not a valid submission URL.

        """
        parts = RedditBase._url_parts(url)
        if 'comments' not in parts:
            submission_id = parts[-1]
            if 'r' in parts:
                raise ClientException('Invalid URL (subreddit, '
                                      'not submission): {}'.format(url))
        else:
            submission_id = parts[parts.index('comments') + 1]

        if not submission_id.isalnum():
            raise ClientException('Invalid URL: {}'.format(url))
        return submission_id

    @property
    def comments(self):
        """Provide an instance of :class:`.CommentForest`.

        This attribute can use used, for example, to obtain a flat list of
        comments, with any :class:`.MoreComments` removed:

        .. code:: python

           submission.comments.replace_more(limit=0)
           comments = submission.comments.list()

        Sort order and comment limit can be set with the ``comment_sort`` and
        ``comment_limit`` attributes before comments are fetched, including
        any call to :meth:`.replace_more`:

        .. code:: python

           submission.comment_sort = 'new'
           comments = submission.comments.list()

        See :ref:`extracting_comments` for more on working with a
        :class:`.CommentForest`.

        """
        # This assumes _comments is set so that _fetch is called when it's not.
        return self._comments

    @property
    def flair(self):
        """Provide an instance of :class:`.SubmissionFlair`.

        This attribute is used to work with flair as a regular user of the
        subreddit the submission belongs to. Moderators can directly use
        :meth:`.flair`.

        For example, to select an arbitrary editable flair text (assuming there
        is one) and set a custom value try:

        .. code:: python

           choices = submission.flair.choices()
           template_id = next(x for x in choices
                              if x['flair_text_editable'])['flair_template_id']
           submission.flair.select(template_id, 'my custom value')

        """
        if self._flair is None:
            self._flair = SubmissionFlair(self)
        return self._flair

    @property
    def mod(self):
        """Provide an instance of :class:`.SubmissionModeration`."""
        if self._mod is None:
            self._mod = SubmissionModeration(self)
        return self._mod

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 url=None, _data=None):
        """Initialize a Submission instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param id: A reddit base36 submission ID, e.g., ``2gmzqe``.
        :param url: A URL supported by
            :meth:`~praw.models.Submission.id_from_url`.

        Either ``id`` or ``url`` can be provided, but not both.

        """
        if [id, url, _data].count(None) != 2:
            raise TypeError('Exactly one of `id`, `url`, or `_data` must be '
                            'provided.')
        super(Submission, self).__init__(reddit, _data)
        self.comment_limit = 2048

        #: Specify the sort order for ``comments``
        self.comment_sort = 'best'

        if id is not None:
            self.id = id  # pylint: disable=invalid-name
        elif url is not None:
            self.id = self.id_from_url(url)
        self._flair = self._mod = None

        self._comments_by_id = {}

    def __setattr__(self, attribute, value):
        """Objectify author, and subreddit attributes."""
        if attribute == 'author':
            value = Redditor.from_data(self._reddit, value)
        elif attribute == 'subreddit':
            value = Subreddit(self._reddit, value)
        super(Submission, self).__setattr__(attribute, value)

    def _chunk(self, other_submissions, chunk_size):
        all_submissions = [self.fullname]
        if other_submissions:
            all_submissions += [x.fullname for x in other_submissions]

        for position in range(0, len(all_submissions), chunk_size):
            yield ','.join(all_submissions[position:position + 50])

    def _fetch(self):
        other, comments = self._reddit.get(self._info_path(),
                                           params={'limit': self.comment_limit,
                                                   'sort': self.comment_sort})
        other = other.children[0]
        delattr(other, 'comment_limit')
        delattr(other, 'comment_sort')
        other._comments = CommentForest(self)
        self.__dict__.update(other.__dict__)
        self.comments._update(comments.children)
        self._fetched = True

    def _info_path(self):
        return API_PATH['submission'].format(id=self.id)

    def hide(self, other_submissions=None):
        """Hide Submission.

        :param other_submissions: When provided, additionally
            hide this list of :class:`.Submission` instances
            as part of a single request (default: None).

        """
        for submissions in self._chunk(other_submissions, 50):
            self._reddit.post(API_PATH['hide'], data={'id': submissions})

    @property
    def shortlink(self):
        """Return a shortlink to the submission.

        For example http://redd.it/eorhm is a shortlink for
        https://www.reddit.com/r/announcements/comments/eorhm/reddit_30_less_typing/.

        """
        return urljoin(self._reddit.config.short_url, self.id)

    def unhide(self, other_submissions=None):
        """Unhide Submission.

        :param other_submissions: When provided, additionally
            unhide this list of :class:`.Submission` instances
            as part of a single request (default: None).

        """
        for submissions in self._chunk(other_submissions, 50):
            self._reddit.post(API_PATH['unhide'], data={'id': submissions})

    def crosspost(self, subreddit, title=None, send_replies=True):
        """Crosspost the submission to a subreddit.

        :param subreddit: Name of the subreddit or :class:`~.Subreddit`
            object to crosspost into.
        :param title: Title of the submission. Will use this submission's
            title if `None` (default: None).
        :param send_replies: When True, messages will be sent to the
            submission author when comments are made to the submission
            (default: True).
        :returns: A :class:`~.Submission` object for the newly created
            submission.
        """
        if title is None:
            title = self.title

        data = {'sr': str(subreddit),
                'title': title,
                'sendreplies': bool(send_replies),
                'kind': 'crosspost',
                'crosspost_fullname': self.fullname}
        return self._reddit.post(API_PATH['submit'], data=data)


class SubmissionFlair(object):
    """Provide a set of functions pertaining to Submission flair."""

    def __init__(self, submission):
        """Create a SubmissionFlair instance.

        :param submission: The submission associated with the flair functions.

        """
        self.submission = submission

    def choices(self):
        """Return list of available flair choices.

        Choices are required in order to use :meth:`.select`.

        Example:

        .. code:: python

           choices = submission.flair.choices()

        """
        url = API_PATH['flairselector'].format(
            subreddit=self.submission.subreddit)
        return self.submission._reddit.post(url, data={
            'link': self.submission.fullname})['choices']

    def select(self, flair_template_id, text=None):
        """Select flair for submission.

        :param flair_template_id: The flair template to select. The possible
            ``flair_template_id`` values can be discovered through
            :meth:`.choices`.
        :param text: If the template's ``flair_text_editable`` value is True,
            this value will set a custom text (default: None).

        For example, to select an arbitrary editable flair text (assuming there
        is one) and set a custom value try:

        .. code:: python

           choices = submission.flair.choices()
           template_id = next(x for x in choices
                              if x['flair_text_editable'])['flair_template_id']
           submission.flair.select(template_id, 'my custom value')

        """
        data = {'flair_template_id': flair_template_id,
                'link': self.submission.fullname, 'text': text}
        url = API_PATH['select_flair'].format(
            subreddit=self.submission.subreddit)
        self.submission._reddit.post(url, data=data)


class SubmissionModeration(ThingModerationMixin):
    """Provide a set of functions pertaining to Submission moderation."""

    def __init__(self, submission):
        """Create a SubmissionModeration instance.

        :param submission: The submission to moderate.

        """
        self.thing = submission

    def contest_mode(self, state=True):
        """Set contest mode for the comments of this submission.

        :param state: (boolean) True enables contest mode, False, disables
            (default: True).

        Contest mode have the following effects:
          * The comment thread will default to being sorted randomly.
          * Replies to top-level comments will be hidden behind
            "[show replies]" buttons.
          * Scores will be hidden from non-moderators.
          * Scores accessed through the API (mobile apps, bots) will be
            obscured to "1" for non-moderators.

        """
        self.thing._reddit.post(API_PATH['contest_mode'], data={
            'id': self.thing.fullname, 'state': state})

    def flair(self, text='', css_class=''):
        """Set flair for the submission.

        :param text: The flair text to associate with the Submission (default:
            '').
        :param css_class: The css class to associate with the flair html
            (default: '').

        This method can only be used by an authenticated user who is a
        moderator of the Submission's Subreddit.

        Example:

        .. code:: python

           submission.mod.flair(text='PRAW', css_class='bot')

        """
        data = {'css_class': css_class, 'link': self.thing.fullname,
                'text': text}
        url = API_PATH['flair'].format(subreddit=self.thing.subreddit)
        self.thing._reddit.post(url, data=data)

    def lock(self):
        """Lock the submission."""
        self.thing._reddit.post(API_PATH['lock'],
                                data={'id': self.thing.fullname})

    def nsfw(self):
        """Mark as not safe for work.

        This method can be used both by the submission author and moderators of
        the subreddit that the submission belongs to.

        Example:

        .. code:: python

            submission = reddit.subreddit('test').submit('nsfw test',
                                                         selftext='nsfw')
            submission.mod.nsfw()

        """
        self.thing._reddit.post(API_PATH['marknsfw'],
                                data={'id': self.thing.fullname})

    def sfw(self):
        """Mark as safe for work.

        This method can be used both by the submission author and moderators of
        the subreddit that the submission belongs to.

        Example:

        .. code:: python

            submission = reddit.submission(id='5or86n')
            submission.mod.sfw()

        """
        self.thing._reddit.post(API_PATH['unmarknsfw'],
                                data={'id': self.thing.fullname})

    def spoiler(self):
        """Indicate that the submission contains spoilers.

        This method can be used both by the submission author and moderators of
        the subreddit that the submission belongs to.

        Example:

        .. code:: python

            submission = reddit.submission(id='5or86n')
            submission.mod.spoiler()

        """
        self.thing._reddit.post(API_PATH['spoiler'],
                                data={'id': self.thing.fullname})

    def sticky(self, state=True, bottom=True):
        """Set the submission's sticky state in its subreddit.

        :param state: (boolean) True sets the sticky for the submission, false
            unsets (default: True).
        :param bottom: (boolean) When true, set the submission as the bottom
            sticky. If no top sticky exists, this submission will become the
            top sticky regardless (default: True).

        This submission will replace an existing stickied submission if one
        exists.

        Example:

        .. code:: python

           submission.mod.sticky()

        """
        data = {'id': self.thing.fullname, 'state': state}
        if not bottom:
            data['num'] = 1
        return self.thing._reddit.post(API_PATH['sticky_submission'],
                                       data=data)

    def suggested_sort(self, sort='blank'):
        """Set the suggested sort for the comments of the submission.

        :param sort: Can be one of: confidence, top, new, controversial, old,
            random, qa, blank (default: blank).

        """
        self.thing._reddit.post(API_PATH['suggested_sort'], data={
            'id': self.thing.fullname, 'sort': sort})

    def unlock(self):
        """Unlock the submission."""
        self.thing._reddit.post(API_PATH['unlock'],
                                data={'id': self.thing.fullname})

    def unspoiler(self):
        """Indicate that the submission does not contain spoilers.

        This method can be used both by the submission author and moderators of
        the subreddit that the submission belongs to.

        Example:

        .. code:: python

            submission = reddit.subreddit('test').submit('not spoiler',
                                                         selftext='spoiler')
            submission.mod.unspoiler()

        """
        self.thing._reddit.post(API_PATH['unspoiler'],
                                data={'id': self.thing.fullname})


Subreddit._submission_class = Submission
