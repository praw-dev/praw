"""Provide the Comment class."""

from six.moves.urllib.parse import urljoin

from .mixins import (EditableMixin, GildableMixin, InboxableMixin,
                     ModeratableMixin, ReportableMixin, SavableMixin,
                     VotableMixin)
from .submission import Submission
from ..errors import InvalidComment


class Comment(EditableMixin, GildableMixin, InboxableMixin, ModeratableMixin,
              ReportableMixin, SavableMixin, VotableMixin):
    """A class that represents a reddit comments."""

    def __init__(self, reddit_session, json_dict):
        """Construct an instance of the Comment object."""
        super(Comment, self).__init__(reddit_session, json_dict,
                                      underscore_names=['replies'])
        self._has_fetched_replies = not hasattr(self, 'was_comment')
        if self._replies:
            self._replies = self._replies['data']['children']
        elif self._replies == '':  # Comment tree was built and there are none
            self._replies = []
        else:
            self._replies = None
        self._submission = None

    def __unicode__(self):
        """Return a string representation of the comment."""
        return getattr(self, 'body', '[Unloaded Comment]')

    @property
    def _fast_permalink(self):
        """Return the short permalink to the comment."""
        if hasattr(self, 'link_id'):  # from /r or /u comments page
            sid = self.link_id.split('_')[1]
        else:  # from user's /message page
            sid = self.context.split('/')[4]
        return urljoin(self.reddit_session.config['comments'], '{0}/_/{1}'
                       .format(sid, self.id))

    def _update_submission(self, submission):
        """Submission isn't set on __init__ thus we need to update it."""
        submission._comments_by_id[self.name] = self
        self._submission = submission
        if self._replies:
            for reply in self._replies:
                reply._update_submission(submission)

    @property
    def is_root(self):
        """Return True when the comment is a top level comment."""
        sub_prefix = self.reddit_session.config.by_object[Submission]
        return self.parent_id.startswith(sub_prefix)

    @property
    def permalink(self):
        """Return a permalink to the comment."""
        return urljoin(self.submission.permalink, self.id)

    @property
    def replies(self):
        """Return a list of the comment replies to this comment."""
        if self._replies is None or not self._has_fetched_replies:
            response = self.reddit_session.request_json(self._fast_permalink)
            if not response[1]['data']['children']:
                raise InvalidComment('Comment is no longer accessible: {0}'
                                     .format(self._fast_permalink))
            self._replies = response[1]['data']['children'][0]._replies
            self._has_fetched_replies = True
            # Set the submission object if it is not set.
            if not self._submission:
                self._submission = response[0]['data']['children'][0]
        return self._replies

    @property
    def submission(self):
        """Return the Submission object this comment belongs to."""
        if not self._submission:  # Comment not from submission
            self._submission = self.reddit_session.get_submission(
                url=self._fast_permalink)
        return self._submission
