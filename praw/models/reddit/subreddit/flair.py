"""Provide the SubredditFlairTemplates class."""

from __future__ import annotations

from csv import writer
from io import StringIO
from typing import TYPE_CHECKING, Any, cast

from praw.const import API_PATH
from praw.exceptions import InvalidFlairTemplateID
from praw.models.listing.generator import ListingGenerator
from praw.models.reddit.base import RedditBase
from praw.util import cachedproperty

if TYPE_CHECKING:
    from collections.abc import Iterator

    from praw import models


class SubredditFlair:
    """Provide a set of functions to interact with a :class:`.Subreddit`'s flair."""

    @cachedproperty
    def link_templates(
        self,
    ) -> SubredditLinkFlairTemplates:
        """Provide an instance of :class:`.SubredditLinkFlairTemplates`.

        Use this attribute for interacting with a :class:`.Subreddit`'s link flair
        templates. For example to list all the link flair templates for a subreddit
        which you have the ``flair`` moderator permission on try:

        .. code-block:: python

            for template in reddit.subreddit("test").flair.link_templates:
                print(template)

        """
        return SubredditLinkFlairTemplates(self.subreddit)

    @cachedproperty
    def templates(
        self,
    ) -> SubredditRedditorFlairTemplates:
        """Provide an instance of :class:`.SubredditRedditorFlairTemplates`.

        Use this attribute for interacting with a :class:`.Subreddit`'s flair templates.
        For example to list all the flair templates for a subreddit which you have the
        ``flair`` moderator permission on try:

        .. code-block:: python

            for template in reddit.subreddit("test").flair.templates:
                print(template)

        """
        return SubredditRedditorFlairTemplates(self.subreddit)

    def __call__(
        self,
        redditor: models.Redditor | str | None = None,
        **generator_kwargs: Any,
    ) -> Iterator[models.Redditor]:
        """Return a :class:`.ListingGenerator` for Redditors and their flairs.

        :param redditor: When provided, yield at most a single :class:`.Redditor`
            instance (default: ``None``).

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        Usage:

        .. code-block:: python

            for flair in reddit.subreddit("test").flair(limit=None):
                print(flair)

        """
        RedditBase._safely_add_arguments(arguments=generator_kwargs, key="params", name=redditor)
        generator_kwargs.setdefault("limit", None)
        url = API_PATH["flairlist"].format(subreddit=self.subreddit)
        return ListingGenerator(self.subreddit._reddit, url, **generator_kwargs)

    def __init__(self, subreddit: models.Subreddit) -> None:
        """Initialize a :class:`.SubredditFlair` instance.

        :param subreddit: The subreddit whose flair to work with.

        """
        self.subreddit = subreddit

    def configure(
        self,
        *,
        link_position: str = "left",
        link_self_assign: bool = False,
        position: str = "right",
        self_assign: bool = False,
        **settings: Any,
    ) -> None:
        """Update the :class:`.Subreddit`'s flair configuration.

        :param link_position: One of ``"left"``, ``"right"``, or ``False`` to disable
            (default: ``"left"``).
        :param link_self_assign: Permit self assignment of link flair (default:
            ``False``).
        :param position: One of ``"left"``, ``"right"``, or ``False`` to disable
            (default: ``"right"``).
        :param self_assign: Permit self assignment of user flair (default: ``False``).

        .. code-block:: python

            subreddit = reddit.subreddit("test")
            subreddit.flair.configure(link_position="right", self_assign=True)

        Additional keyword arguments can be provided to handle new settings as Reddit
        introduces them.

        """
        data = {
            "flair_enabled": bool(position),
            "flair_position": position or "right",
            "flair_self_assign_enabled": self_assign,
            "link_flair_position": link_position or "",
            "link_flair_self_assign_enabled": link_self_assign,
        }
        data.update(settings)
        url = API_PATH["flairconfig"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def delete(self, redditor: models.Redditor | str) -> None:
        """Delete flair for a :class:`.Redditor`.

        :param redditor: A redditor name or :class:`.Redditor` instance.

        .. seealso::

            :meth:`~.SubredditFlair.update` to delete the flair of many redditors at
            once.

        """
        url = API_PATH["deleteflair"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data={"name": str(redditor)})

    def delete_all(self) -> list[dict[str, str | bool | dict[str, str]]]:
        """Delete all :class:`.Redditor` flair in the :class:`.Subreddit`.

        :returns: List of dictionaries indicating the success or failure of each delete.

        """
        return self.update(cast("dict[str, str | models.Redditor]", x)["user"] for x in self())

    def set(
        self,
        redditor: models.Redditor | str,
        *,
        css_class: str = "",
        flair_template_id: str | None = None,
        text: str = "",
    ) -> None:
        """Set flair for a :class:`.Redditor`.

        :param redditor: A redditor name or :class:`.Redditor` instance.
        :param text: The flair text to associate with the :class:`.Redditor` or
            :class:`.Submission` (default: ``""``).
        :param css_class: The css class to associate with the flair html (default:
            ``""``). Use either this or ``flair_template_id``.
        :param flair_template_id: The ID of the flair template to be used (default:
            ``None``). Use either this or ``css_class``.

        This method can only be used by an authenticated user who is a moderator of the
        associated :class:`.Subreddit`.

        For example:

        .. code-block:: python

            reddit.subreddit("test").flair.set("bboe", text="PRAW author", css_class="mods")
            template = "6bd28436-1aa7-11e9-9902-0e05ab0fad46"
            reddit.subreddit("test").flair.set(
                "spez", text="Reddit CEO", flair_template_id=template
            )

        """
        if css_class and flair_template_id is not None:
            msg = "Parameter 'css_class' cannot be used in conjunction with 'flair_template_id'."
            raise TypeError(msg)
        data = {"name": str(redditor), "text": text}
        if flair_template_id is not None:
            data["flair_template_id"] = flair_template_id
            url = API_PATH["select_flair"].format(subreddit=self.subreddit)
        else:
            data["css_class"] = css_class
            url = API_PATH["flair"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def update(
        self,
        flair_list: Iterator[str | models.Redditor | dict[str, str | models.Redditor]],
        *,
        css_class: str = "",
        text: str = "",
    ) -> list[dict[str, str | bool | dict[str, str]]]:
        """Set or clear the flair for many redditors at once.

        :param flair_list: Each item in this list should be either:

            - The name of a redditor.
            - An instance of :class:`.Redditor`.
            - A dictionary mapping keys ``"user"``, ``"flair_text"``, and
              ``"flair_css_class"`` to their respective values. The ``"user"`` key
              should map to a redditor, as described above. When a dictionary isn't
              provided, or the dictionary is missing either ``"flair_text"`` or
              ``"flair_css_class"`` keys, the default values will come from the other
              arguments.
        :param css_class: The css class to use when not explicitly provided in
            ``flair_list`` (default: ``""``).
        :param text: The flair text to use when not explicitly provided in
            ``flair_list`` (default: ``""``).

        :returns: List of dictionaries indicating the success or failure of each update.

        For example, to clear the flair text, and set the ``"praw"`` flair css class on
        a few users try:

        .. code-block:: python

            subreddit.flair.update(["bboe", "spez", "spladug"], css_class="praw")

        """
        temp_lines = StringIO()
        for item in flair_list:
            if isinstance(item, dict):
                writer(temp_lines).writerow([
                    str(item["user"]),
                    item.get("flair_text", text),
                    item.get("flair_css_class", css_class),
                ])
            else:
                writer(temp_lines).writerow([str(item), text, css_class])

        lines = temp_lines.getvalue().splitlines()
        temp_lines.close()
        response = []
        url = API_PATH["flaircsv"].format(subreddit=self.subreddit)
        while lines:
            data = {"flair_csv": "\n".join(lines[:100])}
            response.extend(self.subreddit._reddit.post(url, data=data))
            lines = lines[100:]
        return response


class SubredditFlairTemplates:
    """Provide functions to interact with a :class:`.Subreddit`'s flair templates."""

    @staticmethod
    def flair_type(*, is_link: bool | None) -> str:
        """Return ``"LINK_FLAIR"`` or ``"USER_FLAIR"`` depending on ``is_link`` value."""
        return "LINK_FLAIR" if is_link else "USER_FLAIR"

    def __init__(self, subreddit: models.Subreddit) -> None:
        """Initialize a :class:`.SubredditFlairTemplates` instance.

        :param subreddit: The subreddit whose flair templates to work with.

        .. note::

            This class should not be initialized directly. Instead, obtain an instance
            via: ``reddit.subreddit("test").flair.templates`` or
            ``reddit.subreddit("test").flair.link_templates``.

        """
        self.subreddit = subreddit

    def __iter__(self) -> Iterator[dict[str, str | int | bool | list[dict[str, str]]]]:
        """Abstract method to return flair templates."""
        raise NotImplementedError

    def _add(
        self,
        *,
        allowable_content: str | None = None,
        background_color: str | None = None,
        css_class: str = "",
        is_link: bool | None = None,
        max_emojis: int | None = None,
        mod_only: bool | None = None,
        text: str,
        text_color: str | None = None,
        text_editable: bool = False,
    ) -> None:
        url = API_PATH["flairtemplate_v2"].format(subreddit=self.subreddit)
        data = {
            "allowable_content": allowable_content,
            "background_color": background_color,
            "css_class": css_class,
            "flair_type": self.flair_type(is_link=is_link),
            "max_emojis": max_emojis,
            "mod_only": bool(mod_only),
            "text": text,
            "text_color": text_color,
            "text_editable": bool(text_editable),
        }
        self.subreddit._reddit.post(url, data=data)

    def _clear(self, *, is_link: bool | None = None) -> None:
        url = API_PATH["flairtemplateclear"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data={"flair_type": self.flair_type(is_link=is_link)})

    def _reorder(self, flair_list: list, *, is_link: bool | None = None) -> None:
        url = API_PATH["flairtemplatereorder"].format(subreddit=self.subreddit)
        self.subreddit._reddit.patch(
            url,
            json=flair_list,
            params={
                "flair_type": self.flair_type(is_link=is_link),
                "subreddit": self.subreddit.display_name,
            },
        )

    def delete(self, template_id: str) -> None:
        """Remove a flair template provided by ``template_id``.

        For example, to delete the first :class:`.Redditor` flair template listed, try:

        .. code-block:: python

            template_info = list(subreddit.flair.templates)[0]
            subreddit.flair.templates.delete(template_info["id"])

        """
        url = API_PATH["flairtemplatedelete"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data={"flair_template_id": template_id})

    def update(
        self,
        template_id: str,
        *,
        allowable_content: str | None = None,
        background_color: str | None = None,
        css_class: str | None = None,
        fetch: bool = True,
        max_emojis: int | None = None,
        mod_only: bool | None = None,
        text: str | None = None,
        text_color: str | None = None,
        text_editable: bool | None = None,
    ) -> None:
        """Update the flair template provided by ``template_id``.

        :param template_id: The flair template to update. If not valid then an exception
            will be thrown.
        :param allowable_content: If specified, most be one of ``"all"``, ``"emoji"``,
            or ``"text"`` to restrict content to that type. If set to ``"emoji"`` then
            the ``"text"`` param must be a valid emoji string, for example,
            ``":snoo:"``.
        :param background_color: The flair template's new background color, as a hex
            color.
        :param css_class: The flair template's new css_class (default: ``""``).
        :param fetch: Whether PRAW will fetch existing information on the existing flair
            before updating (default: ``True``).
        :param max_emojis: Maximum emojis in the flair (Reddit defaults this value to
            ``10``).
        :param mod_only: Indicate if the flair can only be used by moderators.
        :param text: The flair template's new text.
        :param text_color: The flair template's new text color, either ``"light"`` or
            ``"dark"``.
        :param text_editable: Indicate if the flair text can be modified for each
            redditor that sets it (default: ``False``).

        .. warning::

            If parameter ``fetch`` is set to ``False``, all parameters not provided will
            be reset to their default (``None`` or ``False``) values.

        For example, to make a user flair template text editable, try:

        .. code-block:: python

            template_info = list(subreddit.flair.templates)[0]
            subreddit.flair.templates.update(
                template_info["id"],
                text=template_info["flair_text"],
                text_editable=True,
            )

        """
        url = API_PATH["flairtemplate_v2"].format(subreddit=self.subreddit)
        data = {
            "allowable_content": allowable_content,
            "background_color": background_color,
            "css_class": css_class,
            "flair_template_id": template_id,
            "max_emojis": max_emojis,
            "mod_only": mod_only,
            "text": text,
            "text_color": text_color,
            "text_editable": text_editable,
        }
        if fetch:
            existing_data_ = [template for template in iter(self) if template["id"] == template_id]
            if len(existing_data_) != 1:
                raise InvalidFlairTemplateID(template_id)
            existing_data = existing_data_[0]
            for key, value in existing_data.items():
                if data.get(key) is None:
                    data[key] = value
        self.subreddit._reddit.post(url, data=data)


class SubredditLinkFlairTemplates(SubredditFlairTemplates):
    """Provide functions to interact with link flair templates."""

    def __iter__(
        self,
    ) -> Iterator[dict[str, str | int | bool | list[dict[str, str]]]]:
        """Iterate through the link flair templates as a moderator.

        For example:

        .. code-block:: python

            for template in reddit.subreddit("test").flair.link_templates:
                print(template)

        """
        url = API_PATH["link_flair"].format(subreddit=self.subreddit)
        yield from self.subreddit._reddit.get(url)

    def add(
        self,
        text: str,
        *,
        allowable_content: str | None = None,
        background_color: str | None = None,
        css_class: str = "",
        max_emojis: int | None = None,
        mod_only: bool | None = None,
        text_color: str | None = None,
        text_editable: bool = False,
    ) -> None:
        """Add a link flair template to the associated subreddit.

        :param text: The flair template's text.
        :param allowable_content: If specified, most be one of ``"all"``, ``"emoji"``,
            or ``"text"`` to restrict content to that type. If set to ``"emoji"`` then
            the ``"text"`` param must be a valid emoji string, for example,
            ``":snoo:"``.
        :param background_color: The flair template's new background color, as a hex
            color.
        :param css_class: The flair template's css_class (default: ``""``).
        :param max_emojis: Maximum emojis in the flair (Reddit defaults this value to
            ``10``).
        :param mod_only: Indicate if the flair can only be used by moderators.
        :param text_color: The flair template's new text color, either ``"light"`` or
            ``"dark"``.
        :param text_editable: Indicate if the flair text can be modified for each
            redditor that sets it (default: ``False``).

        For example, to add an editable link flair try:

        .. code-block:: python

            reddit.subreddit("test").flair.link_templates.add(
                "PRAW",
                css_class="praw",
                text_editable=True,
            )

        """
        self._add(
            allowable_content=allowable_content,
            background_color=background_color,
            css_class=css_class,
            is_link=True,
            max_emojis=max_emojis,
            mod_only=mod_only,
            text=text,
            text_color=text_color,
            text_editable=text_editable,
        )

    def clear(self) -> None:
        """Remove all link flair templates from the subreddit.

        For example:

        .. code-block:: python

            reddit.subreddit("test").flair.link_templates.clear()

        """
        self._clear(is_link=True)

    def reorder(self, flair_list: list[str]) -> None:
        """Reorder a list of flairs.

        :param flair_list: A list of flair IDs.

        For example, to reverse the order of the link flair list try:

        .. code-block:: python

            subreddit = reddit.subreddit("test")
            flairs = [flair["id"] for flair in subreddit.flair.link_templates]
            subreddit.flair.link_templates.reorder(list(reversed(flairs)))

        """
        self._reorder(flair_list, is_link=True)

    def user_selectable(
        self,
    ) -> Iterator[dict[str, str | bool]]:
        """Iterate through the link flair templates as a regular user.

        For example:

        .. code-block:: python

            for template in reddit.subreddit("test").flair.link_templates.user_selectable():
                print(template)

        """
        url = API_PATH["flairselector"].format(subreddit=self.subreddit)
        yield from self.subreddit._reddit.post(url, data={"is_newlink": True})["choices"]


class SubredditRedditorFlairTemplates(SubredditFlairTemplates):
    """Provide functions to interact with :class:`.Redditor` flair templates."""

    def __iter__(
        self,
    ) -> Iterator[dict[str, str | int | bool | list[dict[str, str]]]]:
        """Iterate through the user flair templates.

        For example:

        .. code-block:: python

            for template in reddit.subreddit("test").flair.templates:
                print(template)

        """
        url = API_PATH["user_flair"].format(subreddit=self.subreddit)
        params: dict[str, str | int] = {"unique": self.subreddit._reddit._next_unique}
        yield from self.subreddit._reddit.get(url, params=params)

    def add(
        self,
        text: str,
        *,
        allowable_content: str | None = None,
        background_color: str | None = None,
        css_class: str = "",
        max_emojis: int | None = None,
        mod_only: bool | None = None,
        text_color: str | None = None,
        text_editable: bool = False,
    ) -> None:
        """Add a redditor flair template to the associated subreddit.

        :param text: The flair template's text.
        :param allowable_content: If specified, most be one of ``"all"``, ``"emoji"``,
            or ``"text"`` to restrict content to that type. If set to ``"emoji"`` then
            the ``"text"`` param must be a valid emoji string, for example,
            ``":snoo:"``.
        :param background_color: The flair template's new background color, as a hex
            color.
        :param css_class: The flair template's css_class (default: ``""``).
        :param max_emojis: Maximum emojis in the flair (Reddit defaults this value to
            ``10``).
        :param mod_only: Indicate if the flair can only be used by moderators.
        :param text_color: The flair template's new text color, either ``"light"`` or
            ``"dark"``.
        :param text_editable: Indicate if the flair text can be modified for each
            redditor that sets it (default: ``False``).

        For example, to add an editable redditor flair try:

        .. code-block:: python

            reddit.subreddit("test").flair.templates.add(
                "PRAW",
                css_class="praw",
                text_editable=True,
            )

        """
        self._add(
            allowable_content=allowable_content,
            background_color=background_color,
            css_class=css_class,
            is_link=False,
            max_emojis=max_emojis,
            mod_only=mod_only,
            text=text,
            text_color=text_color,
            text_editable=text_editable,
        )

    def clear(self) -> None:
        """Remove all :class:`.Redditor` flair templates from the subreddit.

        For example:

        .. code-block:: python

            reddit.subreddit("test").flair.templates.clear()

        """
        self._clear(is_link=False)

    def reorder(self, flair_list: list[str]) -> None:
        """Reorder a list of flairs.

        :param flair_list: A list of flair IDs.

        For example, to reverse the order of the :class:`.Redditor` flair templates list
        try:

        .. code-block:: python

            subreddit = reddit.subreddit("test")
            flairs = [flair["id"] for flair in subreddit.flair.templates]
            subreddit.flair.templates.reorder(list(reversed(flairs)))

        """
        self._reorder(flair_list, is_link=False)
