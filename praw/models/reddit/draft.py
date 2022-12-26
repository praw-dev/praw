"""Provide the draft class."""
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ...const import API_PATH
from ...exceptions import ClientException
from .base import RedditBase
from .subreddit import Subreddit
from .user_subreddit import UserSubreddit

if TYPE_CHECKING:  # pragma: no cover
    import praw


class Draft(RedditBase):
    """A class that represents a Reddit submission draft.

    .. include:: ../../typical_attributes.rst

    ========================== ======================================================
    Attribute                  Description
    ========================== ======================================================
    ``link_flair_template_id`` The link flair's ID.
    ``link_flair_text``        The link flair's text content, or ``None`` if not
                               flaired.
    ``modified``               Time the submission draft was modified, represented in
                               `Unix Time`_.
    ``original_content``       Whether the submission draft will be set as original
                               content.
    ``selftext``               The submission draft's selftext. ``None`` if a link
                               submission draft.
    ``spoiler``                Whether the submission will be marked as a spoiler.
    ``subreddit``              Provides an instance of :class:`.Subreddit` or
                               :class:`.UserSubreddit` (if set).
    ``title``                  The title of the submission draft.
    ``url``                    The URL the submission draft links to.
    ========================== ======================================================

    .. _unix time: https://en.wikipedia.org/wiki/Unix_time

    """

    STR_FIELD = "id"

    @classmethod
    def _prepare_data(
        cls,
        *,
        flair_id: Optional[str] = None,
        flair_text: Optional[str] = None,
        is_public_link: Optional[bool] = None,
        nsfw: Optional[bool] = None,
        original_content: Optional[bool] = None,
        selftext: Optional[str] = None,
        send_replies: Optional[bool] = None,
        spoiler: Optional[bool] = None,
        subreddit: Optional[
            Union["praw.models.Subreddit", "praw.models.UserSubreddit"]
        ] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        **draft_kwargs,
    ):
        data = {
            "body": selftext or url,
            "flair_id": flair_id,
            "flair_text": flair_text,
            "is_public_link": is_public_link,
            "kind": "markdown" if selftext is not None else "link",
            "nsfw": nsfw,
            "original_content": original_content,
            "send_replies": send_replies,
            "spoiler": spoiler,
            "title": title,
        }
        if subreddit:
            data.update(
                {
                    "subreddit": subreddit.fullname,
                    "target": "profile"
                    if subreddit.display_name.startswith("u_")
                    else "subreddit",
                }
            )
        data.update(draft_kwargs)
        return data

    def __init__(
        self,
        reddit: "praw.Reddit",
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        _data: Dict[str, Any] = None,
    ):
        """Initialize a :class:`.Draft` instance."""
        if (id, _data).count(None) != 1:
            raise TypeError("Exactly one of 'id' or '_data' must be provided.")
        fetched = False
        if id:
            self.id = id
        else:
            if len(_data) > 1:
                if _data["kind"] == "markdown":
                    _data["selftext"] = _data.pop("body")
                elif _data["kind"] == "link":
                    _data["url"] = _data.pop("body")
                fetched = True
        super().__init__(reddit, _data=_data, _fetched=fetched)

    def __repr__(self) -> str:
        """Return an object initialization representation of the instance."""
        if self._fetched:
            subreddit = (
                f" subreddit={self.subreddit.display_name!r}" if self.subreddit else ""
            )
            title = f" title={self.title!r}" if self.title else ""
            return f"{self.__class__.__name__}(id={self.id!r}{subreddit}{title})"
        else:
            return f"{self.__class__.__name__}(id={self.id!r})"

    def _fetch(self):
        for draft in self._reddit.drafts():
            if draft.id == self.id:
                self.__dict__.update(draft.__dict__)
                self._fetched = True
                return
        raise ClientException(
            f"The currently authenticated user not have a draft with an ID of {self.id}"
        )

    def delete(self):
        """Delete the :class:`.Draft`.

        Example usage:

        .. code-block:: python

            draft = reddit.drafts("124862bc-e1e9-11eb-aa4f-e68667a77cbb")
            draft.delete()

        """
        self._reddit.delete(API_PATH["draft"], params={"draft_id": self.id})

    def submit(
        self,
        *,
        flair_id: Optional[str] = None,
        flair_text: Optional[str] = None,
        nsfw: Optional[bool] = None,
        selftext: Optional[str] = None,
        spoiler: Optional[bool] = None,
        subreddit: Optional[
            Union[str, "praw.models.Subreddit", "praw.models.UserSubreddit"]
        ] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        **submit_kwargs,
    ) -> "praw.models.Submission":
        """Submit a draft.

        :param flair_id: The flair template to select (default: ``None``).
        :param flair_text: If the template's ``flair_text_editable`` value is ``True``,
            this value will set a custom text (default: ``None``). ``flair_id`` is
            required when ``flair_text`` is provided.
        :param nsfw: Whether or not the submission should be marked NSFW (default:
            ``None``).
        :param selftext: The Markdown formatted content for a ``text`` submission. Use
            an empty string, ``""``, to make a title-only submission (default:
            ``None``).
        :param spoiler: Whether or not the submission should be marked as a spoiler
            (default: ``None``).
        :param subreddit: The subreddit to submit the draft to. This accepts a subreddit
            display name, :class:`.Subreddit` object, or :class:`.UserSubreddit` object.
        :param title: The title of the submission (default: ``None``).
        :param url: The URL for a ``link`` submission (default: ``None``).

        :returns: A :class:`.Submission` object for the newly created submission.

        .. note::

            Parameters set here will override their respective :class:`.Draft`
            attributes.

        Additional keyword arguments are passed to the :meth:`.Subreddit.submit` method.

        For example, to submit a draft as is:

        .. code-block:: python

            draft = reddit.drafts("5f87d55c-e4fb-11eb-8965-6aeb41b0880e")
            submission = draft.submit()

        For example, to submit a draft but use a different title than what is set:

        .. code-block:: python

            draft = reddit.drafts("5f87d55c-e4fb-11eb-8965-6aeb41b0880e")
            submission = draft.submit(title="New Title")

        .. seealso::

            - :meth:`~.Subreddit.submit` to submit url posts and selftexts
            - :meth:`~.Subreddit.submit_gallery`. to submit more than one image in the
              same post
            - :meth:`~.Subreddit.submit_image` to submit images
            - :meth:`~.Subreddit.submit_poll` to submit polls
            - :meth:`~.Subreddit.submit_video` to submit videos and videogifs

        """
        submit_kwargs["draft_id"] = self.id
        if not (self.subreddit or subreddit):
            raise ValueError(
                "'subreddit' must be set on the Draft instance or passed as a keyword"
                " argument."
            )
        for key, attribute in [
            ("flair_id", flair_id),
            ("flair_text", flair_text),
            ("nsfw", nsfw),
            ("selftext", selftext),
            ("spoiler", spoiler),
            ("title", title),
            ("url", url),
        ]:
            value = attribute or getattr(self, key, None)
            if value is not None:
                submit_kwargs[key] = value
        if isinstance(subreddit, str):
            _subreddit = self._reddit.subreddit(subreddit)
        elif isinstance(subreddit, (Subreddit, UserSubreddit)):
            _subreddit = subreddit
        else:
            _subreddit = self.subreddit
        return _subreddit.submit(**submit_kwargs)

    def update(
        self,
        *,
        flair_id: Optional[str] = None,
        flair_text: Optional[str] = None,
        is_public_link: Optional[bool] = None,
        nsfw: Optional[bool] = None,
        original_content: Optional[bool] = None,
        selftext: Optional[str] = None,
        send_replies: Optional[bool] = None,
        spoiler: Optional[bool] = None,
        subreddit: Optional[
            Union[str, "praw.models.Subreddit", "praw.models.UserSubreddit"]
        ] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        **draft_kwargs,
    ):
        """Update the :class:`.Draft`.

        .. note::

            Only provided values will be updated.

        :param flair_id: The flair template to select.
        :param flair_text: If the template's ``flair_text_editable`` value is ``True``,
            this value will set a custom text. ``flair_id`` is required when
            ``flair_text`` is provided.
        :param is_public_link: Whether to enable public viewing of the draft before it
            is submitted.
        :param nsfw: Whether the draft should be marked NSFW.
        :param original_content: Whether the submission should be marked as original
            content.
        :param selftext: The Markdown formatted content for a text submission draft. Use
            ``None`` to make a title-only submission draft. ``selftext`` can not be
            provided if ``url`` is provided.
        :param send_replies: When ``True``, messages will be sent to the submission
            author when comments are made to the submission.
        :param spoiler: Whether the submission should be marked as a spoiler.
        :param subreddit: The subreddit to create the draft for. This accepts a
            subreddit display name, :class:`.Subreddit` object, or
            :class:`.UserSubreddit` object.
        :param title: The title of the draft.
        :param url: The URL for a ``link`` submission draft. ``url`` can not be provided
            if ``selftext`` is provided.

        Additional keyword arguments can be provided to handle new parameters as Reddit
        introduces them.

        For example, to update the title of a draft do:

        .. code-block:: python

            draft = reddit.drafts("5f87d55c-e4fb-11eb-8965-6aeb41b0880e")
            draft.update(title="New title")

        """
        if isinstance(subreddit, str):
            subreddit = self._reddit.subreddit(subreddit)
        data = self._prepare_data(
            flair_id=flair_id,
            flair_text=flair_text,
            is_public_link=is_public_link,
            nsfw=nsfw,
            original_content=original_content,
            selftext=selftext,
            send_replies=send_replies,
            spoiler=spoiler,
            subreddit=subreddit,
            title=title,
            url=url,
            **draft_kwargs,
        )
        data["id"] = self.id
        _new_draft = self._reddit.put(API_PATH["draft"], data=data)
        _new_draft._fetch()
        self.__dict__.update(_new_draft.__dict__)
