"""Provide the Comment class."""

from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from .mixins import (EditableMixin, GildableMixin, InboxableMixin,
                     ModeratableMixin, ReportableMixin, SavableMixin,
                     VotableMixin)
from .redditor import Redditor
from .subreddit import Subreddit


class Comment(EditableMixin, GildableMixin, InboxableMixin, ModeratableMixin,
              ReportableMixin, SavableMixin, VotableMixin):
    """A class that represents a reddit comments."""

    def __init__(self, reddit, submission, data):
        """Construct an instance of the Comment object."""
        super(Comment, self).__init__(reddit)
        self._submission = submission
        self._populate(data)

    @property
    def _fast_permalink(self):
        """Return the short permalink to the comment."""
        if hasattr(self, 'link_id'):  # from /r or /u comments page
            sid = self.link_id.split('_')[1]
        else:  # from user's /message page
            sid = self.context.split('/')[4]
        return urljoin(self._reddit.config['comments'], '{}/_/{}'
                       .format(sid, self.id))

    def _transform_data(self, original_data):
        data = original_data['data']
        data['author'] = Redditor.from_data(self._reddit, data['author'])
        data['subreddit'] = Subreddit(self._reddit, data['subreddit'])
        replies = []
        if data['replies'] != '':
            for reply in data['replies']['data']['children']:
                replies.append(Comment(self._reddit, self._submission, reply))
        data['replies'] = replies
        return data

    @property
    def is_root(self):
        """Return True when the comment is a top level comment."""
        submission_prefix = self._reddit.config._obj['subreddit_kind']
        return self.parent_id.startswith(submission_prefix)

    @property
    def permalink(self):
        """Return a permalink to the comment."""
        return urljoin(self.submission.permalink, self.id)

    @property
    def submission(self):
        """Return the Submission object this comment belongs to."""
        if not self._submission:  # Comment not from submission
            self._submission = self._reddit.get_submission(
                url=self._fast_permalink)
        return self._submission
