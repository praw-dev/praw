"""Provide the Flair class."""
from typing import Any, Dict, Optional, TypeVar, Union
from .base import RedditBase

_AdvancedSubmissionFlair = TypeVar("_AdvancedSubmissionFlair")
_LinkFlair = TypeVar("_LinkFlair")
_RedditorFlair = TypeVar("_RedditorFlair")
_RichFlairBase = TypeVar("_RichFlairBase")
Reddit = TypeVar("Reddit")
Submission = TypeVar("Submission")
Subreddit = TypeVar("Subreddit")


class RichFlairBase(RedditBase):
    """A base class for rich flairs.

    Flairs of this type are obtained by either
    :class:`.SubredditLinkFlairTemplates`
    or :class:`.SubredditRedditorFlairTemplates`.

    Subclasses:

        * :class:`.AdvancedSubmissionFlair`
        * :class:`.RedditorFlair`

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

    def __init__(
        self,
        reddit: Reddit,
        subreddit: Subreddit,
        id: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the class.

        :param reddit: An instance of :class:`~.Reddit`.
        :param subreddit: An instance of :class:`~.Subreddit`.
        :param id: The template id of the flair.
        """
        if [id, _data].count(None) != 1:
            raise TypeError("Either ``id`` or ``_data`` needs to be provided.")
        super().__init__(reddit, _data=_data)
        if id is not None:
            self.id = id
        self.subreddit = subreddit
        if not self.subreddit.use_flair_class:
            self.subreddit.use_flair_class = True
        if "create_before_usage" not in self.__dict__:
            self.create_before_usage = False


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

    def __init__(
        self,
        reddit: Reddit,
        subreddit: Subreddit,
        id: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Instantize the class.

        .. warning:: This class should not be directly created. Instead,
            obtain an instance through :class:`.SubredditFlair`.

        :param reddit: An instance of :class:`~.Reddit`.
        :param subreddit: An instance of :class:`~.Subreddit`.
        :param id: The template id of the flair.
        """
        super().__init__(reddit, subreddit, id, _data)


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

    def __init__(
        self,
        reddit: Reddit,
        subreddit: Subreddit,
        id: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Instantize the class.

        .. warning:: This class should not be directly created, but instead
            obtained through :class:`~.SubredditFlair`.

        :param reddit: An instance of :class:`~.Reddit`.
        :param subreddit: An instance of :class:`~.Subreddit`.
        :param id: The template id of the flair.
        """
        super().__init__(reddit, subreddit, id, _data)


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
