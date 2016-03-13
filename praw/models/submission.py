"""Provide the Submission class."""

from heapq import heappop, heappush

from six import text_type
from six.moves.urllib.parse import (urljoin,  # pylint: disable=import-error
                                    urlparse)

from ..const import API_PATH
from .morecomments import MoreComments
from .mixins import (EditableMixin, GildableMixin, HidableMixin,
                     ModeratableMixin, ReportableMixin, SavableMixin,
                     VotableMixin)


class Submission(EditableMixin, GildableMixin, HidableMixin, ModeratableMixin,
                 ReportableMixin, SavableMixin, VotableMixin):
    """A class for submissions to reddit."""

    _methods = (('select_flair', 'AR'),)

    @staticmethod
    def _extract_more_comments(tree):
        """Return a list of MoreComments objects removed from tree."""
        more_comments = []
        queue = [(None, x) for x in tree]
        while len(queue) > 0:
            parent, comm = queue.pop(0)
            if isinstance(comm, MoreComments):
                heappush(more_comments, comm)
                if parent:
                    parent.replies.remove(comm)
                else:
                    tree.remove(comm)
            else:
                for item in comm.replies:
                    queue.append((comm, item))
        return more_comments

    @staticmethod
    def id_from_url(url):
        """Return the ID contained within a submission URL.

        :param url: A url to a submission in one of the following formats (http
            urls will also work):
            * https://redd.it/2gmzqe
            * https://reddit.com/comments/2gmzqe/
            * https://www.reddit.com/r/redditdev/comments/2gmzqe/praw_https/

        Raise ``AttributeError`` if URL is not a valid submission URL.

        """
        parsed = urlparse(url)
        if not parsed.netloc:
            raise AttributeError('Invalid URL: {}'.format(url))

        parts = parsed.path.split('/')
        if 'comments' not in parts:
            submission_id = parts[-1]
        else:
            submission_id = parts[parts.index('comments') + 1]

        if not submission_id.isalnum():
            raise AttributeError('Invalid URL: {}'.format(url))
        return submission_id

    def __init__(self, reddit, id_or_url=None, json_dict=None, fetch=False):
        """Construct an instance of the Subreddit object.

        :param reddit: An instance of :class:`~.Reddit`.
        :param id_or_url: Either a reddit base64 submission ID, e.g.,
            ``2gmzqe``, or a URL supported by :meth:`~.id_from_url`.

        """
        if id_or_url.isalnum():
            submission_id = id_or_url
        else:
            submission_id = self.id_from_url(id_or_url)

        info_path = API_PATH['submission'].format(id=submission_id)
        super(Submission, self).__init__(reddit, json_dict, fetch, info_path)
        if 'id' not in self.__dict__:
            self.id = submission_id
        """
        self._comments_by_id = {}
        self._comments = None
        self._orphaned = {}
        self._replaced_more = False
        """

    def __unicode__(self):
        """Return a string representation of the Subreddit.

        Note: The representation is truncated to a fix number of characters.
        """
        title = self.title.replace('\r\n', ' ')
        return text_type('{0} :: {1}').format(self.score, title)

    def _insert_comment(self, comment):
        if comment.name in self._comments_by_id:  # Skip existing comments
            return

        comment._update_submission(self)
        if comment.name in self._orphaned:  # Reunite children with parent
            comment.replies.extend(self._orphaned[comment.name])
            del self._orphaned[comment.name]

        if comment.is_root:
            self._comments.append(comment)
        elif comment.parent_id in self._comments_by_id:
            self._comments_by_id[comment.parent_id].replies.append(comment)
        else:  # Orphan
            if comment.parent_id in self._orphaned:
                self._orphaned[comment.parent_id].append(comment)
            else:
                self._orphaned[comment.parent_id] = [comment]

    def _update_comments(self, comments):
        self._comments = comments
        for comment in self._comments:
            comment._update_submission(self)

    def add_comment(self, text):
        """Comment on the submission using the specified text.

        :returns: A Comment object for the newly created comment.

        """
        response = self.reddit_session._add_comment(self.fullname, text)
        return response

    @property
    def comments(self):
        """Return forest of comments, with top-level comments as tree roots.

        May contain instances of MoreComment objects. To easily replace these
        objects with Comment objects, use the replace_more_comments method then
        fetch this attribute. Use comment replies to walk down the tree. To get
        an unnested, flat list of comments from this attribute use
        helpers.flatten_tree.

        """
        if self._comments is None:
            other = Submission.from_url(self.reddit_session, self._api_path)
            self.comments = other.comments
        return self._comments

    @comments.setter
    def comments(self, new_comments):
        """Update the list of comments with the provided nested list."""
        self._update_comments(new_comments)
        self._orphaned = {}

    def get_duplicates(self, *args, **kwargs):
        """Return a get_content generator for the submission's duplicates.

        :returns: get_content generator iterating over Submission objects.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` and `object_filter` parameters
        cannot be altered.

        """
        url = self.reddit_session.config['duplicates'].format(
            submissionid=self.id)
        return self.reddit_session.get_content(url, *args, object_filter=1,
                                               **kwargs)

    def get_flair_choices(self, *args, **kwargs):
        """Return available link flair choices and current flair.

        Convenience function for
        :meth:`~.AuthenticatedReddit.get_flair_choices` populating both the
        `subreddit` and `link` parameters.

        :returns: The json response from the server.

        """
        return self.subreddit.get_flair_choices(self.fullname, *args, **kwargs)

    def mark_as_nsfw(self, unmark_nsfw=False):
        """Mark as Not Safe For Work.

        Requires that the currently authenticated user is the author of the
        submission, has the modposts oauth scope or has user/password
        authentication as a mod of the subreddit.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['unmarknsfw' if unmark_nsfw else
                                         'marknsfw']
        data = {'id': self.fullname}
        return self.reddit_session.request_json(url, data=data)

    def replace_more_comments(self, limit=32, threshold=1):
        """Update the comment tree by replacing instances of MoreComments.

        :param limit: The maximum number of MoreComments objects to
            replace. Each replacement requires 1 API request. Set to None to
            have no limit, or to 0 to make no extra requests. Default: 32
        :param threshold: The minimum number of children comments a
            MoreComments object must have in order to be replaced. Default: 1
        :returns: A list of MoreComments objects that were not replaced.

        Note that after making this call, the `comments` attribute of the
        submission will no longer contain any MoreComments objects. Items that
        weren't replaced are still removed from the tree, and will be included
        in the returned list.

        """
        if self._replaced_more:
            return []

        remaining = limit
        more_comments = self._extract_more_comments(self.comments)
        skipped = []

        # Fetch largest more_comments until reaching the limit or the threshold
        while more_comments:
            item = heappop(more_comments)
            if remaining == 0:  # We're not going to replace any more
                heappush(more_comments, item)  # It wasn't replaced
                break
            elif len(item.children) == 0 or 0 < item.count < threshold:
                heappush(skipped, item)  # It wasn't replaced
                continue

            # Fetch new comments and decrease remaining if a request was made
            new_comments = item.comments(update=False)
            if new_comments is not None and remaining is not None:
                remaining -= 1
            elif new_comments is None:
                continue

            # Re-add new MoreComment objects to the heap of more_comments
            for more in self._extract_more_comments(new_comments):
                more._update_submission(self)
                heappush(more_comments, more)
            # Insert the new comments into the tree
            for comment in new_comments:
                self._insert_comment(comment)

        self._replaced_more = True
        return more_comments + skipped

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
        url = self.reddit_session.config['contest_mode']
        data = {'id': self.fullname, 'state': state}
        return self.reddit_session.request_json(url, data=data)

    def set_suggested_sort(self, sort='blank'):
        """Set 'Suggested Sort' for the comments of the submission.

        Comments can be sorted in one of (confidence, top, new, hot,
        controversial, old, random, qa, blank).

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['suggested_sort']
        data = {'id': self.fullname, 'sort': sort}
        return self.reddit_session.request_json(url, data=data)

    @property
    def short_link(self):
        """Return a short link to the submission.

        For example http://redd.it/eorhm is a short link for
        https://www.reddit.com/r/announcements/comments/eorhm/reddit_30_less_typing/.

        """
        return urljoin(self.reddit_session.config.short_url, self.id)

    def sticky(self, bottom=True):
        """Sticky a post in its subreddit.

        If there is already a stickied post in the designated slot it will be
        unstickied.

        :param bottom: Set this as the top or bottom sticky. If no top sticky
            exists, this submission will become the top sticky regardless.

        :returns: The json response from the server

        """
        url = self.reddit_session.config['sticky_submission']
        data = {'id': self.fullname, 'state': True}
        if not bottom:
            data['num'] = 1
        return self.reddit_session.request_json(url, data=data)

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
        url = self.reddit_session.config['sticky_submission']
        data = {'id': self.fullname, 'state': False}
        return self.reddit_session.request_json(url, data=data)
