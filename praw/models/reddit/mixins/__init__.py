"""Package providing reddit class mixins."""
from ....const import API_PATH
from .editable import EditableMixin  # NOQA
from .gildable import GildableMixin  # NOQA
from .inboxable import InboxableMixin  # NOQA
from .inboxtoggleable import InboxToggleableMixin  # NOQA
from .messageable import MessageableMixin  # NOQA
from .replyable import ReplyableMixin  # NOQA
from .reportable import ReportableMixin  # NOQA
from .savable import SavableMixin  # NOQA
from .votable import VotableMixin  # NOQA


class ThingModerationMixin(object):
    """Provides moderation methods for Comments and Submissions."""

    def approve(self):
        """Approve a :class:`~.Comment` or :class:`~.Submission`.

        Approving a comment or submission reverts a removal, resets the report
        counter, adds a green check mark indicator (only visible to other
        moderators) on the website view, and sets the ``approved_by`` attribute
        to the authenticated user.

        Example usage:

        .. code:: python

           # approve a comment:
           comment = reddit.comment('dkk4qjd')
           comment.mod.approve()
           # approve a submission:
           submission = reddit.submission(id='5or86n')
           submission.mod.approve()

        """
        self.thing._reddit.post(API_PATH['approve'],
                                data={'id': self.thing.fullname})

    def distinguish(self, how='yes', sticky=False):
        """Distinguish a :class:`~.Comment` or :class:`~.Submission`.

        :param how: One of 'yes', 'no', 'admin', 'special'. 'yes' adds a
            moderator level distinguish. 'no' removes any distinction. 'admin'
            and 'special' require special user privileges to use.
        :param sticky: Comment is stickied if True, placing it at the top of
            the comment page regardless of score. If thing is not a top-level
            comment, this parameter is silently ignored.

        Example usage:

        .. code:: python

           # distinguish and sticky a comment:
           comment = reddit.comment('dkk4qjd')
           comment.mod.distinguish(how='yes', sticky=True)
           # undistinguish a submission:
           submission = reddit.submission(id='5or86n')
           submission.mod.distinguish(how='no')

        See also :meth:`~.undistinguish`

        """
        data = {'how': how, 'id': self.thing.fullname}
        if sticky and getattr(self.thing, 'is_root', False):
            data['sticky'] = True
        self.thing._reddit.post(API_PATH['distinguish'], data=data)

    def ignore_reports(self):
        """Ignore future reports on a Comment or Submission.

        Calling this method will prevent future reports on this Comment or
        Submission from both triggering notifications and appearing in the
        various moderation listings. The report count will still increment on
        the Comment or Submission.

        Example usage:

        .. code:: python

           # ignore future reports on a comment:
           comment = reddit.comment('dkk4qjd')
           comment.mod.ignore_reports()
           # ignore future reports on a submission
           submission = reddit.submission(id='5or86n')
           submission.mod.ignore_reports()

        See also :meth:`~.unignore_reports`

        """
        self.thing._reddit.post(API_PATH['ignore_reports'],
                                data={'id': self.thing.fullname})

    def remove(self, spam=False):
        """Remove a :class:`~.Comment` or :class:`~.Submission`.

        :param spam: When True, use the removal to help train the Subreddit's
            spam filter (default: False).

        Example usage:

        .. code:: python

           # remove a comment and mark as spam:
           comment = reddit.comment('dkk4qjd')
           comment.mod.remove(spam=True)
           # remove a submission
           submission = reddit.submission(id='5or86n')
           submission.mod.remove()

        """
        data = {'id': self.thing.fullname, 'spam': bool(spam)}
        self.thing._reddit.post(API_PATH['remove'], data=data)

    def undistinguish(self):
        """Remove mod, admin, or special distinguishing on object.

        Also unstickies the object if applicable.

        Example usage:

        .. code:: python

           # undistinguish a comment:
           comment = reddit.comment('dkk4qjd')
           comment.mod.undistinguish()
           # undistinguish a submission:
           submission = reddit.submission(id='5or86n')
           submission.mod.undistinguish()

        See also :meth:`~.distinguish`

        """
        self.distinguish(how='no')

    def unignore_reports(self):
        """Resume receiving future reports on a Comment or Submission.

        Future reports on this Comment or Submission will cause notifications,
        and appear in the various moderation listings.

        Example usage:

        .. code:: python

           # accept future reports on a comment:
           comment = reddit.comment('dkk4qjd')
           comment.mod.unignore_reports()
           # accept future reports on a submission
           submission = reddit.submission(id='5or86n')
           submission.mod.unignore_reports()

        See also :meth:`~.ignore_reports`

        """
        self.thing._reddit.post(API_PATH['unignore_reports'],
                                data={'id': self.thing.fullname})


class UserContentMixin(EditableMixin, GildableMixin, InboxToggleableMixin,
                       ReplyableMixin, ReportableMixin, SavableMixin,
                       VotableMixin):
    """A convenience mixin that applies to both Comments and Submissions."""
