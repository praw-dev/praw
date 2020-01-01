"""A file providing the helper class for creating Flairs.

This is not included in :mod:`.helpers` because it is imported by
:mod`.reddit.subreddit` and therefore would cause import errors.
"""
from typing import TypeVar

from .base import PRAWBase
from .reddit.flair import AdvancedSubmissionFlair, RedditorFlair

Subreddit = TypeVar("Subreddit")


class FlairHelper(PRAWBase):
    """Provide a set of functions to create subreddit-specific flairs.

    This helper should not be created directly, but obtained from an instance
    of :class:`.Subreddit`.
    """

    def __init__(self, subreddit: Subreddit):
        """Initialize an instance of :class:`.FlairHelper`."""
        super().__init__(subreddit._reddit, None)
        self.subreddit = subreddit

    def make_link_flair(
        self,
        text: str,
        css_class: str = "",
        text_editable: bool = False,
        background_color: str = "transparent",
        text_color: str = "dark",
        mod_only: bool = False,
        allowable_content: str = "all",
        max_emojis: str = 10,
    ) -> AdvancedSubmissionFlair:
        r"""Make an instance of :class:`.AdvancedSubmissionFlair`.

        This is a lazy instance, and it is only meant to be used with
        :meth:`.SubredditLinkFlairTemplates.add`.

        :param text: The flair template's text (required).
        :param css_class: The flair template's css_class (default: '').

        .. warning:: Reddit will not accept a css_class containing any
            characters in the character set
            ``!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~``.

        :param text_editable: (boolean) Indicate if the flair text can be
            modified for each Redditor that sets it (default: False).
        :param background_color: The flair template's new background color,
            as a hex color.
        :param text_color: The flair template's new text color, either
            ``'light'`` or ``'dark'``.
        :param mod_only: (boolean) Indicate if the flair can only be used by
            moderators.
        :param allowable_content: If specified, most be one of ``'all'``,
            ``'emoji'``, or ``'text'`` to restrict content to that type.
            If set to ``'emoji'`` then the ``'text'`` param must be a
            valid emoji string, for example ``':snoo:'``.
        :param max_emojis: (int) Maximum emojis in the flair
            (Reddit defaults this value to 10).
        """
        return AdvancedSubmissionFlair.make_new_flair(
            self._reddit,
            self.subreddit,
            text=text,
            css_class=css_class,
            text_editable=text_editable,
            background_color=background_color,
            text_color=text_color,
            mod_only=mod_only,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    def make_user_flair(
        self,
        text: str,
        css_class: str = "",
        text_editable: bool = False,
        background_color: str = "transparent",
        text_color: str = "dark",
        mod_only: bool = False,
        allowable_content: str = "all",
        max_emojis: str = 10,
    ) -> RedditorFlair:
        r"""Make an instance of :class:`.RedditorFlair`.

        This is a lazy instance, and it is only meant to be used with
        :meth:`.SubredditRedditorFlairTemplates.add`.

        :param text: The flair template's text (required).
        :param css_class: The flair template's css_class (default: '').

        .. warning:: Reddit will not accept a css_class containing any
            characters in the character set
            ``!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~``.


        :param text_editable: (boolean) Indicate if the flair text can be
            modified for each Redditor that sets it (default: False).
        :param background_color: The flair template's new background color,
            as a hex color.
        :param text_color: The flair template's new text color, either
            ``'light'`` or ``'dark'``.
        :param mod_only: (boolean) Indicate if the flair can only be used by
            moderators.
        :param allowable_content: If specified, most be one of ``'all'``,
            ``'emoji'``, or ``'text'`` to restrict content to that type.
            If set to ``'emoji'`` then the ``'text'`` param must be a
            valid emoji string, for example ``':snoo:'``.
        :param max_emojis: (int) Maximum emojis in the flair
            (Reddit defaults this value to 10).
        """
        return RedditorFlair.make_new_flair(
            self._reddit,
            self.subreddit,
            text,
            css_class=css_class,
            text_editable=text_editable,
            background_color=background_color,
            text_color=text_color,
            mod_only=mod_only,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )
