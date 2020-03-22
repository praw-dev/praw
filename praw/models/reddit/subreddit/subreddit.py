"""Provide the Subreddit class."""

# pylint: disable=too-many-lines
import socket
from json import loads
from os.path import basename, abspath, join
from urllib.parse import urljoin
from xml.etree.ElementTree import XML

import websocket
from prawcore import Redirect

from ....const import API_PATH
from ....exceptions import (
    ClientException,
    TooLargeMediaException,
    WebSocketException,
)
from ....util.cache import cachedproperty
from ...listing.generator import ListingGenerator
from ...listing.mixins import SubredditListingMixin
from ..base import RedditBase
from ..emoji import SubredditEmoji
from ..mixins import FullnameMixin, MessageableMixin
from ..widgets import SubredditWidgets, WidgetEncoder
from .relationship.relationship import SubredditRelationship
from .relationship.contributor import ContributorRelationship
from .relationship.moderator import ModeratorRelationship
from .wiki import SubredditWiki
from .modmail import Modmail
from .stylesheet import SubredditStylesheet
from .flair.flair import SubredditFlair
from .filters import SubredditFilters
from .moderation import SubredditModeration
from .quarantine import SubredditQuarantine
from .stream import SubredditStream


class Subreddit(
    MessageableMixin, SubredditListingMixin, FullnameMixin, RedditBase
):
    """A class for Subreddits.

    To obtain an instance of this class for subreddit ``r/redditdev`` execute:

    .. code-block:: python

       subreddit = reddit.subreddit('redditdev')

    While ``r/all`` is not a real subreddit, it can still be treated like
    one. The following outputs the titles of the 25 hottest submissions in
    ``r/all``:

    .. code-block:: python

       for submission in reddit.subreddit('all').hot(limit=25):
           print(submission.title)

    Multiple subreddits can be combined with a ``+`` like so:

    .. code-block:: python

       for submission in reddit.subreddit('redditdev+learnpython').top('all'):
           print(submission)

    Subreddits can be filtered from combined listings as follows. Note that
    these filters are ignored by certain methods, including
    :attr:`~praw.models.Subreddit.comments`,
    :meth:`~praw.models.Subreddit.gilded`, and
    :meth:`.SubredditStream.comments`.

    .. code-block:: python

       for submission in reddit.subreddit('all-redditdev').new():
           print(submission)

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ========================== ===============================================
    Attribute                  Description
    ========================== ===============================================
    ``can_assign_link_flair``  Whether users can assign their own link flair.
    ``can_assign_user_flair``  Whether users can assign their own user flair.
    ``created_utc``            Time the subreddit was created, represented in
                               `Unix Time`_.
    ``description``            Subreddit description, in Markdown.
    ``description_html``       Subreddit description, in HTML.
    ``display_name``           Name of the subreddit.
    ``id``                     ID of the subreddit.
    ``name``                   Fullname of the subreddit.
    ``over18``                 Whether the subreddit is NSFW.
    ``public_description``     Description of the subreddit, shown in searches
                               and on the "You must be invited to visit this
                               community" page (if applicable).
    ``spoilers_enabled``       Whether the spoiler tag feature is enabled.
    ``subscribers``            Count of subscribers.
    ``user_is_banned``         Whether the authenticated user is banned.
    ``user_is_moderator``      Whether the authenticated user is a moderator.
    ``user_is_subscriber``     Whether the authenticated user is subscribed.
    ========================== ===============================================


    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time

    """

    # pylint: disable=too-many-public-methods

    STR_FIELD = "display_name"
    MESSAGE_PREFIX = "#"

    @staticmethod
    def _create_or_update(
        _reddit,
        allow_images=None,
        allow_post_crossposts=None,
        allow_top=None,
        collapse_deleted_comments=None,
        comment_score_hide_mins=None,
        description=None,
        domain=None,
        exclude_banned_modqueue=None,
        header_hover_text=None,
        hide_ads=None,
        lang=None,
        key_color=None,
        link_type=None,
        name=None,
        over_18=None,
        public_description=None,
        public_traffic=None,
        show_media=None,
        show_media_preview=None,
        spam_comments=None,
        spam_links=None,
        spam_selfposts=None,
        spoilers_enabled=None,
        sr=None,
        submit_link_label=None,
        submit_text=None,
        submit_text_label=None,
        subreddit_type=None,
        suggested_comment_sort=None,
        title=None,
        wiki_edit_age=None,
        wiki_edit_karma=None,
        wikimode=None,
        **other_settings
    ):
        # pylint: disable=invalid-name,too-many-locals,too-many-arguments
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
    def _subreddit_list(subreddit, other_subreddits):
        if other_subreddits:
            return ",".join(
                [str(subreddit)] + [str(x) for x in other_subreddits]
            )
        return str(subreddit)

    @property
    def _kind(self):
        """Return the class's kind."""
        return self._reddit.config.kinds["subreddit"]

    @cachedproperty
    def banned(self):
        """Provide an instance of :class:`.SubredditRelationship`.

        For example to ban a user try:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').banned.add('NAME', ban_reason='...')

        To list the banned users along with any notes, try:

        .. code-block:: python

           for ban in reddit.subreddit('SUBREDDIT').banned():
               print('{}: {}'.format(ban, ban.note))

        """
        return SubredditRelationship(self, "banned")

    @cachedproperty
    def collections(self):
        r"""Provide an instance of :class:`.SubredditCollections`.

        To see the permalinks of all :class:`.Collection`\ s that belong to
        a subreddit, try:

        .. code-block:: python

           for collection in reddit.subreddit('SUBREDDIT').collections:
               print(collection.permalink)

        To get a specific :class:`.Collection` by its UUID or permalink,
        use one of the following:

        .. code-block:: python

           collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
           collection = reddit.subreddit('SUBREDDIT').collections(
               permalink='https://reddit.com/r/SUBREDDIT/collection/some_uuid')

        """
        return self._subreddit_collections_class(self._reddit, self)

    @cachedproperty
    def contributor(self):
        """Provide an instance of :class:`.ContributorRelationship`.

        Contributors are also known as approved submitters.

        To add a contributor try:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').contributor.add('NAME')

        """
        return ContributorRelationship(self, "contributor")

    @cachedproperty
    def emoji(self):
        """Provide an instance of :class:`.SubredditEmoji`.

        This attribute can be used to discover all emoji for a subreddit:

        .. code-block:: python

           for emoji in reddit.subreddit('iama').emoji:
               print(emoji)

        A single emoji can be lazily retrieved via:

        .. code-block:: python

           reddit.subreddit('blah').emoji['emoji_name']

        .. note:: Attempting to access attributes of an nonexistent emoji will
           result in a :class:`.ClientException`.

        """
        return SubredditEmoji(self)

    @cachedproperty
    def filters(self):
        """Provide an instance of :class:`.SubredditFilters`.

        For example, to add a filter, run:

        .. code-block:: python

            reddit.subreddit('all').filters.add('subreddit_name')

        """
        return SubredditFilters(self)

    @cachedproperty
    def flair(self):
        """Provide an instance of :class:`.SubredditFlair`.

        Use this attribute for interacting with a subreddit's flair. For
        example to list all the flair for a subreddit which you have the
        ``flair`` moderator permission on try:

        .. code-block:: python

           for flair in reddit.subreddit('NAME').flair():
               print(flair)

        Flair templates can be interacted with through this attribute via:

        .. code-block:: python

           for template in reddit.subreddit('NAME').flair.templates:
               print(template)

        """
        return SubredditFlair(self)

    @cachedproperty
    def mod(self):
        """Provide an instance of :class:`.SubredditModeration`.

        For example, to accept a moderation invite from subreddit ``r/test``:

        .. code-block:: python

            reddit.subreddit('test').mod.accept_invite()
        """
        return SubredditModeration(self)

    @cachedproperty
    def moderator(self):
        """Provide an instance of :class:`.ModeratorRelationship`.

        For example to add a moderator try:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').moderator.add('NAME')

        To list the moderators along with their permissions try:

        .. code-block:: python

           for moderator in reddit.subreddit('SUBREDDIT').moderator():
               print('{}: {}'.format(moderator, moderator.mod_permissions))

        """
        return ModeratorRelationship(self, "moderator")

    @cachedproperty
    def modmail(self):
        """Provide an instance of :class:`.Modmail`.

        For example, to send a new modmail from the subreddit ``r/test`` to
        user ``u/spez`` with the subject ``test`` along with a message body of
        ``hello``:

        .. code-block:: python

            reddit.subreddit('test').modmail.create('test', 'hello', 'spez')

        """
        return Modmail(self)

    @cachedproperty
    def muted(self):
        """Provide an instance of :class:`.SubredditRelationship`.

        For example, muted users can be iterated through like so:

        .. code-block:: python

            for mute in reddit.subreddit('redditdev').muted():
                print('{}: {}'.format(mute, mute.note))

        """
        return SubredditRelationship(self, "muted")

    @cachedproperty
    def quaran(self):
        """Provide an instance of :class:`.SubredditQuarantine`.

        This property is named ``quaran`` because ``quarantine`` is a
        Subreddit attribute returned by Reddit to indicate whether or not a
        Subreddit is quarantined.

        To opt-in into a quarantined subreddit:

        .. code-block:: python

            reddit.subreddit('test').quaran.opt_in()

        """
        return SubredditQuarantine(self)

    @cachedproperty
    def stream(self):
        """Provide an instance of :class:`.SubredditStream`.

        Streams can be used to indefinitely retrieve new comments made to a
        subreddit, like:

        .. code-block:: python

           for comment in reddit.subreddit('iama').stream.comments():
               print(comment)

        Additionally, new submissions can be retrieved via the stream. In the
        following example all submissions are fetched via the special subreddit
        ``r/all``:

        .. code-block:: python

           for submission in reddit.subreddit('all').stream.submissions():
               print(submission)

        """
        return SubredditStream(self)

    @cachedproperty
    def stylesheet(self):
        """Provide an instance of :class:`.SubredditStylesheet`.

        For example, to add the css data ``.test{color:blue}`` to the existing
        stylesheet:

        .. code-block:: python

            subreddit = reddit.subreddit('SUBREDDIT')
            stylesheet = subreddit.stylesheet()
            stylesheet += ".test{color:blue}"
            subreddit.stylesheet.update(stylesheet)

        """
        return SubredditStylesheet(self)

    @cachedproperty
    def widgets(self):
        """Provide an instance of :class:`.SubredditWidgets`.

        **Example usage**

        Get all sidebar widgets:

        .. code-block:: python

           for widget in reddit.subreddit('redditdev').widgets.sidebar:
               print(widget)

        Get ID card widget:

        .. code-block:: python

           print(reddit.subreddit('redditdev').widgets.id_card)

        """
        return SubredditWidgets(self)

    @cachedproperty
    def wiki(self):
        """Provide an instance of :class:`.SubredditWiki`.

        This attribute can be used to discover all wikipages for a subreddit:

        .. code-block:: python

           for wikipage in reddit.subreddit('iama').wiki:
               print(wikipage)

        To fetch the content for a given wikipage try:

        .. code-block:: python

           wikipage = reddit.subreddit('iama').wiki['proof']
           print(wikipage.content_md)

        """
        return SubredditWiki(self)

    def __init__(self, reddit, display_name=None, _data=None):
        """Initialize a Subreddit instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param display_name: The name of the subreddit.

        .. note:: This class should not be initialized directly. Instead obtain
           an instance via: ``reddit.subreddit('subreddit_name')``

        """
        if bool(display_name) == bool(_data):
            raise TypeError(
                "Either `display_name` or `_data` must be provided."
            )
        super().__init__(reddit, _data=_data)
        if display_name:
            self.display_name = display_name
        self._path = API_PATH["subreddit"].format(subreddit=self)

    def _fetch_info(self):
        return ("subreddit_about", {"subreddit": self}, None)

    def _fetch_data(self):
        name, fields, params = self._fetch_info()
        path = API_PATH[name].format(**fields)
        return self._reddit.request("GET", path, params)

    def _fetch(self):
        data = self._fetch_data()
        data = data["data"]
        other = type(self)(self._reddit, _data=data)
        self.__dict__.update(other.__dict__)
        self._fetched = True

    def _parse_xml_response(self, response):
        """Parse the XML from a response and raise any errors found."""
        xml = response.text
        root = XML(xml)
        tags = [element.tag for element in root]
        if tags[:4] == ["Code", "Message", "ProposedSize", "MaxSizeAllowed"]:
            # Returned if image is too big
            code, message, actual, maximum_size = [
                element.text for element in root[:4]
            ]
            raise TooLargeMediaException(int(maximum_size), int(actual))

    def _submit_media(self, data, timeout, without_websockets):
        """Submit and return an `image`, `video`, or `videogif`.

        This is a helper method for submitting posts that are not link posts or
        self posts.
        """
        response = self._reddit.post(API_PATH["submit"], data=data)

        # About the websockets:
        #
        # Reddit responds to this request with only two fields: a link to
        # the user's /submitted page, and a websocket URL. We can use the
        # websocket URL to get a link to the new post once it is created.
        #
        # An important note to PRAW contributors or anyone who would
        # wish to step through this section with a debugger: This block
        # of code is NOT debugger-friendly. If there is *any*
        # significant time between the POST request just above this
        # comment and the creation of the websocket connection just
        # below, the code will become stuck in an infinite loop at the
        # connection.recv() call. I believe this is because only one message is
        # sent over the websocket, and if the client doesn't connect
        # soon enough, it will miss the message and get stuck forever
        # waiting for another.
        #
        # So if you need to debug this section of code, please let the
        # websocket creation happen right after the POST request,
        # otherwise you will have trouble.

        if without_websockets:
            return

        try:
            connection = websocket.create_connection(
                response["json"]["data"]["websocket_url"], timeout=timeout
            )
            ws_update = loads(connection.recv())
            connection.close()
        except (
            websocket.WebSocketException,
            socket.error,
            BlockingIOError,
        ) as ws_exception:
            raise WebSocketException(
                "Websocket error. Check your media file. "
                "Your post may still have been created. "
                "Use this exception's .original_exception attribute to get "
                "the original exception.",
                ws_exception,
            )
        url = ws_update["payload"]["redirect"]
        return self._reddit.submission(url=url)

    def _upload_media(self, media_path, expected_mime_prefix=None):
        """Upload media and return its URL. Uses undocumented endpoint.

        :param expected_mime_prefix: If provided, enforce that the media has a
            mime type that starts with the provided prefix.
        """
        if media_path is None:
            media_path = abspath(
                join(
                    __file__, "..", "..", "..", "..", "images", "PRAW logo.png"
                )
            )

        file_name = basename(media_path).lower()
        file_extension = file_name.rpartition(".")[2]
        mime_type = {
            "png": "image/png",
            "mov": "video/quicktime",
            "mp4": "video/mp4",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
        }.get(
            file_extension, "image/jpeg"
        )  # default to JPEG
        if (
            expected_mime_prefix is not None
            and mime_type.partition("/")[0] != expected_mime_prefix
        ):
            raise ClientException(
                "Expected a mimetype starting with {!r} but got mimetype {!r} "
                "(from file extension {!r}).".format(
                    expected_mime_prefix, mime_type, file_extension
                )
            )
        img_data = {"filepath": file_name, "mimetype": mime_type}

        url = API_PATH["media_asset"]
        # until we learn otherwise, assume this request always succeeds
        upload_lease = self._reddit.post(url, data=img_data)["args"]
        upload_url = "https:{}".format(upload_lease["action"])
        upload_data = {
            item["name"]: item["value"] for item in upload_lease["fields"]
        }

        with open(media_path, "rb") as media:
            response = self._reddit._core._requestor._http.post(
                upload_url, data=upload_data, files={"file": media}
            )
        if not response.ok:
            self._parse_xml_response(response)
        response.raise_for_status()

        return upload_url + "/" + upload_data["key"]

    def post_requirements(self):
        """Get the post requirements for a subreddit.

        :returns: A dict with the various requirements.

        The returned dict contains the following keys:

        * ``domain_blacklist``
        * ``body_restriction_policy``
        * ``domain_whitelist``
        * ``title_regexes``
        * ``body_blacklisted_strings``
        * ``body_required_strings``
        * ``title_text_min_length``
        * ``is_flair_required``
        * ``title_text_max_length``
        * ``body_regexes``
        * ``link_repost_age``
        * ``body_text_min_length``
        * ``link_restriction_policy``
        * ``body_text_max_length``
        * ``title_required_strings``
        * ``title_blacklisted_strings``
        * ``guidelines_text``
        * ``guidelines_display_policy``

        For example, to fetch the post requirements for ``r/test``:

        .. code-block:: python

            print(reddit.subreddit("test").post_requirements)

        """
        return self._reddit.get(
            API_PATH["post_requirements"].format(subreddit=str(self))
        )

    def random(self):
        """Return a random Submission.

        Returns ``None`` on subreddits that do not support the random feature.
        One example, at the time of writing, is ``r/wallpapers``.

        For example, to get a random submission off of ``r/AskReddit``:

        .. code-block:: python

            submission = reddit.subreddit("AskReddit").random()
            print(submission.title)
        """
        url = API_PATH["subreddit_random"].format(subreddit=self)
        try:
            self._reddit.get(url, params={"unique": self._reddit._next_unique})
        except Redirect as redirect:
            path = redirect.path
        try:
            return self._submission_class(
                self._reddit, url=urljoin(self._reddit.config.reddit_url, path)
            )
        except ClientException:
            return None

    def rules(self):
        """Return rules for the subreddit.

        For example to show the rules of ``r/redditdev`` try:

        .. code-block:: python

           reddit.subreddit('redditdev').rules()

        """
        return self._reddit.get(API_PATH["rules"].format(subreddit=self))

    def search(
        self,
        query,
        sort="relevance",
        syntax="lucene",
        time_filter="all",
        **generator_kwargs
    ):
        """Return a :class:`.ListingGenerator` for items that match ``query``.

        :param query: The query string to search for.
        :param sort: Can be one of: relevance, hot, top, new,
            comments. (default: relevance).
        :param syntax: Can be one of: cloudsearch, lucene, plain
            (default: lucene).
        :param time_filter: Can be one of: all, day, hour, month, week, year
            (default: all).

        For more information on building a search query see:
            https://www.reddit.com/wiki/search

        For example to search all subreddits for ``praw`` try:

        .. code-block:: python

           for submission in reddit.subreddit('all').search('praw'):
               print(submission.title)

        """
        self._validate_time_filter(time_filter)
        not_all = self.display_name.lower() != "all"
        self._safely_add_arguments(
            generator_kwargs,
            "params",
            q=query,
            restrict_sr=not_all,
            sort=sort,
            syntax=syntax,
            t=time_filter,
        )
        url = API_PATH["search"].format(subreddit=self)
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def sticky(self, number=1):
        """Return a Submission object for a sticky of the subreddit.

        :param number: Specify which sticky to return. 1 appears at the top
            (default: 1).

        Raises ``prawcore.NotFound`` if the sticky does not exist.

        For example, to get the stickied post on the subreddit ``r/test``:

        .. code-block:: python

            reddit.subreddit("test").sticky()

        """
        url = API_PATH["about_sticky"].format(subreddit=self)
        try:
            self._reddit.get(url, params={"num": number})
        except Redirect as redirect:
            path = redirect.path
        return self._submission_class(
            self._reddit, url=urljoin(self._reddit.config.reddit_url, path)
        )

    def submit(
        self,
        title,
        selftext=None,
        url=None,
        flair_id=None,
        flair_text=None,
        resubmit=True,
        send_replies=True,
        nsfw=False,
        spoiler=False,
        collection_id=None,
        discussion_type=None,
    ):
        """Add a submission to the subreddit.

        :param title: The title of the submission.
        :param selftext: The Markdown formatted content for a ``text``
            submission. Use an empty string, ``''``, to make a title-only
            submission.
        :param url: The URL for a ``link`` submission.
        :param collection_id: The UUID of a :class:`.Collection` to add the
            newly-submitted post to.
        :param flair_id: The flair template to select (default: None).
        :param flair_text: If the template's ``flair_text_editable`` value is
            True, this value will set a custom text (default: None).
        :param resubmit: When False, an error will occur if the URL has already
            been submitted (default: True).
        :param send_replies: When True, messages will be sent to the submission
            author when comments are made to the submission (default: True).
        :param nsfw: Whether or not the submission should be marked NSFW
            (default: False).
        :param spoiler: Whether or not the submission should be marked as
            a spoiler (default: False).
        :param discussion_type: Set to ``CHAT`` to enable live discussion
            instead of traditional comments (default: None).
        :returns: A :class:`~.Submission` object for the newly created
            submission.

        Either ``selftext`` or ``url`` can be provided, but not both.

        For example to submit a URL to ``r/reddit_api_test`` do:

        .. code-block:: python

           title = 'PRAW documentation'
           url = 'https://praw.readthedocs.io'
           reddit.subreddit('reddit_api_test').submit(title, url=url)

        .. note ::

           For submitting images, videos, and videogifs,
           see :meth:`.submit_image` and :meth:`.submit_video`.

        """
        if (bool(selftext) or selftext == "") == bool(url):
            raise TypeError("Either `selftext` or `url` must be provided.")

        data = {
            "sr": str(self),
            "resubmit": bool(resubmit),
            "sendreplies": bool(send_replies),
            "title": title,
            "nsfw": bool(nsfw),
            "spoiler": bool(spoiler),
            "validate_on_submit": self._reddit.validate_on_submit,
        }
        for key, value in (
            ("flair_id", flair_id),
            ("flair_text", flair_text),
            ("collection_id", collection_id),
            ("discussion_type", discussion_type),
        ):
            if value is not None:
                data[key] = value
        if selftext is not None:
            data.update(kind="self", text=selftext)
        else:
            data.update(kind="link", url=url)

        return self._reddit.post(API_PATH["submit"], data=data)

    def submit_image(
        self,
        title,
        image_path,
        flair_id=None,
        flair_text=None,
        resubmit=True,
        send_replies=True,
        nsfw=False,
        spoiler=False,
        timeout=10,
        collection_id=None,
        without_websockets=False,
        discussion_type=None,
    ):
        """Add an image submission to the subreddit.

        :param title: The title of the submission.
        :param image_path: The path to an image, to upload and post.
        :param collection_id: The UUID of a :class:`.Collection` to add the
            newly-submitted post to.
        :param flair_id: The flair template to select (default: None).
        :param flair_text: If the template's ``flair_text_editable`` value is
            True, this value will set a custom text (default: None).
        :param resubmit: When False, an error will occur if the URL has already
            been submitted (default: True).
        :param send_replies: When True, messages will be sent to the submission
            author when comments are made to the submission (default: True).
        :param nsfw: Whether or not the submission should be marked NSFW
            (default: False).
        :param spoiler: Whether or not the submission should be marked as
            a spoiler (default: False).
        :param timeout: Specifies a particular timeout, in seconds. Use to
            avoid "Websocket error" exceptions (default: 10).
        :param without_websockets: Set to ``True`` to disable use of WebSockets
            (see note below for an explanation). If ``True``, this method
            doesn't return anything. (default: ``False``).
        :param discussion_type: Set to ``CHAT`` to enable live discussion
            instead of traditional comments (default: None).
        :returns: A :class:`.Submission` object for the newly created
            submission, unless ``without_websockets`` is ``True``.

        If ``image_path`` refers to a file that is not an image, PRAW will
        raise a :class:`.ClientException`.

        .. note::

           Reddit's API uses WebSockets to respond with the link of the
           newly created post. If this fails, the method will raise
           :class:`.WebSocketException`. Occasionally, the Reddit post will
           still be created. More often, there is an error with the image
           file. If you frequently get exceptions but successfully created
           posts, try setting the ``timeout`` parameter to a value above 10.

           To disable the use of WebSockets, set ``without_websockets=True``.
           This will make the method return ``None``, though the post will
           still be created. You may wish to do this if you are running your
           program in a restricted network environment, or using a proxy
           that doesn't support WebSockets connections.

        For example to submit an image to ``r/reddit_api_test`` do:

        .. code-block:: python

           title = 'My favorite picture'
           image = '/path/to/image.png'
           reddit.subreddit('reddit_api_test').submit_image(title, image)

        """
        data = {
            "sr": str(self),
            "resubmit": bool(resubmit),
            "sendreplies": bool(send_replies),
            "title": title,
            "nsfw": bool(nsfw),
            "spoiler": bool(spoiler),
            "validate_on_submit": self._reddit.validate_on_submit,
        }
        for key, value in (
            ("flair_id", flair_id),
            ("flair_text", flair_text),
            ("collection_id", collection_id),
            ("discussion_type", discussion_type),
        ):
            if value is not None:
                data[key] = value
        data.update(
            kind="image",
            url=self._upload_media(image_path, expected_mime_prefix="image"),
        )
        return self._submit_media(
            data, timeout, without_websockets=without_websockets
        )

    def submit_video(
        self,
        title,
        video_path,
        videogif=False,
        thumbnail_path=None,
        flair_id=None,
        flair_text=None,
        resubmit=True,
        send_replies=True,
        nsfw=False,
        spoiler=False,
        timeout=10,
        collection_id=None,
        without_websockets=False,
        discussion_type=None,
    ):
        """Add a video or videogif submission to the subreddit.

        :param title: The title of the submission.
        :param video_path: The path to a video, to upload and post.
        :param videogif: A ``bool`` value. If ``True``, the video is
            uploaded as a videogif, which is essentially a silent video
            (default: ``False``).
        :param thumbnail_path: (Optional) The path to an image, to be uploaded
            and used as the thumbnail for this video. If not provided, the
            PRAW logo will be used as the thumbnail.
        :param collection_id: The UUID of a :class:`.Collection` to add the
            newly-submitted post to.
        :param flair_id: The flair template to select (default: ``None``).
        :param flair_text: If the template's ``flair_text_editable`` value is
            True, this value will set a custom text (default: ``None``).
        :param resubmit: When False, an error will occur if the URL has already
            been submitted (default: ``True``).
        :param send_replies: When True, messages will be sent to the submission
            author when comments are made to the submission
            (default: ``True``).
        :param nsfw: Whether or not the submission should be marked NSFW
            (default: False).
        :param spoiler: Whether or not the submission should be marked as
            a spoiler (default: False).
        :param timeout: Specifies a particular timeout, in seconds. Use to
            avoid "Websocket error" exceptions (default: 10).
        :param without_websockets: Set to ``True`` to disable use of WebSockets
            (see note below for an explanation). If ``True``, this method
            doesn't return anything. (default: ``False``).
        :param discussion_type: Set to ``CHAT`` to enable live discussion
            instead of traditional comments (default: None).
        :returns: A :class:`.Submission` object for the newly created
            submission, unless ``without_websockets`` is ``True``.

        If ``video_path`` refers to a file that is not a video, PRAW will
        raise a :class:`.ClientException`.

        .. note::

           Reddit's API uses WebSockets to respond with the link of the
           newly created post. If this fails, the method will raise
           :class:`.WebSocketException`. Occasionally, the Reddit post will
           still be created. More often, there is an error with the image
           file. If you frequently get exceptions but successfully created
           posts, try setting the ``timeout`` parameter to a value above 10.

           To disable the use of WebSockets, set ``without_websockets=True``.
           This will make the method return ``None``, though the post will
           still be created. You may wish to do this if you are running your
           program in a restricted network environment, or using a proxy
           that doesn't support WebSockets connections.

        For example to submit a video to ``r/reddit_api_test`` do:

        .. code-block:: python

           title = 'My favorite movie'
           video = '/path/to/video.mp4'
           reddit.subreddit('reddit_api_test').submit_video(title, video)

        """
        data = {
            "sr": str(self),
            "resubmit": bool(resubmit),
            "sendreplies": bool(send_replies),
            "title": title,
            "nsfw": bool(nsfw),
            "spoiler": bool(spoiler),
            "validate_on_submit": self._reddit.validate_on_submit,
        }
        for key, value in (
            ("flair_id", flair_id),
            ("flair_text", flair_text),
            ("collection_id", collection_id),
            ("discussion_type", discussion_type),
        ):
            if value is not None:
                data[key] = value
        data.update(
            kind="videogif" if videogif else "video",
            url=self._upload_media(video_path, expected_mime_prefix="video"),
            # if thumbnail_path is None, it uploads the PRAW logo
            video_poster_url=self._upload_media(thumbnail_path),
        )
        return self._submit_media(
            data, timeout, without_websockets=without_websockets
        )

    def subscribe(self, other_subreddits=None):
        """Subscribe to the subreddit.

        :param other_subreddits: When provided, also subscribe to the provided
            list of subreddits.

        For example, to subscribe to ``r/test``:

        .. code-block:: python

            reddit.subreddit("test").subscribe()

        """
        data = {
            "action": "sub",
            "skip_inital_defaults": True,
            "sr_name": self._subreddit_list(self, other_subreddits),
        }
        self._reddit.post(API_PATH["subscribe"], data=data)

    def traffic(self):
        """Return a dictionary of the subreddit's traffic statistics.

        Raises ``prawcore.NotFound`` when the traffic stats aren't available to
        the authenticated user, that is, they are not public and the
        authenticated user is not a moderator of the subreddit.

        The traffic method returns a dict with three keys. The keys are
        ``day``, ``hour`` and ``month``. Each key contains a list of lists with
        3 or 4 values. The first value is a timestamp indicating the start of
        the category (start of the day for the ``day`` key, start of the hour
        for the ``hour`` key, etc.). The second, third, and fourth values
        indicate the unique pageviews, total pageviews, and subscribers,
        respectively.

        .. note:: The ``hour`` key does not contain subscribers, and therefore
            each sub-list contains three values.

        For example, to get the traffic stats for ``r/test``:

        .. code-block:: python

            stats=reddit.subreddit("test").traffic()

        """
        return self._reddit.get(
            API_PATH["about_traffic"].format(subreddit=self)
        )

    def unsubscribe(self, other_subreddits=None):
        """Unsubscribe from the subreddit.

        :param other_subreddits: When provided, also unsubscribe from
            the provided list of subreddits.

        To unsubscribe from ``r/test``:

        .. code-block:: python

            reddit.subreddit('test').unsubscribe()

        """
        data = {
            "action": "unsub",
            "sr_name": self._subreddit_list(self, other_subreddits),
        }
        self._reddit.post(API_PATH["subscribe"], data=data)


WidgetEncoder._subreddit_class = Subreddit
