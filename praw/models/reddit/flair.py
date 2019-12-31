"""Provide the Flair class."""
from typing import Any, Dict, Optional, TypeVar, Union
from .base import RedditBase

_RichFlairBase = TypeVar("_RichFlairBase")
_LinkFlair = TypeVar("_LinkFlair")
Reddit = TypeVar("Reddit")
Submission = TypeVar("Submission")
Subreddit = TypeVar("Subreddit")


class RichFlairBase(RedditBase):
    """A base class for rich flairs.

    Flairs of this type are obtained by either
    :class:`.SubredditLinkFlairTemplates`
    or :class:`.SubredditRedditorFlairTemplates`.
    """

    STR_FIELD = "text"

    @classmethod
    def make_new_flair(
        cls,
        reddit,
        text=None,
        css_class=None,
        text_editable=False,
        background_color=None,
        text_color=None,
        mod_only=None,
        allowable_content=None,
        max_emojis=None,
    ):
        """Make a new flair instance. Useful for adding new flair templates."""

    def __eq__(self, other: Union[str, _RichFlairBase]) -> bool:
        """Check that two instances of the class are equal."""
        if isinstance(other, str):
            return str(self) == other
        return (
            isinstance(other, self.__class__)
            and str(self) == str(other)
            and self.id == other.id
            and self.css_class == other.css_class
        )

    def __hash__(self) -> int:
        """Get the hash of the instance."""
        return (
            hash(self.__class__.__name__)
            ^ hash(str(self))
            ^ hash(self.id)
            ^ hash(self.css_class)
        )

    def __init__(
        self, reddit: Reddit, subreddit: Subreddit, _data: Dict[str, Any]
    ):
        """Initialize the class."""
        super().__init__(reddit, _data=_data)
        self.subreddit = subreddit

    def change_info(self, **new_values: Union[str, int, bool]):
        """Update the values of the flair instance.

        .. warning:: Most values, except text, can only be updated by a
            moderator who has the ``flair`` permission. Text can only be
            updated if the flair is editable. To check if a flair is editable,
            run:

            .. code-block:: python

                flair.text_editable

        :param text: The flair template's new text
        :param css_class: The flair template's new css class. (Mod only)
        :param text_editable: (boolean) Indicate if the flair text can be
            modified for each Redditor that sets it. (Mod only)
        :param background_color: The flair template's new background color,
            as a hex color (``#XXXXXX``). This should be inputted as
            ``0x------``, where the 6 ``-`` correspond to the 6 digits of an
            RGB hex. (Mod only)
        :param text_color: The flair template's new text color, either
            ``'light'`` or ``'dark'``. (Mod only)
        :param mod_only: (boolean) Indicate if the flair can only be used by
            moderators. (Mod only)
        :param allowable_content: If specified, most be one of ``'all'``,
            ``'emoji'``, or ``'text'`` to restrict content to that type.
            If set to ``'emoji'`` then the ``'text'`` param must be a
            valid emoji string, for example ``':snoo:'``. (Mod only)
        :param max_emojis: (int) Maximum emojis in the flair. (Mod only)

        To change just the text of an editable flair, run:

        .. code-block:: python

            if flair.text_editable:
                flair.change_info(text="New text")

        To change the flair into a mod-only flair that has a white background
        and dark text, run:

        .. code-block:: python

            flair.change_info(mod_only=True,
                              background_color=,0xffffff # White is FFFFFF
                              text_color="dark"
                              )

        To make a flair's text editable by anyone, run:

        ..code-block:: python

            flair.change_info(text_editable=True)

        """
        for attribute, new_value in new_values.items():
            setattr(self, attribute, new_value)


class AdvancedSubmissionFlair(RichFlairBase):
    """A special submission flair that contains more details.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``allowable_content``   The type of content allowed in the flair (
                            acceptable values are ``all``, ``emoji`` or
                            ``text``).
    ``background_color``    The background color of the flair. Values can be a
                            color name (``dark`` or a 6-digit RGB code
                            ``#ffffff``.)
    ``css_class``           The css class of the flair.
    ``id``                  The flair template id.
    ``max_emojis``          The amount of :class:`.Emoji` that can go in the
                            flair.
    ``mod_only``            Whether or not the flair is mod only or not.
    ``richtext``            A list containing data about any richtext elements,
                            including any emojis, present in the flair.
    ``text``                The text of the flair.
    ``text_color``          The color of the text
    ``text_editable``       Whether or not the flair text can be edited.
    ``type``                The type of the flair (``text`` or ``richtext``.)
    ======================= ===================================================
    """


class RedditorFlair(RichFlairBase):
    """An individual RedditorFlair object.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``allowable_content``   The type of content allowed in the flair (
                            acceptable values are ``all``, ``emoji`` or
                            ``text``).
    ``background_color``    The background color of the flair. Values can be a
                            color name (``dark`` or a 6-digit RGB code
                            ``#ffffff``.)
    ``css_class``           The css class of the flair.
    ``id``                  The flair template id.
    ``max_emojis``          The amount of :class:`.Emoji` that can go in the
                            flair.
    ``mod_only``            Whether or not the flair is mod only or not.
    ``richtext``            A list containing data about any richtext elements,
                            including any emojis, present in the flair.
    ``text``                The text of the flair.
    ``text_color``          The color of the text
    ``text_editable``       Whether or not the flair text can be edited.
    ``type``                The type of the flair (``text`` or ``richtext``.)
    ======================= ===================================================

    """


class LinkFlair(RedditBase):
    """An individual LinkFlair object.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``flair_template_id``   The id of the flair template.
    ``flair_text_editable`` Whether or not the flair text can be edited.
    ``flair_text``          The text of the flair
    ======================= ===================================================
    """

    STR_FIELD = "flair_text"

    def __eq__(self, other: Union[str, _LinkFlair]) -> bool:
        """Check that two flairs are the same flair."""
        if isinstance(other, str):
            return str(self) == other
        return (
            isinstance(other, self.__class__)
            and str(self) == str(other)
            and self.flair_template_id == other.flair_template_id
        )

    def __hash__(self) -> int:
        """Return the hash of the flair."""
        return (
            hash(self.__class__.__name__)
            ^ hash(str(self))
            ^ hash(self.flair_template_id)
        )

    def __init__(
        self, reddit: Reddit, submission: Submission, _data: Dict[str, Any]
    ):
        """Instantizes the flair object."""
        self.submission = submission
        super().__init__(reddit, _data=_data)

    def change_text(self, text: str):
        """Change the text of the flair.

        :param: The text to replace the default text with.

        .. warning:: This method requires that the flair be editable or the
            authenticated user be a moderator of the subreddit the flair will
            be applied on. To check if a flair is editable, run:

            .. code-block:: python

                flair.flair_text_editable

        For example, to edit the first editable flair to have a flair with the
        text "test", run:

        .. code-block:: python

            submission = reddit.submission("Post ID")
            for flair in subreddit.flair.choices():
                if flair.flair_text_editable:
                    break
            flair.change_text("test")

        """
        self.flair_text = text

    def find_advanced_flair_template(
        self,
    ) -> Optional[AdvancedSubmissionFlair]:
        """Allow a user to find more info about the flair.

        The method will scan the subreddit the flair belongs to and either
        return :class:`.AdvancedSubmissionFlair` or None if no flair is found

        :returns: The :class:`.AdvancedSubmissionFlair` if it could find it,
            otherwise None

        """
        display_name = self.submission.subreddit.display_name
        for flair in self._reddit.subreddit(
            display_name, use_flair_class=True
        ).flair.link_templates:
            if flair.id == self.flair_template_id:
                return flair
