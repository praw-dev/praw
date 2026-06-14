"""Provide the Subreddit class."""

from __future__ import annotations

from json import dumps, loads
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast, overload
from urllib.parse import urljoin

import websocket
from prawcore import Redirect

from praw.const import API_PATH
from praw.exceptions import MediaPostFailed, RedditAPIException, WebSocketException
from praw.models.listing.generator import ListingGenerator
from praw.models.listing.mixins import SubredditListingMixin
from praw.models.media import PostMedia
from praw.models.reddit.base import RedditBase
from praw.models.reddit.emoji import SubredditEmoji
from praw.models.reddit.mixins import CreatedMixin, FullnameMixin, MessageableMixin
from praw.models.reddit.rules import SubredditRules
from praw.models.reddit.subreddit.filters import SubredditFilters
from praw.models.reddit.subreddit.flair import SubredditFlair
from praw.models.reddit.subreddit.moderation import SubredditModeration
from praw.models.reddit.subreddit.modmail import Modmail
from praw.models.reddit.subreddit.quarantine import SubredditQuarantine
from praw.models.reddit.subreddit.relationship import (
    ContributorRelationship,
    ModeratorRelationship,
    SubredditRelationship,
)
from praw.models.reddit.subreddit.stream import SubredditStream
from praw.models.reddit.subreddit.stylesheet import SubredditStylesheet
from praw.models.reddit.subreddit.wiki import SubredditWiki
from praw.models.reddit.widgets import SubredditWidgets, WidgetEncoder
from praw.util import cachedproperty

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    import praw
    from praw import models
    from praw.models.reddit.collections import SubredditCollections


