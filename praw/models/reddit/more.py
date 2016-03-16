"""Provide the MoreComments class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from .base import RedditBase


class MoreComments(RedditBase):
    """A class indicating there are more comments."""

    def __init__(self, reddit_session, json_dict):
        """Construct an instance of the MoreComment object."""
        super(MoreComments, self).__init__(reddit_session, json_dict)
        self.submission = None
        self._comments = None

    def __lt__(self, other):
        """Proide a sort order on the MoreComments object."""
        # To work with heapq a "smaller" item is the one with the most comments
        # We are intentionally making the biggest element the smallest element
        # to turn the min-heap implementation in heapq into a max-heap
        # implementation for Submission.replace_more_comments()
        return self.count > other.count

    def _continue_comments(self, update):
        assert len(self.children) > 0
        tmp = self.reddit_session.get_submission(urljoin(
            self.submission.permalink, self.parent_id.split('_', 1)[1]))
        assert len(tmp.comments) == 1
        self._comments = tmp.comments[0].replies
        if update:
            for comment in self._comments:
                comment._update_submission(self.submission)
        return self._comments

    def _update_submission(self, submission):
        self.submission = submission

    def comments(self, update=True):
        """Fetch and return the comments for a single MoreComments object."""
        if not self._comments:
            if self.count == 0:  # Handle 'continue this thread' type
                return self._continue_comments(update)
            children = [x for x in self.children if 't1_{0}'.format(x)
                        not in self.submission._comments_by_id]
            if not children:
                return None
            data = {'children': ','.join(children),
                    'link_id': self.submission.fullname,
                    'r': str(self.submission.subreddit)}

            if self.submission._comment_sort:
                data['where'] = self.submission._comment_sort
            url = self.reddit_session.config['morechildren']
            response = self.reddit_session.request_json(url, data=data)
            self._comments = response['data']['things']
            if update:
                for comment in self._comments:
                    comment._update_submission(self.submission)
        return self._comments
