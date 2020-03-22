"""Provide the SubmissionModeration class."""
from typing import Optional, TypeVar

from prawcore import Conflict

from ....const import API_PATH
from ..mixins import ThingModerationMixin

_Submission = TypeVar("_Submission")


class SubmissionModeration(ThingModerationMixin):
    """Provide a set of functions pertaining to Submission moderation.

    Example usage:

    .. code-block:: python

       submission = reddit.submission(id="8dmv8z")
       submission.mod.approve()

    """

    REMOVAL_MESSAGE_API = "removal_link_message"

    def __init__(self, submission: _Submission):
        """Create a SubmissionModeration instance.

        :param submission: The submission to moderate.

        """
        self.thing = submission

    def contest_mode(self, state: bool = True):
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

        Example usage:

        .. code-block:: python

           submission = reddit.submission(id='5or86n')
           submission.mod.contest_mode(state=True)

        """
        self.thing._reddit.post(
            API_PATH["contest_mode"],
            data={"id": self.thing.fullname, "state": state},
        )

    def flair(
        self,
        text: str = "",
        css_class: str = "",
        flair_template_id: Optional[str] = None,
    ):
        """Set flair for the submission.

        :param text: The flair text to associate with the Submission (default:
            '').
        :param css_class: The css class to associate with the flair html
            (default: '').
        :param flair_template_id: The flair template id to use when flairing
            (Optional).

        This method can only be used by an authenticated user who is a
        moderator of the Submission's Subreddit.

        Example usage:

        .. code-block:: python

           submission = reddit.submission(id='5or86n')
           submission.mod.flair(text='PRAW', css_class='bot')

        """
        data = {
            "css_class": css_class,
            "link": self.thing.fullname,
            "text": text,
        }
        url = API_PATH["flair"].format(subreddit=self.thing.subreddit)
        if flair_template_id is not None:
            data["flair_template_id"] = flair_template_id
            url = API_PATH["select_flair"].format(
                subreddit=self.thing.subreddit
            )
        self.thing._reddit.post(url, data=data)

    def nsfw(self):
        """Mark as not safe for work.

        This method can be used both by the submission author and moderators of
        the subreddit that the submission belongs to.

        Example usage:

        .. code-block:: python

           submission = reddit.subreddit('test').submit('nsfw test',
                                                        selftext='nsfw')
           submission.mod.nsfw()

        See also :meth:`~.sfw`

        """
        self.thing._reddit.post(
            API_PATH["marknsfw"], data={"id": self.thing.fullname}
        )

    def set_original_content(self):
        """Mark as original content.

        This method can be used by moderators of the subreddit that the
        submission belongs to. If the subreddit has enabled the Original
        Content beta feature in settings, then the submission's author
        can use it as well.

        Example usage:

        .. code-block:: python

           submission = reddit.subreddit('test').submit('oc test',
                                                        selftext='original')
           submission.mod.set_original_content()

        See also :meth:`.unset_original_content`

        """
        data = {
            "id": self.thing.id,
            "fullname": self.thing.fullname,
            "should_set_oc": True,
            "executed": False,
            "r": self.thing.subreddit,
        }
        self.thing._reddit.post(API_PATH["set_original_content"], data=data)

    def sfw(self):
        """Mark as safe for work.

        This method can be used both by the submission author and moderators of
        the subreddit that the submission belongs to.

        Example usage:

        .. code-block:: python

           submission = reddit.submission(id='5or86n')
           submission.mod.sfw()

        See also :meth:`~.nsfw`

        """
        self.thing._reddit.post(
            API_PATH["unmarknsfw"], data={"id": self.thing.fullname}
        )

    def spoiler(self):
        """Indicate that the submission contains spoilers.

        This method can be used both by the submission author and moderators of
        the subreddit that the submission belongs to.

        Example usage:

        .. code-block:: python

           submission = reddit.submission(id='5or86n')
           submission.mod.spoiler()

        See also :meth:`~.unspoiler`

        """
        self.thing._reddit.post(
            API_PATH["spoiler"], data={"id": self.thing.fullname}
        )

    def sticky(
        self, state: bool = True, bottom: bool = True,
    ):
        """Set the submission's sticky state in its subreddit.

        :param state: (boolean) True sets the sticky for the submission, false
            unsets (default: True).
        :param bottom: (boolean) When true, set the submission as the bottom
            sticky. If no top sticky exists, this submission will become the
            top sticky regardless (default: True).

        .. note:: When a submission is stickied two or more times, the Reddit
            API responds with a 409 error that is raises as a ``Conflict`` by
            PRAWCore. The method suppresses these ``Conflict`` errors.

        This submission will replace the second stickied submission if one
        exists.

        For example:

        .. code-block:: python

           submission = reddit.submission(id='5or86n')
           submission.mod.sticky()

        """
        data = {"id": self.thing.fullname, "state": state}
        if not bottom:
            data["num"] = 1
        try:
            return self.thing._reddit.post(
                API_PATH["sticky_submission"], data=data
            )
        except Conflict:
            pass

    def suggested_sort(self, sort: str = "blank"):
        """Set the suggested sort for the comments of the submission.

        :param sort: Can be one of: confidence, top, new, controversial, old,
            random, qa, blank (default: blank).

        """
        self.thing._reddit.post(
            API_PATH["suggested_sort"],
            data={"id": self.thing.fullname, "sort": sort},
        )

    def unset_original_content(self):
        """Indicate that the submission is not original content.

        This method can be used by moderators of the subreddit that the
        submission belongs to. If the subreddit has enabled the Original
        Content beta feature in settings, then the submission's author
        can use it as well.

        Example usage:

        .. code-block:: python

           submission = reddit.subreddit('test').submit('oc test',
                                                        selftext='original')
           submission.mod.unset_original_content()

        See also :meth:`.set_original_content`

        """
        data = {
            "id": self.thing.id,
            "fullname": self.thing.fullname,
            "should_set_oc": False,
            "executed": False,
            "r": self.thing.subreddit,
        }
        self.thing._reddit.post(API_PATH["set_original_content"], data=data)

    def unspoiler(self):
        """Indicate that the submission does not contain spoilers.

        This method can be used both by the submission author and moderators of
        the subreddit that the submission belongs to.

        For example:

        .. code-block:: python

           submission = reddit.subreddit('test').submit('not spoiler',
                                                        selftext='spoiler')
           submission.mod.unspoiler()

        See also :meth:`~.spoiler`

        """
        self.thing._reddit.post(
            API_PATH["unspoiler"], data={"id": self.thing.fullname}
        )