class Subreddit(MessageableMixin, SubredditListingMixin, FullnameMixin, CreatedMixin, RedditBase):
    """A class for Subreddits.

    To obtain an instance of this class for r/test execute:

    .. code-block:: python

        subreddit = reddit.subreddit("test")

    While r/all is not a real subreddit, it can still be treated like one. The following
    outputs the titles of the 25 hottest submissions in r/all:

    .. code-block:: python

        for submission in reddit.subreddit("all").hot(limit=25):
            print(submission.title)

    Multiple subreddits can be combined with a ``+`` like so:

    .. code-block:: python

        for submission in reddit.subreddit("redditdev+learnpython").top(time_filter="all"):
            print(submission)

    Subreddits can be filtered from combined listings as follows.

    .. note::

        These filters are ignored by certain methods, including :attr:`.comments`, and
        :meth:`.SubredditStream.comments`.

    .. code-block:: python

        for submission in reddit.subreddit("all-redditdev").new():
            print(submission)

    .. include:: ../../typical_attributes.rst

    ========================= ==========================================================
    Attribute                 Description
    ========================= ==========================================================
    ``can_assign_link_flair`` Whether users can assign their own link flair.
    ``can_assign_user_flair`` Whether users can assign their own user flair.
    ``created_utc``           Time the subreddit was created, represented in `Unix
                              Time`_.
    ``description``           Subreddit description, in Markdown.
    ``description_html``      Subreddit description, in HTML.
    ``display_name``          Name of the subreddit.
    ``icon_img``              The URL of the subreddit icon image.
    ``id``                    ID of the subreddit.
    ``name``                  Fullname of the subreddit.
    ``over18``                Whether the subreddit is NSFW.
    ``public_description``    Description of the subreddit, shown in searches and on the
                              "You must be invited to visit this community" page (if
                              applicable).
    ``spoilers_enabled``      Whether the spoiler tag feature is enabled.
    ``subscribers``           Count of subscribers.
    ``user_is_banned``        Whether the authenticated user is banned.
    ``user_is_moderator``     Whether the authenticated user is a moderator.
    ``user_is_subscriber``    Whether the authenticated user is subscribed.
    ========================= ==========================================================

    .. note::

        Trying to retrieve attributes of quarantined or private subreddits will result
        in a 403 error. Trying to retrieve attributes of a banned subreddit will result
        in a 404 error.

    .. _unix time: https://en.wikipedia.org/wiki/Unix_time

    """

    MAX_CAPTION_LENGTH = 180
    MESSAGE_PREFIX = "#"
    STR_FIELD = "display_name"

    # Bound at import time by the submission and collections modules to avoid circular
    # imports.
    _submission_class: type[models.Submission]
    _subreddit_collections_class: type[SubredditCollections]

    last_updated: int

    @staticmethod
    def _create_or_update(
        *,
        _reddit: praw.Reddit,
        allow_images: bool | None = None,
        allow_post_crossposts: bool | None = None,
        allow_top: bool | None = None,
        collapse_deleted_comments: bool | None = None,
        comment_score_hide_mins: int | None = None,
        description: str | None = None,
        domain: str | None = None,
        exclude_banned_modqueue: bool | None = None,
        header_hover_text: str | None = None,
        hide_ads: bool | None = None,
        key_color: str | None = None,
        lang: str | None = None,
        link_type: str | None = None,
        name: str | None = None,
        over_18: bool | None = None,
        public_description: str | None = None,
        public_traffic: bool | None = None,
        show_media: bool | None = None,
        show_media_preview: bool | None = None,
        spam_comments: bool | None = None,
        spam_links: bool | None = None,
        spam_selfposts: bool | None = None,
        spoilers_enabled: bool | None = None,
        sr: str | None = None,
        submit_link_label: str | None = None,
        submit_text: str | None = None,
        submit_text_label: str | None = None,
        subreddit_type: str | None = None,
        suggested_comment_sort: str | None = None,
        title: str | None = None,
        wiki_edit_age: int | None = None,
        wiki_edit_karma: int | None = None,
        wikimode: str | None = None,
        **other_settings: Any,
    ) -> None:
        model = {
            "allow_images": allow_images,
            "allow_post_crossposts": allow_post_crossposts,
            "allow_top": allow_top,
            "collapse_deleted_comments": collapse_deleted_comments,
            "comment_score_hide_mins": comment_score_hide_mins,
            "description": description,
            "domain": domain,
            "exclude_banned_modqueue": exclude_banned_modqueue,
            "header-title": header_hover_text,  # Remap here - better name
            "hide_ads": hide_ads,
            "key_color": key_color,
            "lang": lang,
            "link_type": link_type,
            "name": name,
            "over_18": over_18,
            "public_description": public_description,
            "public_traffic": public_traffic,
            "show_media": show_media,
            "show_media_preview": show_media_preview,
            "spam_comments": spam_comments,
            "spam_links": spam_links,
            "spam_selfposts": spam_selfposts,
            "spoilers_enabled": spoilers_enabled,
            "sr": sr,
            "submit_link_label": submit_link_label,
            "submit_text": submit_text,
            "submit_text_label": submit_text_label,
            "suggested_comment_sort": suggested_comment_sort,
            "title": title,
            "type": subreddit_type,
            "wiki_edit_age": wiki_edit_age,
            "wiki_edit_karma": wiki_edit_karma,
            "wikimode": wikimode,
        }

        model.update(other_settings)

        _reddit.post(API_PATH["site_admin"], data=model)

    @staticmethod
    def _subreddit_list(
        *,
        other_subreddits: Sequence[str | models.Subreddit] | None,
        subreddit: models.Subreddit,
    ) -> str:
        if other_subreddits:
            return ",".join([str(subreddit)] + [str(x) for x in other_subreddits])
        return str(subreddit)

    @staticmethod
    def _validate_gallery(images: list[dict[str, str | PostMedia]]) -> None:
        for image in images:
            media = image.get("media")
            if not isinstance(media, PostMedia):
                msg = "'media' is required and must be a PostMedia instance."
                raise TypeError(msg)
            if not len(cast("str", image.get("caption", ""))) <= Subreddit.MAX_CAPTION_LENGTH:
                msg = "Caption must be 180 characters or less."
                raise TypeError(msg)

    @staticmethod
    def _validate_inline_media(inline_media: models.InlineMedia) -> None:
        if not isinstance(inline_media.media, PostMedia):
            msg = "'media' must be a PostMedia instance."
            raise TypeError(msg)

    @cachedproperty
    def banned(self) -> SubredditRelationship:
        """Provide an instance of :class:`.SubredditRelationship`.

        For example, to ban a user try:

        .. code-block:: python

            reddit.subreddit("test").banned.add("spez", ban_reason="...")

        To list the banned users along with any notes, try:

        .. code-block:: python

            for ban in reddit.subreddit("test").banned():
                print(f"{ban}: {ban.note}")

        """
        return SubredditRelationship(self, "banned")

    @cachedproperty
    def collections(self) -> SubredditCollections:
        r"""Provide an instance of :class:`.SubredditCollections`.

        To see the permalinks of all :class:`.Collection`\ s that belong to a subreddit,
        try:

        .. code-block:: python

            for collection in reddit.subreddit("test").collections:
                print(collection.permalink)

        To get a specific :class:`.Collection` by its UUID or permalink, use one of the
        following:

        .. code-block:: python

            collection = reddit.subreddit("test").collections("some_uuid")
            collection = reddit.subreddit("test").collections(
                permalink="https://reddit.com/r/SUBREDDIT/collection/some_uuid"
            )

        """
        return self._subreddit_collections_class(self._reddit, self)

    @cachedproperty
    def contributor(self) -> ContributorRelationship:
        """Provide an instance of :class:`.ContributorRelationship`.

        Contributors are also known as approved submitters.

        To add a contributor try:

        .. code-block:: python

            reddit.subreddit("test").contributor.add("spez")

        """
        return ContributorRelationship(self, "contributor")

    @cachedproperty
    def emoji(self) -> SubredditEmoji:
        """Provide an instance of :class:`.SubredditEmoji`.

        This attribute can be used to discover all emoji for a subreddit:

        .. code-block:: python

            for emoji in reddit.subreddit("test").emoji:
                print(emoji)

        A single emoji can be lazily retrieved via:

        .. code-block:: python

            reddit.subreddit("test").emoji["emoji_name"]

        .. note::

            Attempting to access attributes of a nonexistent emoji will result in a
            :class:`.ClientException`.

        """
        return SubredditEmoji(self)

    @cachedproperty
    def filters(self) -> SubredditFilters:
        """Provide an instance of :class:`.SubredditFilters`.

        For example, to add a filter, run:

        .. code-block:: python

            reddit.subreddit("all").filters.add("test")

        """
        return SubredditFilters(self)

    @cachedproperty
    def flair(self) -> SubredditFlair:
        """Provide an instance of :class:`.SubredditFlair`.

        Use this attribute for interacting with a :class:`.Subreddit`'s flair. For
        example, to list all the flair for a subreddit which you have the ``flair``
        moderator permission on try:

        .. code-block:: python

            for flair in reddit.subreddit("test").flair():
                print(flair)

        Flair templates can be interacted with through this attribute via:

        .. code-block:: python

            for template in reddit.subreddit("test").flair.templates:
                print(template)

        """
        return SubredditFlair(self)

    @cachedproperty
    def mod(self) -> SubredditModeration:
        """Provide an instance of :class:`.SubredditModeration`.

        For example, to accept a moderation invite from r/test:

        .. code-block:: python

            reddit.subreddit("test").mod.accept_invite()

        """
        return SubredditModeration(self)

    @cachedproperty
    def moderator(self) -> ModeratorRelationship:
        """Provide an instance of :class:`.ModeratorRelationship`.

        For example, to add a moderator try:

        .. code-block:: python

            reddit.subreddit("test").moderator.add("spez")

        To list the moderators along with their permissions try:

        .. code-block:: python

            for moderator in reddit.subreddit("test").moderator():
                print(f"{moderator}: {moderator.mod_permissions}")

        """
        return ModeratorRelationship(self, "moderator")

    @cachedproperty
    def modmail(self) -> Modmail:
        """Provide an instance of :class:`.Modmail`.

        For example, to send a new modmail from r/test to u/spez with the subject
        ``"test"`` along with a message body of ``"hello"``:

        .. code-block:: python

            reddit.subreddit("test").modmail.create(subject="test", body="hello", recipient="spez")

        """
        return Modmail(self)

    @cachedproperty
    def muted(self) -> SubredditRelationship:
        """Provide an instance of :class:`.SubredditRelationship`.

        For example, muted users can be iterated through like so:

        .. code-block:: python

            for mute in reddit.subreddit("test").muted():
                print(f"{mute}: {mute.date}")

        """
        return SubredditRelationship(self, "muted")

    @cachedproperty
    def quaran(self) -> SubredditQuarantine:
        """Provide an instance of :class:`.SubredditQuarantine`.

        This property is named ``quaran`` because ``quarantine`` is a subreddit
        attribute returned by Reddit to indicate whether or not a subreddit is
        quarantined.

        To opt-in into a quarantined subreddit:

        .. code-block:: python

            reddit.subreddit("test").quaran.opt_in()

        """
        return SubredditQuarantine(self)

    @cachedproperty
    def rules(self) -> SubredditRules:
        """Provide an instance of :class:`.SubredditRules`.

        Use this attribute for interacting with a :class:`.Subreddit`'s rules.

        For example, to list all the rules for a subreddit:

        .. code-block:: python

            for rule in reddit.subreddit("test").rules:
                print(rule)

        Moderators can also add rules to the subreddit. For example, to make a rule
        called ``"No spam"`` in r/test:

        .. code-block:: python

            reddit.subreddit("test").rules.mod.add(
                short_name="No spam", kind="all", description="Do not spam. Spam bad"
            )

        """
        return SubredditRules(self)

    @cachedproperty
    def stream(self) -> SubredditStream:
        """Provide an instance of :class:`.SubredditStream`.

        Streams can be used to indefinitely retrieve new comments made to a subreddit,
        like:

        .. code-block:: python

            for comment in reddit.subreddit("test").stream.comments():
                print(comment)

        Additionally, new submissions can be retrieved via the stream. In the following
        example all submissions are fetched via the special r/all:

        .. code-block:: python

            for submission in reddit.subreddit("all").stream.submissions():
                print(submission)

        """
        return SubredditStream(self)

    @cachedproperty
    def stylesheet(self) -> SubredditStylesheet:
        """Provide an instance of :class:`.SubredditStylesheet`.

        For example, to add the css data ``.test{color:blue}`` to the existing
        stylesheet:

        .. code-block:: python

            subreddit = reddit.subreddit("test")
            stylesheet = subreddit.stylesheet()
            stylesheet.stylesheet += ".test{color:blue}"
            subreddit.stylesheet.update(stylesheet.stylesheet)

        """
        return SubredditStylesheet(self)

    @cachedproperty
    def widgets(self) -> models.SubredditWidgets:
        """Provide an instance of :class:`.SubredditWidgets`.

        **Example usage**

        Get all sidebar widgets:

        .. code-block:: python

            for widget in reddit.subreddit("test").widgets.sidebar:
                print(widget)

        Get ID card widget:

        .. code-block:: python

            print(reddit.subreddit("test").widgets.id_card)

        """
        return SubredditWidgets(self)

    @cachedproperty
    def wiki(self) -> SubredditWiki:
        """Provide an instance of :class:`.SubredditWiki`.

        This attribute can be used to discover all wikipages for a subreddit:

        .. code-block:: python

            for wikipage in reddit.subreddit("test").wiki:
                print(wikipage)

        To fetch the content for a given wikipage try:

        .. code-block:: python

            wikipage = reddit.subreddit("test").wiki["proof"]
            print(wikipage.content_md)

        """
        return SubredditWiki(self)

    @property
    def _kind(self) -> str:
        """Return the class's kind."""
        return self._reddit.config.kinds["subreddit"]

    def __init__(
        self,
        reddit: praw.Reddit,
        display_name: str | None = None,
        _data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a :class:`.Subreddit` instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param display_name: The name of the subreddit.

        .. note::

            This class should not be initialized directly. Instead, obtain an instance
            via:

            .. code-block:: python

                subreddit = reddit.subreddit("test")

        """
        if (display_name, _data).count(None) != 1:
            msg = "Either 'display_name' or '_data' must be provided."
            raise TypeError(msg)
        if display_name:
            self.display_name = display_name
        super().__init__(reddit, _data=_data)
        self._path = API_PATH["subreddit"].format(subreddit=self)

    def _convert_to_fancypants(self, markdown_text: str) -> dict:
        """Convert a Markdown string to a dict for use with the ``richtext_json`` param.

        :param markdown_text: A Markdown string to convert.

        :returns: A dict in ``richtext_json`` format.

        """
        text_data = {"markdown_text": markdown_text, "output_mode": "rtjson"}
        return self._reddit.post(API_PATH["convert_rte_body"], data=text_data)["output"]

    def _fetch(self) -> None:
        data = self._fetch_data()
        data = data["data"]
        other = type(self)(self._reddit, _data=data)
        self.__dict__.update(other.__dict__)
        super()._fetch()

    def _fetch_info(self) -> tuple[str, dict[str, RedditBase], None]:
        return "subreddit_about", {"subreddit": self}, None

    def _submit_media(
        self, *, data: dict[Any, Any], timeout: int, without_websockets: bool
    ) -> models.Submission | None:
        """Submit and return an ``image``, ``video``, or ``videogif``.

        This is a helper method for submitting posts that are not link posts or self
        posts.

        """
        response = self._reddit.post(API_PATH["submit"], data=data)
        websocket_url = response["json"]["data"]["websocket_url"]
        connection = None
        if websocket_url is not None and not without_websockets:
            try:
                connection = websocket.create_connection(websocket_url, timeout=timeout)
            except (
                OSError,
                websocket.WebSocketException,
                BlockingIOError,
            ):
                msg = "Error establishing websocket connection."
                raise WebSocketException(msg) from None

        if connection is None:
            return None

        try:
            ws_update = loads(connection.recv())
            connection.close()
        except (OSError, websocket.WebSocketException, BlockingIOError):
            msg = "Websocket error. Check your media file. Your post may still have been created."
            raise WebSocketException(
                msg,
            ) from None
        if ws_update.get("type") == "failed":
            raise MediaPostFailed
        url = ws_update["payload"]["redirect"]
        return self._reddit.submission(url=url)

    def _upload_inline_media(self, inline_media: models.InlineMedia) -> models.InlineMedia:
        """Upload media for use in self posts and return ``inline_media``.

        :param inline_media: An :class:`.InlineMedia` object to validate and upload.

        """
        self._validate_inline_media(inline_media)
        inline_media.media_id = inline_media.media._upload(self._reddit, upload_type="selfpost")
        return inline_media

    def post_requirements(self) -> dict[str, str | int | bool]:
        """Get the post requirements for a subreddit.

        :returns: A dict with the various requirements.

        The returned dict contains the following keys:

        - ``domain_blacklist``
        - ``body_restriction_policy``
        - ``domain_whitelist``
        - ``title_regexes``
        - ``body_blacklisted_strings``
        - ``body_required_strings``
        - ``title_text_min_length``
        - ``is_flair_required``
        - ``title_text_max_length``
        - ``body_regexes``
        - ``link_repost_age``
        - ``body_text_min_length``
        - ``link_restriction_policy``
        - ``body_text_max_length``
        - ``title_required_strings``
        - ``title_blacklisted_strings``
        - ``guidelines_text``
        - ``guidelines_display_policy``

        For example, to fetch the post requirements for r/test:

        .. code-block:: python

            print(reddit.subreddit("test").post_requirements)

        """
        return self._reddit.get(API_PATH["post_requirements"].format(subreddit=str(self)))

    def search(
        self,
        query: str,
        *,
        sort: str = "relevance",
        syntax: str = "lucene",
        time_filter: str = "all",
        **generator_kwargs: Any,
    ) -> Iterator[models.Submission]:
        """Return a :class:`.ListingGenerator` for items that match ``query``.

        :param query: The query string to search for.
        :param sort: Can be one of: ``"relevance"``, ``"hot"``, ``"top"``, ``"new"``, or
            ``"comments"``. (default: ``"relevance"``).
        :param syntax: Can be one of: ``"cloudsearch"``, ``"lucene"``, or ``"plain"``
            (default: ``"lucene"``).
        :param time_filter: Can be one of: ``"all"``, ``"day"``, ``"hour"``,
            ``"month"``, ``"week"``, or ``"year"`` (default: ``"all"``).

        For more information on building a search query see:
        https://www.reddit.com/r/reddit.com/wiki/search/

        For example, to search all subreddits for ``"praw"`` try:

        .. code-block:: python

            for submission in reddit.subreddit("all").search("praw"):
                print(submission.title)

        """
        self._validate_time_filter(time_filter)
        not_all = self.display_name.lower() != "all"
        self._safely_add_arguments(
            arguments=generator_kwargs,
            key="params",
            q=query,
            restrict_sr=not_all,
            sort=sort,
            syntax=syntax,
            t=time_filter,
        )
        url = API_PATH["search"].format(subreddit=self)
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def sticky(self, *, number: int = 1) -> models.Submission:
        """Return a :class:`.Submission` object for a sticky of the subreddit.

        :param number: Specify which sticky to return. 1 appears at the top (default:
            ``1``).

        :raises: ``prawcore.NotFound`` if the sticky does not exist.

        For example, to get the stickied post on r/test:

        .. code-block:: python

            reddit.subreddit("test").sticky()

        """
        url = API_PATH["about_sticky"].format(subreddit=self)
        path = url
        try:
            self._reddit.get(url, params={"num": number})
        except Redirect as redirect:
            path = redirect.path
        reddit_url = self._reddit.config.reddit_url
        assert reddit_url is not None
        return self._submission_class(self._reddit, url=urljoin(reddit_url, path))

    @overload
    def submit(
        self,
        title: str,
        *,
        collection_id: str | None = ...,
        discussion_type: str | None = ...,
        draft_id: str | None = ...,
        flair_id: str | None = ...,
        flair_text: str | None = ...,
        inline_media: dict[str, models.InlineMedia] | None = ...,
        nsfw: bool = ...,
        resubmit: bool = ...,
        selftext: str,
        send_replies: bool = ...,
        spoiler: bool = ...,
    ) -> models.Submission: ...

    @overload
    def submit(
        self,
        title: str,
        *,
        collection_id: str | None = ...,
        discussion_type: str | None = ...,
        draft_id: str | None = ...,
        flair_id: str | None = ...,
        flair_text: str | None = ...,
        nsfw: bool = ...,
        resubmit: bool = ...,
        selftext: str | None = ...,
        send_replies: bool = ...,
        spoiler: bool = ...,
        url: str,
    ) -> models.Submission: ...

    @overload
    def submit(
        self,
        title: str,
        *,
        collection_id: str | None = ...,
        discussion_type: str | None = ...,
        flair_id: str | None = ...,
        flair_text: str | None = ...,
        image: models.PostMedia,
        nsfw: bool = ...,
        resubmit: bool = ...,
        selftext: str | None = ...,
        send_replies: bool = ...,
        spoiler: bool = ...,
        timeout: int = ...,
        without_websockets: bool = ...,
    ) -> models.Submission | None: ...

    @overload
    def submit(
        self,
        title: str,
        *,
        collection_id: str | None = ...,
        discussion_type: str | None = ...,
        flair_id: str | None = ...,
        flair_text: str | None = ...,
        gallery: list[models.PostMedia | dict[str, str | models.PostMedia]],
        nsfw: bool = ...,
        selftext: str | None = ...,
        send_replies: bool = ...,
        spoiler: bool = ...,
    ) -> models.Submission: ...

    @overload
    def submit(
        self,
        title: str,
        *,
        collection_id: str | None = ...,
        discussion_type: str | None = ...,
        flair_id: str | None = ...,
        flair_text: str | None = ...,
        nsfw: bool = ...,
        poll: dict[str, int | list[str]],
        resubmit: bool = ...,
        selftext: str | None = ...,
        send_replies: bool = ...,
        spoiler: bool = ...,
    ) -> models.Submission: ...

    @overload
    def submit(
        self,
        title: str,
        *,
        collection_id: str | None = ...,
        discussion_type: str | None = ...,
        flair_id: str | None = ...,
        flair_text: str | None = ...,
        nsfw: bool = ...,
        resubmit: bool = ...,
        selftext: str | None = ...,
        send_replies: bool = ...,
        spoiler: bool = ...,
        timeout: int = ...,
        video: models.PostMedia | dict[str, bool | models.PostMedia],
        without_websockets: bool = ...,
    ) -> models.Submission | None: ...

    def submit(
        self,
        title: str,
        *,
        collection_id: str | None = None,
        discussion_type: str | None = None,
        draft_id: str | None = None,
        flair_id: str | None = None,
        flair_text: str | None = None,
        gallery: list[models.PostMedia | dict[str, str | models.PostMedia]] | None = None,
        image: models.PostMedia | None = None,
        inline_media: dict[str, models.InlineMedia] | None = None,
        nsfw: bool = False,
        poll: dict[str, int | list[str]] | None = None,
        resubmit: bool = True,
        selftext: str | None = None,
        send_replies: bool = True,
        spoiler: bool = False,
        timeout: int = 10,
        url: str | None = None,
        video: models.PostMedia | dict[str, bool | models.PostMedia] | None = None,
        without_websockets: bool = False,
    ) -> models.Submission | None:
        r"""Add a submission to the :class:`.Subreddit`.

        :param title: The title of the submission.
        :param collection_id: The UUID of a :class:`.Collection` to add the
            newly-submitted post to.
        :param discussion_type: Set to ``"CHAT"`` to enable live discussion instead of
            traditional comments (default: ``None``).
        :param draft_id: The ID of a draft to submit. Only applies to text and link
            submissions.
        :param flair_id: The flair template to select (default: ``None``).
        :param flair_text: If the template's ``flair_text_editable`` value is ``True``,
            this value will set a custom text (default: ``None``). ``flair_id`` is
            required when ``flair_text`` is provided.
        :param gallery: A list of images to post as a gallery. Each item is either a
            :class:`.PostMedia` or a ``dict`` with the structure ``{"media":
            PostMedia("path"), "caption": "caption", "outbound_url": "url"}``, where
            only ``media`` is required.
        :param image: The :class:`.PostMedia` image to upload and post.
        :param inline_media: A dict of :class:`.InlineMedia` objects where the key is
            the placeholder name in ``selftext``. Only supported for text submissions.
        :param nsfw: Whether the submission should be marked NSFW (default: ``False``).
        :param poll: A ``dict`` with the structure ``{"duration": 3, "options": ["Yes",
            "No"]}``, where ``duration`` is the number of days the poll should accept
            votes (between ``1`` and ``7``, inclusive) and ``options`` is a list of two
            to six poll options as ``str``. Both keys are required.
        :param resubmit: When ``False``, an error will occur if the URL has already been
            submitted (default: ``True``).
        :param selftext: The Markdown formatted content for a ``text`` submission or
            optional Markdown-formatted body text for any other kind of submission. Use
            an empty string, ``""``, to make a title-only submission.
        :param send_replies: When ``True``, messages will be sent to the submission
            author when comments are made to the submission (default: ``True``).
        :param spoiler: Whether the submission should be marked as a spoiler (default:
            ``False``).
        :param timeout: Specifies a particular timeout, in seconds, for the WebSockets
            connection used by ``image`` and ``video`` submissions. Use to avoid
            "Websocket error" exceptions (default: ``10``).
        :param url: The URL for a ``link`` submission.
        :param video: The video to upload and post. Either a :class:`.PostMedia` or a
            ``dict`` with the structure ``{"media": PostMedia("path"), "gif": True,
            "thumbnail": PostMedia("path")}``, where only ``media`` is required. Set
            ``"gif"`` to ``True`` to submit the video as a videogif, which is
            essentially a silent video (default: ``False``). When ``"thumbnail"`` is not
            provided, the PRAW logo will be used as the thumbnail.
        :param without_websockets: Set to ``True`` to disable use of WebSockets for
            ``image`` and ``video`` submissions (see note below for an explanation). If
            ``True``, this method doesn't return anything (default: ``False``).

        :returns: A :class:`.Submission` object for the newly created submission, unless
            ``without_websockets`` is ``True`` for an ``image`` or ``video`` submission.

        :raises: :class:`.ClientException` if ``image`` or a ``gallery`` item's
            ``media`` refers to a file that is not an image, or if the ``video`` (or its
            ``media``) refers to a file that is not a video.

        At least one of ``gallery``, ``image``, ``poll``, ``selftext``, ``url``, or
        ``video`` must be provided. ``gallery``, ``image``, ``poll``, ``url``, and
        ``video`` are mutually exclusive, while ``selftext`` may accompany any of them
        as optional Markdown-formatted body text. ``selftext`` that accompanies another
        kind of submission does not support ``inline_media``.

        For example, to submit a URL to r/test do:

        .. code-block:: python

            title = "PRAW documentation"
            url = "https://praw.readthedocs.io"
            reddit.subreddit("test").submit(title, url=url)

        To submit an image to r/test do:

        .. code-block:: python

            from praw.models import PostMedia

            title = "My favorite picture"
            image = PostMedia("/path/to/image.png")
            reddit.subreddit("test").submit(title, image=image)

        To submit an image gallery to r/test do:

        .. code-block:: python

            from praw.models import PostMedia

            title = "My favorite pictures"
            gallery = [
                PostMedia("/path/to/image.png"),
                {
                    "media": PostMedia("/path/to/image2.png"),
                    "caption": "Image caption 2",
                },
                {
                    "media": PostMedia("/path/to/image3.png"),
                    "caption": "Image caption 3",
                    "outbound_url": "https://example.com/link3",
                },
            ]
            reddit.subreddit("test").submit(title, gallery=gallery)

        To submit a video to r/test do:

        .. code-block:: python

            from praw.models import PostMedia

            title = "My favorite movie"
            video = PostMedia("/path/to/video.mp4")
            reddit.subreddit("test").submit(title, video=video)

        To submit a videogif with a custom thumbnail instead, do:

        .. code-block:: python

            from praw.models import PostMedia

            title = "My favorite gif"
            video = {
                "gif": True,
                "media": PostMedia("/path/to/video.mp4"),
                "thumbnail": PostMedia("/path/to/thumbnail.png"),
            }
            reddit.subreddit("test").submit(title, video=video)

        To submit a poll to r/test do:

        .. code-block:: python

            title = "Do you like PRAW?"
            poll = {"duration": 3, "options": ["Yes", "No"]}
            reddit.subreddit("test").submit(title, poll=poll)

        To submit a self post with inline media do:

        .. code-block:: python

            from praw.models import InlineGif, InlineImage, InlineVideo, PostMedia

            gif = InlineGif(caption="optional caption", media=PostMedia("path/to/image.gif"))
            image = InlineImage(caption="optional caption", media=PostMedia("path/to/image.jpg"))
            video = InlineVideo(caption="optional caption", media=PostMedia("path/to/video.mp4"))
            selftext = "Text with a gif {gif1} an image {image1} and a video {video1} inline"
            media = {"gif1": gif, "image1": image, "video1": video}
            reddit.subreddit("test").submit("title", inline_media=media, selftext=selftext)

        .. note::

            Inserted media will have a padding of ``\\n\\n`` automatically added. This
            is due to the weirdness with Reddit's API. Using the example above, the
            result selftext body will look like so:

            .. code-block::

                Text with a gif

                ![gif](u1rchuphryq51 "optional caption")

                an image

                ![img](srnr8tshryq51 "optional caption")

                and video

                ![video](gmc7rvthryq51 "optional caption")

                inline

        .. note::

            For ``image`` and ``video`` submissions, Reddit's API uses WebSockets to
            respond with the link of the newly created post. If this fails, the method
            will raise :class:`.WebSocketException`. Occasionally, the Reddit post will
            still be created. More often, there is an error with the media file. If you
            frequently get exceptions but successfully created posts, try setting the
            ``timeout`` parameter to a value above 10.

            To disable the use of WebSockets, set ``without_websockets=True``. This will
            make the method return ``None``, though the post will still be created. You
            may wish to do this if you are running your program in a restricted network
            environment, or using a proxy that doesn't support WebSockets connections.

        .. note::

            To submit a post to a subreddit with the ``"news"`` flair, you can get the
            flair id like this:

            .. code-block::

                choices = list(subreddit.flair.link_templates.user_selectable())
                template_id = next(x for x in choices if x["flair_text"] == "news")["flair_template_id"]
                subreddit.submit("title", flair_id=template_id, url="https://www.news.com/")

        """
        provided = [
            name
            for name, value in (
                ("gallery", gallery),
                ("image", image),
                ("poll", poll),
                ("url", url),
                ("video", video),
            )
            if value is not None
        ]
        if len(provided) > 1:
            msg = f"Only one of 'gallery', 'image', 'poll', 'url', or 'video' can be provided ({', '.join(repr(name) for name in provided)} given)."
            raise TypeError(msg)
        kind = provided[0] if provided else None
        # test for empty string in selftext for title-only submissions
        if kind is None and not (bool(selftext) or selftext == ""):  # noqa: PLC1901
            msg = "At least one of 'gallery', 'image', 'poll', 'selftext', 'url', or 'video' must be provided."
            raise TypeError(msg)
        if inline_media and kind is not None:
            msg = f"'inline_media' is only supported for text submissions. Only Markdown text can be used for the selftext of a {kind!r} submission."
            raise TypeError(msg)

        data = {
            "nsfw": bool(nsfw),
            "sendreplies": bool(send_replies),
            "spoiler": bool(spoiler),
            "sr": str(self),
            "title": title,
            "validate_on_submit": True,
        }
        data.update({
            key: value
            for key, value in (
                ("collection_id", collection_id),
                ("discussion_type", discussion_type),
                ("flair_id", flair_id),
                ("flair_text", flair_text),
            )
            if value is not None
        })

        if gallery is not None:
            images: list[dict[str, str | PostMedia]] = [
                {"media": item} if isinstance(item, PostMedia) else item for item in gallery
            ]
            self._validate_gallery(images)
            data.update(api_type="json", items=[], show_error_list=True)
            if selftext is not None:
                data["text"] = selftext
            for image_item in images:
                data["items"].append({
                    "caption": image_item.get("caption", ""),
                    "media_id": cast("PostMedia", image_item["media"])._upload(
                        self._reddit,
                        expected_mime_prefix="image",
                        upload_type="gallery",
                    ),
                    "outbound_url": image_item.get("outbound_url", ""),
                })
            response = self._reddit.request(json=data, method="POST", path=API_PATH["submit_gallery_post"])["json"]
            if response["errors"]:
                raise RedditAPIException(response["errors"])
            return self._reddit.submission(url=response["data"]["url"])

        data["resubmit"] = bool(resubmit)

        if poll is not None:
            invalid_keys = poll.keys() - {"duration", "options"}
            if invalid_keys:
                msg = f"'poll' contains invalid keys: {', '.join(repr(key) for key in sorted(invalid_keys))}."
                raise TypeError(msg)
            missing_keys = {"duration", "options"} - poll.keys()
            if missing_keys:
                msg = f"'poll' is missing required keys: {', '.join(repr(key) for key in sorted(missing_keys))}."
                raise TypeError(msg)
            data.update(
                duration=poll["duration"],
                options=poll["options"],
                text=selftext if selftext is not None else "",
            )
            return self._reddit.post(API_PATH["submit_poll_post"], json=data)

        if image is not None:
            if selftext is not None:
                data["text"] = selftext
            data.update(kind="image", url=image._upload(self._reddit, expected_mime_prefix="image"))
            return self._submit_media(data=data, timeout=timeout, without_websockets=without_websockets)

        if video is not None:
            if isinstance(video, PostMedia):
                video = {"media": video}
            invalid_keys = video.keys() - {"gif", "media", "thumbnail"}
            if invalid_keys:
                msg = f"'video' contains invalid keys: {', '.join(repr(key) for key in sorted(invalid_keys))}."
                raise TypeError(msg)
            video_media = video.get("media")
            if not isinstance(video_media, PostMedia):
                msg = "'media' is required and must be a PostMedia instance."
                raise TypeError(msg)
            thumbnail_media = cast("PostMedia | None", video.get("thumbnail"))
            if thumbnail_media is None:
                # if we're uploading without a thumbnail, use the PRAW logo
                logo_path = Path(__file__).absolute().parent.parent.parent.parent / "images" / "PRAW logo.png"
                thumbnail_media = PostMedia(str(logo_path))
            if selftext is not None:
                data["text"] = selftext
            data.update(
                kind="videogif" if video.get("gif") else "video",
                url=video_media._upload(self._reddit, expected_mime_prefix="video"),
                video_poster_url=thumbnail_media._upload(self._reddit),
            )
            return self._submit_media(data=data, timeout=timeout, without_websockets=without_websockets)

        if draft_id is not None:
            data["draft_id"] = draft_id
        if url is not None:
            data.update(kind="link", url=url)
            # we can ignore an empty string for selftext here b/c body text is optional for link posts
            if selftext:
                data["text"] = selftext
        else:
            data.update(kind="self")
            if inline_media:
                assert selftext is not None
                body = selftext.format(**{
                    placeholder: self._upload_inline_media(media) for placeholder, media in inline_media.items()
                })
                data.update(richtext_json=dumps(self._convert_to_fancypants(body)))
            else:
                data.update(text=selftext)

        return self._reddit.post(API_PATH["submit"], data=data)

    def subscribe(self, *, other_subreddits: list[models.Subreddit] | None = None) -> None:
        """Subscribe to the subreddit.

        :param other_subreddits: When provided, also subscribe to the provided list of
            subreddits.

        For example, to subscribe to r/test:

        .. code-block:: python

            reddit.subreddit("test").subscribe()

        """
        data = {
            "action": "sub",
            "skip_inital_defaults": True,
            "sr_name": self._subreddit_list(other_subreddits=other_subreddits, subreddit=self),
        }
        self._reddit.post(API_PATH["subscribe"], data=data)

    def traffic(self) -> dict[str, list[list[int]]]:
        """Return a dictionary of the :class:`.Subreddit`'s traffic statistics.

        :raises: ``prawcore.NotFound`` when the traffic stats aren't available to the
            authenticated user, that is, they are not public and the authenticated user
            is not a moderator of the subreddit.

        The traffic method returns a dict with three keys. The keys are ``day``,
        ``hour`` and ``month``. Each key contains a list of lists with 3 or 4 values.
        The first value is a timestamp indicating the start of the category (start of
        the day for the ``day`` key, start of the hour for the ``hour`` key, etc.). The
        second, third, and fourth values indicate the unique pageviews, total pageviews,
        and subscribers, respectively.

        .. note::

            The ``hour`` key does not contain subscribers, and therefore each sub-list
            contains three values.

        For example, to get the traffic stats for r/test:

        .. code-block:: python

            stats = reddit.subreddit("test").traffic()

        """
        return self._reddit.get(API_PATH["about_traffic"].format(subreddit=self))

    def unsubscribe(self, *, other_subreddits: list[models.Subreddit] | None = None) -> None:
        """Unsubscribe from the subreddit.

        :param other_subreddits: When provided, also unsubscribe from the provided list
            of subreddits.

        To unsubscribe from r/test:

        .. code-block:: python

            reddit.subreddit("test").unsubscribe()

        """
        data = {
            "action": "unsub",
            "sr_name": self._subreddit_list(other_subreddits=other_subreddits, subreddit=self),
        }
        self._reddit.post(API_PATH["subscribe"], data=data)


WidgetEncoder._subreddit_class = Subreddit
