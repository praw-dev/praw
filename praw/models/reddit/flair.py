"""Provide the Flair class."""
from typing import Any, Dict, Optional, TypeVar, Union
from .base import RedditBase

_RichFlairBase = TypeVar("_RichFlairBase")
_LinkFlair = TypeVar("_LinkFlair")
Reddit = TypeVar("Reddit")
Submission = TypeVar("Submission")


class RichFlairBase(RedditBase):
    """A base class for rich flairs.

    Flairs of this type are obtained by either
    :class:`.SubredditLinkFlairTemplates`
    or :class:`.SubredditRedditorFlairTemplates`.
    """

    STR_FIELD = "text"

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

    def __init__(self, reddit: Reddit, _data: Dict[str, Any]):
        """Initialize the class."""
        super().__init__(reddit, _data=_data)

    def change_css_class(self, css_class: str):
        """Change the css class of the flair (Mod only).

        :param css_class: The new css class that you want the flair to have.

        .. warning:: This method can only be used by moderators of the
           subreddit.

        """
        self.css_class = css_class

    def change_text(self, text: str):
        """Change the text of the flair.

        :param: The text to replace the default text with.

        .. warning:: This method requires that the flair be editable or the
            authenticated user be a moderator of the subreddit the flair will
            be applied on. To check if a flair is editable, run:

            .. code-block:: python

                flair.text_editable

        """
        self.text = text


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

    def change_css_class(self, css_class: str):
        """
        Change the css class of the flair (Mod only).

        :param css_class: The new css class that you want the flair to have.

        .. warning::

            This method can only be used by moderators of the subreddit.

        For example, to set the flair of a stickied post as a mod post with a
        css class of "mod":

        .. code-block:: python

            submission = reddit.submission("Mod post ID")
            subreddit = reddit.subreddit(str(submission.subreddit),
                                         use_flair_class=True)
            flair = next(iter(subreddit.flair.link_templates))
            flair.change_css_class("mod")
            submission.flair.select(flair=flair)

        """
        super().change_css_class(css_class)

    def change_text(self, text: str):
        """Change the text of the flair.

        :param: The text to replace the default text with.

        .. warning:: This method requires that the flair be editable or the
            authenticated user be a moderator of the subreddit the flair will
            be applied on. To check if a flair is editable, run:

            .. code-block:: python

                flair.text_editable

        For example, to edit the first editable flair to have a flair with the
        text "test", run:

        .. code-block:: python

            submission = reddit.submission("Post ID")
            subreddit = reddit.subreddit(str(submission.subreddit),
                                         use_flair_class=True)
            for flair in subreddit.flair.link_templates:
                if flair.text_editable:
                    break
            flair.change_text("test")

        """
        super().change_text(text)


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

    def change_css_class(self, css_class: str):
        """
        Change the css class of the flair (Mod only).

        :param css_class: The new css class that you want the flair to have.

        .. warning::

            This method can only be used by moderators of the subreddit.

        For example, to give user "spez" the first avaliable flair but give
        it a css class of "admin", you can run:

        .. code-block:: python

            subreddit = reddit.subreddit("NAME", use_flair_class=True)
            flair = next(iter(subreddit.flair.templates))
            flair.change_css_class("admin")
            subreddit.flair.set("spez", flair=flair)

        """
        super().change_css_class(css_class)

    def change_text(self, text: str):
        """Change the text of the flair.

        :param: The text to replace the default text with.

        .. warning:: This method requires that the flair be editable or the
            authenticated user be a moderator of the subreddit the flair will
            be applied on. To check if a flair is editable, run:

            .. code-block:: python

                flair.text_editable

        For example, to edit the first editable flair to have a flair with the
        text "test", run:

        .. code-block:: python

            subreddit = reddit.subreddit("NAME", use_flair_class=True)
            for flair in subreddit.flair.templates:
                if flair.text_editable:
                    break
            flair.change_text("test")

        """
        super().change_text(text)


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

    def __init__(self, reddit: Reddit, _data: Dict[str, Any]):
        """Instantizes the flair object."""
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
        self, submission: Submission
    ) -> Optional[AdvancedSubmissionFlair]:
        """Allow a user to find more info about the flair.

        When given a submission, the method will scan the subreddit the
        submission is in until it finds a matching
        :class:`.AdvancedSubmissionFlair` or returns nothing

        :param submission: The submission that return the flair
        :returns: The :class:`.AdvancedSubmissionFlair` if it could find it,
            otherwise None

        """
        display_name = submission.subreddit.display_name
        for flair in self._reddit.subreddit(
            display_name, use_flair_class=True
        ).flair.link_templates:
            if flair.id == self.flair_template_id:
                return flair
