"""Package providing reddit class mixins."""
from json import dumps
from ....const import API_PATH
from .editable import EditableMixin
from .fullname import FullnameMixin
from .gildable import GildableMixin
from .inboxable import InboxableMixin
from .inboxtoggleable import InboxToggleableMixin
from .messageable import MessageableMixin
from .replyable import ReplyableMixin
from .reportable import ReportableMixin
from .savable import SavableMixin
from .votable import VotableMixin


class ThingModerationMixin(object):
    """Provides moderation methods for Comments and Submissions."""

    REMOVAL_MESSAGE_API = None

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
        self.thing._reddit.post(
            API_PATH["approve"], data={"id": self.thing.fullname}
        )

    def distinguish(self, how="yes", sticky=False):
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
        data = {"how": how, "id": self.thing.fullname}
        if sticky and getattr(self.thing, "is_root", False):
            data["sticky"] = True
        self.thing._reddit.post(API_PATH["distinguish"], data=data)

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
        self.thing._reddit.post(
            API_PATH["ignore_reports"], data={"id": self.thing.fullname}
        )

    def lock(self):
        """Lock the a :class:`~.Comment` or :class:`~.Submission`.

        Example usage:

           # lock a comment:
           comment = reddit.comment('dkk4qjd')
           comment.mod.lock()
           # lock a submission:
           submission = reddit.submission(id='5or86n')
           submission.mod.lock()

        See also :meth:`~.unlock`

        """
        self.thing._reddit.post(
            API_PATH["lock"], data={"id": self.thing.fullname}
        )

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
        data = {"id": self.thing.fullname, "spam": bool(spam)}
        self.thing._reddit.post(API_PATH["remove"], data=data)

    def send_removal_message(
        self,
        message,
        title="ignored",
        type="public",  # pylint: disable=redefined-builtin
    ):
        """Send a removal message for a Comment or Submission.

        Reddit adds human-readable information about the object to the message.

        :param type: One of 'public', 'private', 'private_exposed'.
            'public' leaves a stickied comment on the post.
            'private' sends a Modmail message with hidden username.
            'private_exposed' sends a Modmail message without hidden username.
        :param title: The short reason given in the message.
            (Ignored if type is 'public'.)
        :param message: The body of the message.

        If ``type`` is 'public', the new :class:`~.Comment` is returned.
        """
        # The API endpoint used to send removal messages is different
        # for posts and comments, so the derived classes specify which one.
        if self.REMOVAL_MESSAGE_API is None:
            raise NotImplementedError("ThingModerationMixin must be extended.")
        url = API_PATH[self.REMOVAL_MESSAGE_API]

        # Only the first element of the item_id list is used.
        data = {
            "item_id": [self.thing.fullname],
            "message": message,
            "title": title,
            "type": type,
        }

        return self.thing._reddit.post(url, data={"json": dumps(data)}) or None

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
        self.distinguish(how="no")

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
        self.thing._reddit.post(
            API_PATH["unignore_reports"], data={"id": self.thing.fullname}
        )

    def unlock(self):
        """Unlock the a :class:`~.Comment` or :class:`~.Submission`.

        Example usage:

           # unlock a comment:
           comment = reddit.comment('dkk4qjd')
           comment.mod.unlock()
           # unlock a submission:
           submission = reddit.submission(id='5or86n')
           submission.mod.unlock()

        See also :meth:`~.lock`

        """
        self.thing._reddit.post(
            API_PATH["unlock"], data={"id": self.thing.fullname}
        )


class UserContentMixin(
    EditableMixin,
    GildableMixin,
    InboxToggleableMixin,
    ReplyableMixin,
    ReportableMixin,
    SavableMixin,
    VotableMixin,
):
    """A convenience mixin that applies to both Comments and Submissions."""
