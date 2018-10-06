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

    def send_removal_message(self, type,  # pylint: disable=redefined-builtin
                             title=None, message=None):
        """Send a removal message for a Comment or Submission.

        Reddit adds human-readable information about the object to the message.

        :param type: One of 'public', 'private', 'private_exposed'.
            'public' leaves a stickied comment on the post.
            'private' sends a Modmail message with hidden username.
            'private_exposed' sends a Modmail message without hidden username.
        :param title: The short reason given in the message.
            (Ignored if type is 'public'.)
        :param message: The body of the message.
        """
        # The API endpoint used to send removal messages is different
        # for posts and comments, so the derived classes specify which one.
        if self.REMOVAL_MESSAGE_API is None:
            raise NotImplementedError('ThingModerationMixin must be extended.')
        url = API_PATH[self.REMOVAL_MESSAGE_API]

        # Only the first element of the item_id list is used.
        data = {"item_id": [self.thing.fullname],
                "message": message,
                "title": title,
                "type": str(type)}

        # Use the core to make the request in order to send the data as
        # JSON - this endpoint doesn't like URL encoding.
        self.thing._reddit._core.request('POST', url, json=data)

    def set_removal_reason(self, reason=None, mod_note="", other_things=None):
        """Set a removal reason for a Comment or Submission.

        Note that the removal message is not sent.  This can be done separately
        using :meth:`~.send_removal_message`.

        You can provide no reason if you only want to set mod_note.

        :param reason: The :class:`~.RemovalReason` to use.
        :param mod_note: A private note shown to moderators alongside the
            reason.
        :param other_things: When provided, set the same reason and mod_note on
            this list of :class:`~.Comment` and/or :class:`~.Submission`
            instances as part of a single request (default: None).
        """
        item_ids = [self.thing.fullname]
        if other_things is not None:
            item_ids += [t.fullname for t in other_things]
        data = {'item_ids': item_ids,
                'reason_id': None if reason is None else str(reason),
                'mod_note': mod_note}

        url = API_PATH['removal_reason_set']
        self.thing._reddit._core.request('POST', url, json=data)

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
