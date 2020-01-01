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
    """

    STR_FIELD = "text"

    @classmethod
    def make_new_flair(
        cls,
        reddit: Reddit,
        subreddit: Subreddit,
        text: str,
        css_class: str = "",
        text_editable: bool = False,
        background_color: str = "transparent",
        text_color: str = "dark",
        mod_only: bool = False,
        allowable_content: str = "all",
        max_emojis: str = 10,
        create_before_usage: bool = False,
    ) -> _RichFlairBase:
        r"""Make a new flair instance. Useful for adding new flair templates.

        .. note:: This method should only be called from an instance of
           :class:`.FlairHelper`.

        :param reddit: An instance of :class:`~.Reddit`.
        :param subreddit: An instance of :class:`~.Subreddit`.
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
        :param create_before_usage: If the flair does not exist and is being
            used to flair a submission or redditor, it will automatically
            create the flair and obtain the flair ID before flairing the
            submission or redditor (Mod only)(Default: False).
        """
        return cls(
            reddit,
            subreddit,
            dict(
                text=text,
                css_class=css_class,
                text_editable=text_editable,
                background_color=background_color,
                text_color=text_color,
                mod_only=mod_only,
                allowable_content=allowable_content,
                max_emojis=max_emojis,
                create_before_usage=create_before_usage,
            ),
        )

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
        if not self.subreddit.use_flair_class:
            self.subreddit.use_flair_class = True
        if "create_before_usage" not in self.__dict__:
            self.create_before_usage = False

    def change_info(self, **new_values: Union[str, int, bool]):
        r"""Update the values of the flair instance.

        .. warning:: Most values, except text, can only be updated by a
            moderator who has the ``flair`` permission. Text can only be
            updated if the flair is editable. To check if a flair is editable,
            run:

            .. code-block:: python

                flair.text_editable

        :param text: The flair template's new text
        :param css_class: The flair template's new css class. (Mod only)

        .. warning:: Reddit will not accept a css_class containing any
            characters in the character set
            ``!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~``.

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

    @classmethod
    def make_new_flair(
        cls,
        reddit: Reddit,
        subreddit: Subreddit,
        text: str,
        css_class: str = "",
        text_editable: bool = False,
        background_color: str = "transparent",
        text_color: str = "dark",
        mod_only: bool = False,
        allowable_content: str = "all",
        max_emojis: str = 10,
        create_before_usage: bool = False,
    ) -> _AdvancedSubmissionFlair:
        r"""Make a new flair instance. Useful for adding new flair templates.

        .. note:: This method should only be called from
           :meth:`.FlairHelper.make_link_flair`.

        :param reddit: An instance of :class:`~.Reddit`.
        :param subreddit: An instance of :class:`~.Subreddit`.
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
        :param create_before_usage: If the flair does not exist and is being
            used to flair a submission or redditor, it will automatically
            create the flair and obtain the flair ID before flairing the
            submission or redditor (Mod only)(Default: False).
        """
        return super().make_new_flair(
            reddit,
            subreddit,
            text,
            css_class,
            text_editable,
            background_color,
            text_color,
            mod_only,
            allowable_content,
            max_emojis,
            create_before_usage,
        )

    def change_info(self, **new_values: Union[str, int, bool]):
        r"""Update the values of the flair instance.

        .. warning:: Most values, except text, can only be updated by a
            moderator who has the ``flair`` permission. Text can only be
            updated if the flair is editable. To check if a flair is editable,
            run:

            .. code-block:: python

                flair.text_editable

        :param text: The flair template's new text
        :param css_class: The flair template's new css class. (Mod only)

        .. warning:: Reddit will not accept a css_class containing any
            characters in the character set
            ``!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~``.

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
        super().change_info(**new_values)

    def _make_in_subreddit(self):
        self.subreddit.flair.link_templates.add(flair=self)
        self._fetch(_called_from_inner_method=True)

    def _fetch(self, _called_from_inner_method=False):
        if not _called_from_inner_method:
            if self.create_before_usage and "id" not in self.__dict__:
                self._make_in_subreddit()
        if (
            len(
                [
                    True
                    for attr in (
                        "allowable_content",
                        "text",
                        "text_color",
                        "mod_only",
                        "background_color",
                        "id",
                        "css_class",
                        "max_emojis",
                        "text_editable",
                        "id",
                    )
                    if attr in self.__dict__
                ]
            )
            == 10
        ):
            self._fetched = True
        else:
            if "id" in self.__dict__:
                for template in self.subreddit.flair.link_templates:
                    if self.id == template.id:
                        self.__dict__ = template.__dict__
                        break
            else:
                for template in self.subreddit.flair.link_templates:
                    if (
                        self.allowable_content,
                        self.text,
                        self.text_color,
                        self.mod_only,
                        self.background_color,
                        self.css_class,
                        self.max_emojis,
                        self.text_editable,
                    ) == (
                        template.allowable_content,
                        template.text,
                        template.text_color,
                        template.mod_only,
                        template.background_color,
                        template.css_class,
                        template.max_emojis,
                        template.text_editable,
                    ):
                        self.__dict__ = template.__dict__
                        break
            super()._fetch()


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

    @classmethod
    def make_new_flair(
        cls,
        reddit: Reddit,
        subreddit: Subreddit,
        text: str,
        css_class: str = "",
        text_editable: bool = False,
        background_color: str = "transparent",
        text_color: str = "dark",
        mod_only: bool = False,
        allowable_content: str = "all",
        max_emojis: str = 10,
        create_before_usage: bool = False,
    ) -> _AdvancedSubmissionFlair:
        r"""Make a new flair instance. Useful for adding new flair templates.

        .. note:: This method should only be called from
           :meth:`.FlairHelper.make_link_flair`.

        :param reddit: An instance of :class:`~.Reddit`.
        :param subreddit: An instance of :class:`~.Subreddit`.
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
        :param create_before_usage: If the flair does not exist and is being
            used to flair a submission or redditor, it will automatically
            create the flair and obtain the flair ID before flairing the
            submission or redditor (Mod only)(Default: False).
        """
        return super().make_new_flair(
            reddit,
            subreddit,
            text,
            css_class,
            text_editable,
            background_color,
            text_color,
            mod_only,
            allowable_content,
            max_emojis,
            create_before_usage,
        )

    def change_info(self, **new_values: Union[str, int, bool]):
        r"""Update the values of the flair instance.

        .. warning:: Most values, except text, can only be updated by a
            moderator who has the ``flair`` permission. Text can only be
            updated if the flair is editable. To check if a flair is editable,
            run:

            .. code-block:: python

                flair.text_editable

        :param text: The flair template's new text
        :param css_class: The flair template's new css class. (Mod only)

        .. warning:: Reddit will not accept a css_class containing any
            characters in the character set
            ``!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~``.


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
        super().change_info(**new_values)

    def _make_in_subreddit(self):
        self.subreddit.flair.templates.add(flair=self)
        self._fetch(_called_from_inner_method=True)

    def _fetch(self, _called_from_inner_method=False):
        if not _called_from_inner_method:
            if self.create_before_usage and "id" not in self.__dict__:
                self._make_in_subreddit()
        if (
            len(
                [
                    True
                    for attr in (
                        "allowable_content",
                        "text",
                        "text_color",
                        "mod_only",
                        "background_color",
                        "id",
                        "css_class",
                        "max_emojis",
                        "text_editable",
                        "id",
                    )
                    if attr in self.__dict__
                ]
            )
            == 10
        ):
            self._fetched = True
        else:
            if "id" in self.__dict__:
                for template in self.subreddit.flair.templates:
                    if self.id == template.id:
                        self.__dict__ = template.__dict__
                        break
            else:
                for template in self.subreddit.flair.templates:
                    if (
                        self.allowable_content,
                        self.text,
                        self.text_color,
                        self.mod_only,
                        self.background_color,
                        self.css_class,
                        self.max_emojis,
                        self.text_editable,
                    ) == (
                        template.allowable_content,
                        template.text,
                        template.text_color,
                        template.mod_only,
                        template.background_color,
                        template.css_class,
                        template.max_emojis,
                        template.text_editable,
                    ):
                        self.__dict__ = template.__dict__
                        break
            super()._fetch()


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
