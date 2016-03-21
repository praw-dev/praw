"""Provide the Submission class."""
from six.moves.urllib.parse import (urljoin,  # pylint: disable=import-error
                                    urlparse)

from ...const import API_PATH
from ...exceptions import ClientException
from ..comment_forest import CommentForest
from ..listing.mixins import SubmissionListingMixin
from .base import RedditBase
from .mixins import UserContentMixin
from .redditor import Redditor
from .subreddit import Subreddit


class Submission(RedditBase, SubmissionListingMixin, UserContentMixin):
    """A class for submissions to reddit."""

    EQ_FIELD = 'id'

    @staticmethod
    def id_from_url(url):
        """Return the ID contained within a submission URL.

        :param url: A url to a submission in one of the following formats (http
            urls will also work):
            * https://redd.it/2gmzqe
            * https://reddit.com/comments/2gmzqe/
            * https://www.reddit.com/r/redditdev/comments/2gmzqe/praw_https/

        Raise ``ClientException`` if URL is not a valid submission URL.

        """
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ClientException('Invalid URL: {}'.format(url))

        parts = parsed.path.split('/')
        if 'comments' not in parts:
            submission_id = parts[-1]
        else:
            submission_id = parts[parts.index('comments') + 1]

        if not submission_id.isalnum():
            raise ClientException('Invalid URL: {}'.format(url))
        return submission_id

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 url=None, _data=None):
        """Initialize a Submission instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param id: A reddit base64 submission ID, e.g., ``2gmzqe``.
        :param url: A URL supported by :meth:`~.id_from_url`.

        Either ``id`` or ``url`` can be provided, but not both.

        """
        if [id, url, _data].count(None) != 2:
            raise TypeError('Exactly one of `id`, `url`, or `_data` must be '
                            'provided.')
        super(Submission, self).__init__(reddit, _data)
        self.comment_limit = 2048
        self.comment_sort = 'best'
        if id is not None:
            self.id = id  # pylint: disable=invalid-name
        elif url is not None:
            self.id = self.id_from_url(url)

    def __setattr__(self, attribute, value):
        """Objectify author, comments, and subreddit attributes."""
        # pylint: disable=redefined-variable-type
        if attribute == 'author':
            value = Redditor.from_data(self._reddit, value)
        elif attribute == 'subreddit':
            value = Subreddit(self._reddit, value)
        super(Submission, self).__setattr__(attribute, value)

    def _fetch(self):
        other, comments = self._reddit.get(self._info_path(),
                                           params={'limit': self.comment_limit,
                                                   'sort': self.comment_sort})
        other = other.children[0]
        other.comments = CommentForest(self)
        self.__dict__.update(other.__dict__)
        self.comments._update(comments.children)
        self._fetched = True

    def _info_path(self):
        return API_PATH['submission'].format(id=self.id)

    def get_flair_choices(self, *args, **kwargs):
        """Return available link flair choices and current flair.

        Convenience function for
        :meth:`~.AuthenticatedReddit.get_flair_choices` populating both the
        `subreddit` and `link` parameters.

        :returns: The json response from the server.

        """
        return self.subreddit.get_flair_choices(self.fullname, *args, **kwargs)

    def hide(self, _unhide=False):
        """Hide object in the context of the logged in user.

        :param _unhide: If True, unhide the item instead.  Use
            :meth:`~.unhide` instead of setting this
            manually.

        :returns: The json response from the server.

        """
        return self._reddit.hide(self.fullname, _unhide=_unhide)

    def mark_as_nsfw(self, unmark_nsfw=False):
        """Mark as Not Safe For Work.

        Requires that the currently authenticated user is the author of the
        submission, has the modposts oauth scope or has user/password
        authentication as a mod of the subreddit.

        :returns: The json response from the server.

        """
        url = self._reddit.config['unmarknsfw' if unmark_nsfw else 'marknsfw']
        data = {'id': self.fullname}
        return self._reddit.request_json(url, data=data)

    def set_flair(self, *args, **kwargs):
        """Set flair for this submission.

        Convenience function that utilizes :meth:`.ModFlairMixin.set_flair`
        populating both the `subreddit` and `item` parameters.

        :returns: The json response from the server.

        """
        return self.subreddit.set_flair(self, *args, **kwargs)

    def set_contest_mode(self, state=True):
        """Set 'Contest Mode' for the comments of this submission.

        Contest mode have the following effects:
          * The comment thread will default to being sorted randomly.
          * Replies to top-level comments will be hidden behind
            "[show replies]" buttons.
          * Scores will be hidden from non-moderators.
          * Scores accessed through the API (mobile apps, bots) will be
            obscured to "1" for non-moderators.

        Source for effects: https://www.reddit.com/159bww/

        :returns: The json response from the server.

        """
        url = self._reddit.config['contest_mode']
        data = {'id': self.fullname, 'state': state}
        return self._reddit.request_json(url, data=data)

    def set_suggested_sort(self, sort='blank'):
        """Set 'Suggested Sort' for the comments of the submission.

        Comments can be sorted in one of (confidence, top, new, hot,
        controversial, old, random, qa, blank).

        :returns: The json response from the server.

        """
        url = self._reddit.config['suggested_sort']
        data = {'id': self.fullname, 'sort': sort}
        return self._reddit.request_json(url, data=data)

    @property
    def short_link(self):
        """Return a short link to the submission.

        For example http://redd.it/eorhm is a short link for
        https://www.reddit.com/r/announcements/comments/eorhm/reddit_30_less_typing/.

        """
        return urljoin(self._reddit.config.short_url, self.id)

    def sticky(self, bottom=True):
        """Sticky a post in its subreddit.

        If there is already a stickied post in the designated slot it will be
        unstickied.

        :param bottom: Set this as the top or bottom sticky. If no top sticky
            exists, this submission will become the top sticky regardless.

        :returns: The json response from the server

        """
        url = self._reddit.config['sticky_submission']
        data = {'id': self.fullname, 'state': True}
        if not bottom:
            data['num'] = 1
        return self._reddit.request_json(url, data=data)

    def unhide(self):
        """Unhide object in the context of the logged in user.

        :returns: The json response from the server.

        """
        return self.hide(_unhide=True)

    def unmark_as_nsfw(self):
        """Mark as Safe For Work.

        :returns: The json response from the server.

        """
        return self.mark_as_nsfw(unmark_nsfw=True)

    def unset_contest_mode(self):
        """Unset 'Contest Mode' for the comments of this submission.

        Contest mode have the following effects:
          * The comment thread will default to being sorted randomly.
          * Replies to top-level comments will be hidden behind
            "[show replies]" buttons.
          * Scores will be hidden from non-moderators.
          * Scores accessed through the API (mobile apps, bots) will be
            obscured to "1" for non-moderators.

        Source for effects: http://www.reddit.com/159bww/

        :returns: The json response from the server.

        """
        return self.set_contest_mode(False)

    def unsticky(self):
        """Unsticky this post.

        :returns: The json response from the server

        """
        url = self._reddit.config['sticky_submission']
        data = {'id': self.fullname, 'state': False}
        return self._reddit.request_json(url, data=data)
