"""Provide the Subreddit class."""
# pylint: disable=too-many-lines
from copy import deepcopy
from json import dumps, loads
from os.path import basename, dirname, join

from prawcore import Redirect
import websocket

from ...compat import urljoin
from ...const import API_PATH, JPEG_HEADER
from ...exceptions import APIException, ClientException
from ...util.cache import cachedproperty
from ..util import permissions_string, stream_generator
from ..listing.generator import ListingGenerator
from ..listing.mixins import SubredditListingMixin
from .base import RedditBase
from .emoji import SubredditEmoji
from .mixins import FullnameMixin, MessageableMixin
from .modmail import ModmailConversation
from .widgets import SubredditWidgets
from .wikipage import WikiPage


class Subreddit(
    MessageableMixin, SubredditListingMixin, FullnameMixin, RedditBase
):
    """A class for Subreddits.

    To obtain an instance of this class for subreddit ``/r/redditdev`` execute:

    .. code:: python

       subreddit = reddit.subreddit('redditdev')

    While ``/r/all`` is not a real subreddit, it can still be treated like
    one. The following outputs the titles of the 25 hottest submissions in
    ``/r/all``:

    .. code:: python

       for submission in reddit.subreddit('all').hot(limit=25):
           print(submission.title)

    Multiple subreddits can be combined like so:

    .. code:: python

       for submission in reddit.subreddit('redditdev+learnpython').top('all'):
           print(submission)

    Subreddits can be filtered from combined listings as follows. Note that
    these filters are ignored by certain methods, including
    :attr:`~praw.models.Subreddit.comments`,
    :meth:`~praw.models.Subreddit.gilded`, and
    :meth:`.SubredditStream.comments`.

    .. code:: python

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

        .. code:: python

           for emoji in reddit.subreddit('iama').emoji:
               print(emoji)

        A single emoji can be lazily retrieved via:

        .. code:: python

           reddit.subreddit('blah').emoji['emoji_name']

        .. note:: Attempting to access attributes of an nonexistent emoji will
           result in a :class:`.ClientException`.

        """
        return SubredditEmoji(self)

    @cachedproperty
    def filters(self):
        """Provide an instance of :class:`.SubredditFilters`."""
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
        """Provide an instance of :class:`.SubredditModeration`."""
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
        """Provide an instance of :class:`.Modmail`."""
        return Modmail(self)

    @cachedproperty
    def muted(self):
        """Provide an instance of :class:`.SubredditRelationship`."""
        return SubredditRelationship(self, "muted")

    @cachedproperty
    def quaran(self):
        """Provide an instance of :class:`.SubredditQuarantine`.

        This property is named ``quaran`` because ``quarantine`` is a
        Subreddit attribute returned by Reddit to indicate whether or not a
        Subreddit is quarantined.

        """
        return SubredditQuarantine(self)

    @cachedproperty
    def stream(self):
        """Provide an instance of :class:`.SubredditStream`.

        Streams can be used to indefinitely retrieve new comments made to a
        subreddit, like:

        .. code:: python

           for comment in reddit.subreddit('iama').stream.comments():
               print(comment)

        Additionally, new submissions can be retrieved via the stream. In the
        following example all submissions are fetched via the special subreddit
        ``all``:

        .. code:: python

           for submission in reddit.subreddit('all').stream.submissions():
               print(submission)

        """
        return SubredditStream(self)

    @cachedproperty
    def stylesheet(self):
        """Provide an instance of :class:`.SubredditStylesheet`."""
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

        .. code:: python

           for wikipage in reddit.subreddit('iama').wiki:
               print(wikipage)

        To fetch the content for a given wikipage try:

        .. code:: python

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
        super(Subreddit, self).__init__(reddit, _data=_data)
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

    def _submit_media(self, data, timeout):
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
        # socket.recv() call. I believe this is because only one message is
        # sent over the websocket, and if the client doesn't connect
        # soon enough, it will miss the message and get stuck forever
        # waiting for another.
        #
        # So if you need to debug this section of code, please let the
        # websocket creation happen right after the POST request,
        # otherwise you will have trouble.

        if not isinstance(response, dict):
            raise ClientException(
                "Something went wrong with your post: {!r}".format(response)
            )

        try:
            socket = websocket.create_connection(
                response["json"]["data"]["websocket_url"], timeout=timeout
            )
            ws_update = loads(socket.recv())
            socket.close()
        except websocket.WebSocketTimeoutException:
            raise ClientException(
                "Websocket error. Check your media file. "
                "Your post may still have been created."
            )
        url = ws_update["payload"]["redirect"]
        return self._reddit.submission(url=url)

    def _upload_media(self, media_path):
        """Upload media and return its URL. Uses undocumented endpoint."""
        if media_path is None:
            media_path = join(
                dirname(dirname(dirname(__file__))), "images", "PRAW logo.png"
            )

        file_name = basename(media_path).lower()
        mime_type = {
            "png": "image/png",
            "mov": "video/quicktime",
            "mp4": "video/mp4",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
        }.get(
            file_name.rpartition(".")[2], "image/jpeg"
        )  # default to JPEG
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
        response.raise_for_status()

        return upload_url + "/" + upload_data["key"]

    def random(self):
        """Return a random Submission.

        Returns ``None`` on subreddits that do not support the random feature.
        One example, at the time of writing, is /r/wallpapers.
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

        For example to show the rules of ``/r/redditdev`` try:

        .. code:: python

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
        """Return a ListingGenerator for items that match ``query``.

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

        .. code:: python

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
    ):
        """Add a submission to the subreddit.

        :param title: The title of the submission.
        :param selftext: The markdown formatted content for a ``text``
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
        :returns: A :class:`~.Submission` object for the newly created
            submission.

        Either ``selftext`` or ``url`` can be provided, but not both.

        For example to submit a URL to ``/r/reddit_api_test`` do:

        .. code:: python

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
        }
        for key, value in (
            ("flair_id", flair_id),
            ("flair_text", flair_text),
            ("collection_id", collection_id),
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

        .. note::

           Reddit's API uses WebSockets to respond with the link of the
           newly created post. If this fails, the method will raise
           :class:`.ClientException`. Occasionally, the Reddit post will still
           be created. More often, there is an error with the image file. If
           you frequently get exceptions but successfully created posts, try
           setting the ``timeout`` parameter to a value above 10.

        :returns: A :class:`~.Submission` object for the newly created
            submission.

        For example to submit an image to ``/r/reddit_api_test`` do:

        .. code:: python

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
        }
        for key, value in (
            ("flair_id", flair_id),
            ("flair_text", flair_text),
            ("collection_id", collection_id),
        ):
            if value is not None:
                data[key] = value
        data.update(kind="image", url=self._upload_media(image_path))
        return self._submit_media(data, timeout)

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

        .. note::

           Reddit's API uses WebSockets to respond with the link of the
           newly created post. If this fails, the method will raise
           :class:`.ClientException`. Occasionally, the Reddit post will still
           be created. More often, there is an error with the video file. If
           you frequently get exceptions but successfully created posts, try
           setting the ``timeout`` parameter to a value above 10.

        :returns: A :class:`~.Submission` object for the newly created
            submission.

        For example to submit a video to ``/r/reddit_api_test`` do:

        .. code:: python

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
        }
        for key, value in (
            ("flair_id", flair_id),
            ("flair_text", flair_text),
            ("collection_id", collection_id),
        ):
            if value is not None:
                data[key] = value
        data.update(
            kind="videogif" if videogif else "video",
            url=self._upload_media(video_path),
            # if thumbnail_path is None, it uploads the PRAW logo
            video_poster_url=self._upload_media(thumbnail_path),
        )
        return self._submit_media(data, timeout)

    def subscribe(self, other_subreddits=None):
        """Subscribe to the subreddit.

        :param other_subreddits: When provided, also subscribe to the provided
            list of subreddits.

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

        """
        return self._reddit.get(
            API_PATH["about_traffic"].format(subreddit=self)
        )

    def unsubscribe(self, other_subreddits=None):
        """Unsubscribe from the subreddit.

        :param other_subreddits: When provided, also unsubscribe to the
            provided list of subreddits.

        """
        data = {
            "action": "unsub",
            "sr_name": self._subreddit_list(self, other_subreddits),
        }
        self._reddit.post(API_PATH["subscribe"], data=data)


class SubredditFilters(object):
    """Provide functions to interact with the special Subreddit's filters.

    Members of this class should be utilized via ``Subreddit.filters``. For
    example to add a filter run:

    .. code:: python

       reddit.subreddit('all').filters.add('subreddit_name')

    """

    def __init__(self, subreddit):
        """Create a SubredditFilters instance.

        :param subreddit: The special subreddit whose filters to work with.

        As of this writing filters can only be used with the special subreddits
        ``all`` and ``mod``.

        """
        self.subreddit = subreddit

    def __iter__(self):
        """Iterate through the special subreddit's filters.

        This method should be invoked as:

        .. code:: python

           for subreddit in reddit.subreddit('NAME').filters:
               ...

        """
        url = API_PATH["subreddit_filter_list"].format(
            special=self.subreddit, user=self.subreddit._reddit.user.me()
        )
        params = {"unique": self.subreddit._reddit._next_unique}
        response_data = self.subreddit._reddit.get(url, params=params)
        for subreddit in response_data.subreddits:
            yield subreddit

    def add(self, subreddit):
        """Add ``subreddit`` to the list of filtered subreddits.

        :param subreddit: The subreddit to add to the filter list.

        Items from subreddits added to the filtered list will no longer be
        included when obtaining listings for ``/r/all``.

        Alternatively, you can filter a subreddit temporarily from a special
        listing in a manner like so:

        .. code:: python

           reddit.subreddit('all-redditdev-learnpython')

        Raises ``prawcore.NotFound`` when calling on a non-special subreddit.

        """
        url = API_PATH["subreddit_filter"].format(
            special=self.subreddit,
            user=self.subreddit._reddit.user.me(),
            subreddit=subreddit,
        )
        self.subreddit._reddit.request(
            "PUT", url, data={"model": dumps({"name": str(subreddit)})}
        )

    def remove(self, subreddit):
        """Remove ``subreddit`` from the list of filtered subreddits.

        :param subreddit: The subreddit to remove from the filter list.

        Raises ``prawcore.NotFound`` when calling on a non-special subreddit.

        """
        url = API_PATH["subreddit_filter"].format(
            special=self.subreddit,
            user=self.subreddit._reddit.user.me(),
            subreddit=str(subreddit),
        )
        self.subreddit._reddit.request("DELETE", url, data={})


class SubredditFlair(object):
    """Provide a set of functions to interact with a Subreddit's flair."""

    @cachedproperty
    def link_templates(self):
        """Provide an instance of :class:`.SubredditLinkFlairTemplates`.

        Use this attribute for interacting with a subreddit's link flair
        templates. For example to list all the link flair templates for a
        subreddit which you have the ``flair`` moderator permission on try:

        .. code-block:: python

           for template in reddit.subreddit('NAME').flair.link_templates:
               print(template)

        """
        return SubredditLinkFlairTemplates(self.subreddit)

    @cachedproperty
    def templates(self):
        """Provide an instance of :class:`.SubredditRedditorFlairTemplates`.

        Use this attribute for interacting with a subreddit's flair
        templates. For example to list all the flair templates for a subreddit
        which you have the ``flair`` moderator permission on try:

        .. code-block:: python

           for template in reddit.subreddit('NAME').flair.templates:
               print(template)

        """
        return SubredditRedditorFlairTemplates(self.subreddit)

    def __call__(self, redditor=None, **generator_kwargs):
        """Return a generator for Redditors and their associated flair.

        :param redditor: When provided, yield at most a single
            :class:`~.Redditor` instance (default: None).

        This method is intended to be used like:

        .. code-block:: python

           for flair in reddit.subreddit('NAME').flair(limit=None):
               print(flair)

        """
        Subreddit._safely_add_arguments(
            generator_kwargs, "params", name=redditor
        )
        generator_kwargs.setdefault("limit", None)
        url = API_PATH["flairlist"].format(subreddit=self.subreddit)
        return ListingGenerator(
            self.subreddit._reddit, url, **generator_kwargs
        )

    def __init__(self, subreddit):
        """Create a SubredditFlair instance.

        :param subreddit: The subreddit whose flair to work with.

        """
        self.subreddit = subreddit

    def configure(
        self,
        position="right",
        self_assign=False,
        link_position="left",
        link_self_assign=False,
        **settings
    ):
        """Update the subreddit's flair configuration.

        :param position: One of left, right, or False to disable (default:
            right).
        :param self_assign: (boolean) Permit self assignment of user flair
            (default: False).
        :param link_position: One of left, right, or False to disable
            (default: left).
        :param link_self_assign: (boolean) Permit self assignment
               of link flair (default: False).

        Additional keyword arguments can be provided to handle new settings as
        Reddit introduces them.

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

    def delete(self, redditor):
        """Delete flair for a Redditor.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        .. note:: To delete the flair of many Redditors at once, please see
                  :meth:`~praw.models.reddit.subreddit.SubredditFlair.update`.

        """
        url = API_PATH["deleteflair"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data={"name": str(redditor)})

    def delete_all(self):
        """Delete all Redditor flair in the Subreddit.

        :returns: List of dictionaries indicating the success or failure of
            each delete.

        """
        return self.update(x["user"] for x in self())

    def set(
        self, redditor=None, text="", css_class="", flair_template_id=None
    ):
        """Set flair for a Redditor.

        :param redditor: (Required) A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param text: The flair text to associate with the Redditor or
            Submission (default: '').
        :param css_class: The css class to associate with the flair html
            (default: ''). Use either this or ``flair_template_id``.
        :param flair_template_id: The ID of the flair template to be used
            (default: ``None``). Use either this or ``css_class``.

        This method can only be used by an authenticated user who is a
        moderator of the associated Subreddit.

        Example:

        .. code:: python

           reddit.subreddit('redditdev').flair.set('bboe', 'PRAW author',
                                                   css_class='mods')
           template = '6bd28436-1aa7-11e9-9902-0e05ab0fad46'
           reddit.subreddit('redditdev').flair.set('spez', 'Reddit CEO',
                                                   flair_template_id=template)

        """
        if css_class and flair_template_id is not None:
            raise TypeError(
                "Parameter `css_class` cannot be used in "
                "conjunction with `flair_template_id`."
            )
        data = {"name": str(redditor), "text": text}
        if flair_template_id is not None:
            data["flair_template_id"] = flair_template_id
            url = API_PATH["select_flair"].format(subreddit=self.subreddit)
        else:
            data["css_class"] = css_class
            url = API_PATH["flair"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def update(self, flair_list, text="", css_class=""):
        """Set or clear the flair for many Redditors at once.

        :param flair_list: Each item in this list should be either: the name of
            a Redditor, an instance of :class:`.Redditor`, or a dictionary
            mapping keys ``user``, ``flair_text``, and ``flair_css_class`` to
            their respective values. The ``user`` key should map to a Redditor,
            as described above. When a dictionary isn't provided, or the
            dictionary is missing one of ``flair_text``, or ``flair_css_class``
            attributes the default values will come from the the following
            arguments.

        :param text: The flair text to use when not explicitly provided in
            ``flair_list`` (default: '').
        :param css_class: The css class to use when not explicitly provided in
            ``flair_list`` (default: '').
        :returns: List of dictionaries indicating the success or failure of
            each update.

        For example to clear the flair text, and set the ``praw`` flair css
        class on a few users try:

        .. code:: python

           subreddit.flair.update(['bboe', 'spez', 'spladug'],
                                  css_class='praw')

        """
        lines = []
        for item in flair_list:
            if isinstance(item, dict):
                fmt_data = (
                    str(item["user"]),
                    item.get("flair_text", text),
                    item.get("flair_css_class", css_class),
                )
            else:
                fmt_data = (str(item), text, css_class)
            lines.append('"{}","{}","{}"'.format(*fmt_data))

        response = []
        url = API_PATH["flaircsv"].format(subreddit=self.subreddit)
        while lines:
            data = {"flair_csv": "\n".join(lines[:100])}
            response.extend(self.subreddit._reddit.post(url, data=data))
            lines = lines[100:]
        return response


class SubredditFlairTemplates(object):
    """Provide functions to interact with a Subreddit's flair templates."""

    @staticmethod
    def flair_type(is_link):
        """Return LINK_FLAIR or USER_FLAIR depending on ``is_link`` value."""
        return "LINK_FLAIR" if is_link else "USER_FLAIR"

    def __init__(self, subreddit):
        """Create a SubredditFlairTemplate instance.

        :param subreddit: The subreddit whose flair templates to work with.

        .. note:: This class should not be initialized directly. Instead obtain
           an instance via:
           ``reddit.subreddit('subreddit_name').flair.templates`` or
           ``reddit.subreddit('subreddit_name').flair.link_templates``.

        """
        self.subreddit = subreddit

    def _add(
        self,
        text,
        css_class="",
        text_editable=False,
        is_link=None,
        background_color=None,
        text_color=None,
        mod_only=None,
    ):
        if css_class and any(
            param is not None
            for param in (background_color, text_color, mod_only)
        ):
            raise TypeError(
                "Parameter `css_class` cannot be used in "
                "conjunction with parameters `background_color`, "
                "`text_color`, or `mod_only`."
            )
        if css_class:
            url = API_PATH["flairtemplate"].format(subreddit=self.subreddit)
            data = {
                "css_class": css_class,
                "flair_type": self.flair_type(is_link),
                "text": text,
                "text_editable": bool(text_editable),
            }
        else:
            url = API_PATH["flairtemplate_v2"].format(subreddit=self.subreddit)
            data = {
                "background_color": background_color,
                "text_color": text_color,
                "flair_type": self.flair_type(is_link),
                "text": text,
                "text_editable": bool(text_editable),
                "mod_only": bool(mod_only),
            }
        self.subreddit._reddit.post(url, data=data)

    def _clear(self, is_link=None):
        url = API_PATH["flairtemplateclear"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(
            url, data={"flair_type": self.flair_type(is_link)}
        )

    def delete(self, template_id):
        """Remove a flair template provided by ``template_id``.

        For example, to delete the first Redditor flair template listed, try:

        .. code-block:: python

           template_info = list(subreddit.flair.templates)[0]
           subreddit.flair.templates.delete(template_info['id'])

        """
        url = API_PATH["flairtemplatedelete"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(
            url, data={"flair_template_id": template_id}
        )

    def update(
        self,
        template_id,
        text,
        css_class="",
        text_editable=False,
        background_color=None,
        text_color=None,
        mod_only=None,
    ):
        """Update the flair template provided by ``template_id``.

        :param template_id: The flair template to update.
        :param text: The flair template's new text (required).
        :param css_class: The flair template's new css_class (default: '').
            Cannot be used in conjunction with ``background_color``,
            ``text_color``, or ``mod_only``.
        :param text_editable: (boolean) Indicate if the flair text can be
            modified for each Redditor that sets it (default: False).
        :param background_color: The flair template's new background color,
            as a hex color. Cannot be used in conjunction with ``css_class``.
        :param text_color: The flair template's new text color, either
            ``'light'`` or ``'dark'``. Cannot be used in conjunction with
            ``css_class``.
        :param mod_only: (boolean) Indicate if the flair can only be used by
            moderators. Cannot be used in conjunction with ``css_class``.

        For example to make a user flair template text_editable, try:

        .. code-block:: python

           template_info = list(subreddit.flair.templates)[0]
           subreddit.flair.templates.update(
               template_info['id'],
               template_info['flair_text'],
               text_editable=True)

        .. note::

           Any parameters not provided will be set to default values (usually
           ``None`` or ``False``) on Reddit's end.

        """
        if css_class and any(
            param is not None
            for param in (background_color, text_color, mod_only)
        ):
            raise TypeError(
                "Parameter `css_class` cannot be used in "
                "conjunction with parameters `background_color`, "
                "`text_color`, or `mod_only`."
            )

        if css_class:
            url = API_PATH["flairtemplate"].format(subreddit=self.subreddit)
            data = {
                "css_class": css_class,
                "flair_template_id": template_id,
                "text": text,
                "text_editable": bool(text_editable),
            }
        else:
            url = API_PATH["flairtemplate_v2"].format(subreddit=self.subreddit)
            data = {
                "flair_template_id": template_id,
                "text": text,
                "background_color": background_color,
                "text_color": text_color,
                "text_editable": text_editable,
                "mod_only": mod_only,
            }
        self.subreddit._reddit.post(url, data=data)


class SubredditRedditorFlairTemplates(SubredditFlairTemplates):
    """Provide functions to interact with Redditor flair templates."""

    def __iter__(self):
        """Iterate through the user flair templates.

        Example:

        .. code-block:: python

           for template in reddit.subreddit('NAME').flair.templates:
               print(template)


        """
        url = API_PATH["user_flair"].format(subreddit=self.subreddit)
        params = {"unique": self.subreddit._reddit._next_unique}
        for template in self.subreddit._reddit.get(url, params=params):
            yield template

    def add(
        self,
        text,
        css_class="",
        text_editable=False,
        background_color=None,
        text_color=None,
        mod_only=None,
    ):
        """Add a Redditor flair template to the associated subreddit.

        :param text: The flair template's text (required).
        :param css_class: The flair template's css_class (default: '').
            Cannot be used in conjunction with ``background_color``,
            ``text_color``, or ``mod_only``.
        :param text_editable: (boolean) Indicate if the flair text can be
            modified for each Redditor that sets it (default: False).
        :param background_color: The flair template's new background color,
            as a hex color. Cannot be used in conjunction with ``css_class``.
        :param text_color: The flair template's new text color, either
            ``'light'`` or ``'dark'``. Cannot be used in conjunction with
            ``css_class``.
        :param mod_only: (boolean) Indicate if the flair can only be used by
            moderators. Cannot be used in conjunction with ``css_class``.

        For example, to add an editable Redditor flair try:

        .. code-block:: python

           reddit.subreddit('NAME').flair.templates.add(
               css_class='praw', text_editable=True)

        """
        self._add(
            text,
            css_class=css_class,
            text_editable=text_editable,
            is_link=False,
            background_color=background_color,
            text_color=text_color,
            mod_only=mod_only,
        )

    def clear(self):
        """Remove all Redditor flair templates from the subreddit.

        For example:

        .. code-block:: python

           reddit.subreddit('NAME').flair.templates.clear()

        """
        self._clear(is_link=False)


class SubredditLinkFlairTemplates(SubredditFlairTemplates):
    """Provide functions to interact with link flair templates."""

    def __iter__(self):
        """Iterate through the link flair templates.

        Example:

        .. code-block:: python

           for template in reddit.subreddit('NAME').flair.link_templates:
               print(template)


        """
        url = API_PATH["link_flair"].format(subreddit=self.subreddit)
        for template in self.subreddit._reddit.get(url):
            yield template

    def add(
        self,
        text,
        css_class="",
        text_editable=False,
        background_color=None,
        text_color=None,
        mod_only=None,
    ):
        """Add a link flair template to the associated subreddit.

        :param text: The flair template's text (required).
        :param css_class: The flair template's css_class (default: '').
            Cannot be used in conjunction with ``background_color``,
            ``text_color``, or ``mod_only``.
        :param text_editable: (boolean) Indicate if the flair text can be
            modified for each Redditor that sets it (default: False).
        :param background_color: The flair template's new background color,
            as a hex color. Cannot be used in conjunction with ``css_class``.
        :param text_color: The flair template's new text color, either
            ``'light'`` or ``'dark'``. Cannot be used in conjunction with
            ``css_class``.
        :param mod_only: (boolean) Indicate if the flair can only be used by
            moderators. Cannot be used in conjunction with ``css_class``.

        For example, to add an editable link flair try:

        .. code-block:: python

           reddit.subreddit('NAME').flair.link_templates.add(
               css_class='praw', text_editable=True)

        """
        self._add(
            text,
            css_class=css_class,
            text_editable=text_editable,
            is_link=True,
            background_color=background_color,
            text_color=text_color,
            mod_only=mod_only,
        )

    def clear(self):
        """Remove all link flair templates from the subreddit.

        For example:

        .. code-block:: python

           reddit.subreddit('NAME').flair.link_templates.clear()

        """
        self._clear(is_link=True)


class SubredditModeration(object):
    """Provides a set of moderation functions to a Subreddit."""

    @staticmethod
    def _handle_only(only, generator_kwargs):
        if only is not None:
            if only == "submissions":
                only = "links"
            RedditBase._safely_add_arguments(
                generator_kwargs, "params", only=only
            )

    def __init__(self, subreddit):
        """Create a SubredditModeration instance.

        :param subreddit: The subreddit to moderate.

        """
        self.subreddit = subreddit

    def accept_invite(self):
        """Accept an invitation as a moderator of the community."""
        url = API_PATH["accept_mod_invite"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def edited(self, only=None, **generator_kwargs):
        """Return a ListingGenerator for edited comments and submissions.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print all items in the edited queue try:

        .. code:: python

           for item in reddit.subreddit('mod').mod.edited(limit=None):
               print(item)

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_edited"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def inbox(self, **generator_kwargs):
        """Return a ListingGenerator for moderator messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        See ``unread`` for unread moderator messages.

        To print the last 5 moderator mail messages and their replies, try:

        .. code:: python

           for message in reddit.subreddit('mod').mod.inbox(limit=5):
               print("From: {}, Body: {}".format(message.author, message.body))
               for reply in message.replies:
                   print("From: {}, Body: {}".format(reply.author, reply.body))

        """
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["moderator_messages"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def log(self, action=None, mod=None, **generator_kwargs):
        """Return a ListingGenerator for moderator log entries.

        :param action: If given, only return log entries for the specified
            action.
        :param mod: If given, only return log entries for actions made by the
            passed in Redditor.

        To print the moderator and subreddit of the last 5 modlog entries try:

        .. code:: python

           for log in reddit.subreddit('mod').mod.log(limit=5):
               print("Mod: {}, Subreddit: {}".format(log.mod, log.subreddit))

        """
        params = {"mod": str(mod) if mod else mod, "type": action}
        Subreddit._safely_add_arguments(generator_kwargs, "params", **params)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_log"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def modqueue(self, only=None, **generator_kwargs):
        """Return a ListingGenerator for comments/submissions in the modqueue.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print all modqueue items try:

        .. code:: python

           for item in reddit.subreddit('mod').mod.modqueue(limit=None):
               print(item)

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_modqueue"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def reports(self, only=None, **generator_kwargs):
        """Return a ListingGenerator for reported comments and submissions.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the user and mod report reasons in the report queue try:

        .. code:: python

           for reported_item in reddit.subreddit('mod').mod.reports():
               print("User Reports: {}".format(reported_item.user_reports))
               print("Mod Reports: {}".format(reported_item.mod_reports))

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_reports"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def settings(self):
        """Return a dictionary of the subreddit's current settings."""
        url = API_PATH["subreddit_settings"].format(subreddit=self.subreddit)
        return self.subreddit._reddit.get(url)["data"]

    def spam(self, only=None, **generator_kwargs):
        """Return a ListingGenerator for spam comments and submissions.

        :param only: If specified, one of ``'comments'``, or ``'submissions'``
            to yield only results of that type.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the items in the spam queue try:

        .. code:: python

           for item in reddit.subreddit('mod').mod.spam():
               print(item)

        """
        self._handle_only(only, generator_kwargs)
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_spam"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def unmoderated(self, **generator_kwargs):
        """Return a ListingGenerator for unmoderated submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print the items in the unmoderated queue try:

        .. code:: python

           for item in reddit.subreddit('mod').mod.unmoderated():
               print(item)

        """
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["about_unmoderated"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def unread(self, **generator_kwargs):
        """Return a ListingGenerator for unread moderator messages.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        See ``inbox`` for all messages.

        To print the mail in the unread modmail queue try:

        .. code:: python

           for message in reddit.subreddit('mod').mod.unread():
               print("From: {}, To: {}".format(message.author, message.dest))

        """
        return ListingGenerator(
            self.subreddit._reddit,
            API_PATH["moderator_unread"].format(subreddit=self.subreddit),
            **generator_kwargs
        )

    def update(self, **settings):
        """Update the subreddit's settings.

        :param allow_images: Allow users to upload images using the native
            image hosting. Only applies to link-only subreddits.
        :param allow_post_crossposts: Allow users to crosspost submissions from
            other subreddits.
        :param allow_top: Allow the subreddit to appear on ``/r/all`` as well
            as the default and trending lists.
        :param collapse_deleted_comments: Collapse deleted and removed comments
            on comments pages by default.
        :param comment_score_hide_mins: The number of minutes to hide comment
            scores.
        :param description: Shown in the sidebar of your subreddit.
        :param disable_contributor_requests: Specifies whether redditors may
            send automated modmail messages requesting approval as a submitter.
        :type disable_contributor_requests: bool
        :param domain: Domain name with a cname that points to
            {subreddit}.reddit.com.
        :param exclude_banned_modqueue: Exclude posts by site-wide banned users
            from modqueue/unmoderated.
        :param header_hover_text: The text seen when hovering over the snoo.
        :param hide_ads: Don't show ads within this subreddit. Only applies to
            gold-user only subreddits.
        :param key_color: A 6-digit rgb hex color (e.g. ``'#AABBCC'``), used as
            a thematic color for your subreddit on mobile.
        :param lang: A valid IETF language tag (underscore separated).
        :param link_type: The types of submissions users can make.
            One of ``any``, ``link``, ``self``.
        :param over_18: Viewers must be over 18 years old (i.e. NSFW).
        :param public_description: Public description blurb. Appears in search
            results and on the landing page for private subreddits.
        :param public_traffic: Make the traffic stats page public.
        :param restrict_commenting: Specifies whether approved users have the
            ability to comment.
        :type restrict_commenting: bool
        :param restrict_posting: Specifies whether approved users have the
            ability to submit posts.
        :type restrict_posting: bool
        :param show_media: Show thumbnails on submissions.
        :param show_media_preview: Expand media previews on comments pages.
        :param spam_comments: Spam filter strength for comments.
            One of ``all``, ``low``, ``high``.
        :param spam_links: Spam filter strength for links.
            One of ``all``, ``low``, ``high``.
        :param spam_selfposts: Spam filter strength for selfposts.
            One of ``all``, ``low``, ``high``.
        :param spoilers_enabled: Enable marking posts as containing spoilers.
        :param sr: The fullname of the subreddit whose settings will be
            updated.
        :param submit_link_label: Custom label for submit link button
            (None for default).
        :param submit_text: Text to show on submission page.
        :param submit_text_label: Custom label for submit text post button
            (None for default).
        :param subreddit_type: One of ``archived``, ``employees_only``,
            ``gold_only``, ``gold_restricted``, ``private``, ``public``,
            ``restricted``.
        :param suggested_comment_sort: All comment threads will use this
            sorting method by default. Leave None, or choose one of
            ``confidence``, ``controversial``, ``new``, ``old``, ``qa``,
            ``random``, ``top``.
        :param title: The title of the subreddit.
        :param wiki_edit_age: Account age, in days, required to edit and create
            wiki pages.
        :param wiki_edit_karma: Subreddit karma required to edit and create
            wiki pages.
        :param wikimode: One of  ``anyone``, ``disabled``, ``modonly``.

        Additional keyword arguments can be provided to handle new settings as
        Reddit introduces them.

        Settings that are documented here and aren't explicitly set by you in a
        call to :meth:`.SubredditModeration.update` should retain their current
        value. If they do not please file a bug.

        .. warning:: Undocumented settings, or settings that were very recently
                     documented, may not retain their current value when
                     updating. This often occurs when Reddit adds a new setting
                     but forgets to add that setting to the API endpoint that
                     is used to fetch the current settings.

        """
        current_settings = self.settings()
        fullname = current_settings.pop("subreddit_id")

        # These attributes come out using different names than they go in.
        remap = {
            "allow_top": "default_set",
            "lang": "language",
            "link_type": "content_options",
        }
        for (new, old) in remap.items():
            current_settings[new] = current_settings.pop(old)

        current_settings.update(settings)
        return Subreddit._create_or_update(
            _reddit=self.subreddit._reddit, sr=fullname, **current_settings
        )


class SubredditQuarantine(object):
    """Provides subreddit quarantine related methods."""

    def __init__(self, subreddit):
        """Create a SubredditQuarantine instance.

        :param subreddit: The subreddit associated with the quarantine.

        """
        self.subreddit = subreddit

    def opt_in(self):
        """Permit your user access to the quarantined subreddit.

        Usage:

        .. code:: python

           subreddit = reddit.subreddit('QUESTIONABLE')
           next(subreddit.hot())  # Raises prawcore.Forbidden

           subreddit.quaran.opt_in()
           next(subreddit.hot())  # Returns Submission

        """
        data = {"sr_name": self.subreddit}
        try:
            self.subreddit._reddit.post(
                API_PATH["quarantine_opt_in"], data=data
            )
        except Redirect:
            pass

    def opt_out(self):
        """Remove access to the quarantined subreddit.

        Usage:

        .. code:: python

           subreddit = reddit.subreddit('QUESTIONABLE')
           next(subreddit.hot())  # Returns Submission

           subreddit.quaran.opt_out()
           next(subreddit.hot())  # Raises prawcore.Forbidden

        """
        data = {"sr_name": self.subreddit}
        try:
            self.subreddit._reddit.post(
                API_PATH["quarantine_opt_out"], data=data
            )
        except Redirect:
            pass


class SubredditRelationship(object):
    """Represents a relationship between a redditor and subreddit.

    Instances of this class can be iterated through in order to discover the
    Redditors that make up the relationship.

    For example, banned users of a subreddit can be iterated through like so:

    .. code-block:: python

       for ban in reddit.subreddit('redditdev').banned():
           print('{}: {}'.format(ban, ban.note))

    """

    def __call__(self, redditor=None, **generator_kwargs):
        """Return a generator for Redditors belonging to this relationship.

        :param redditor: When provided, yield at most a single
            :class:`~.Redditor` instance. This is useful to confirm if a
            relationship exists, or to fetch the metadata associated with a
            particular relationship (default: None).

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        Subreddit._safely_add_arguments(
            generator_kwargs, "params", user=redditor
        )
        url = API_PATH["list_{}".format(self.relationship)].format(
            subreddit=self.subreddit
        )
        return ListingGenerator(
            self.subreddit._reddit, url, **generator_kwargs
        )

    def __init__(self, subreddit, relationship):
        """Create a SubredditRelationship instance.

        :param subreddit: The subreddit for the relationship.
        :param relationship: The name of the relationship.

        """
        self.relationship = relationship
        self.subreddit = subreddit

    def add(self, redditor, **other_settings):
        """Add ``redditor`` to this relationship.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        """
        data = {"name": str(redditor), "type": self.relationship}
        data.update(other_settings)
        url = API_PATH["friend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def remove(self, redditor):
        """Remove ``redditor`` from this relationship.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        """
        data = {"name": str(redditor), "type": self.relationship}
        url = API_PATH["unfriend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)


class ContributorRelationship(SubredditRelationship):
    """Provides methods to interact with a Subreddit's contributors.

    Contributors are also known as approved submitters.

    Contributors of a subreddit can be iterated through like so:

    .. code-block:: python

       for contributor in reddit.subreddit('redditdev').contributor():
           print(contributor)

    """

    def leave(self):
        """Abdicate the contributor position."""
        self.subreddit._reddit.post(
            API_PATH["leavecontributor"], data={"id": self.subreddit.fullname}
        )


class ModeratorRelationship(SubredditRelationship):
    """Provides methods to interact with a Subreddit's moderators.

    Moderators of a subreddit can be iterated through like so:

    .. code-block:: python

       for moderator in reddit.subreddit('redditdev').moderator():
           print(moderator)

    """

    PERMISSIONS = {"access", "config", "flair", "mail", "posts", "wiki"}

    @staticmethod
    def _handle_permissions(permissions, other_settings):
        other_settings = deepcopy(other_settings) if other_settings else {}
        other_settings["permissions"] = permissions_string(
            permissions, ModeratorRelationship.PERMISSIONS
        )
        return other_settings

    def __call__(self, redditor=None):  # pylint: disable=arguments-differ
        """Return a list of Redditors who are moderators.

        :param redditor: When provided, return a list containing at most one
            :class:`~.Redditor` instance. This is useful to confirm if a
            relationship exists, or to fetch the metadata associated with a
            particular relationship (default: None).

        .. note:: Unlike other relationship callables, this relationship is not
                  paginated. Thus it simply returns the full list, rather than
                  an iterator for the results.

        To be used like:

        .. code:: python

           moderators = reddit.subreddit('nameofsub').moderator()

        For example, to list the moderators along with their permissions try:

        .. code:: python

           for moderator in reddit.subreddit('SUBREDDIT').moderator():
               print('{}: {}'.format(moderator, moderator.mod_permissions))


        """
        params = {} if redditor is None else {"user": redditor}
        url = API_PATH["list_{}".format(self.relationship)].format(
            subreddit=self.subreddit
        )
        return self.subreddit._reddit.get(url, params=params)

    # pylint: disable=arguments-differ
    def add(self, redditor, permissions=None, **other_settings):
        """Add or invite ``redditor`` to be a moderator of the subreddit.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be
            a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when not
            provided ``None``, indicates full permissions.

        An invite will be sent unless the user making this call is an admin
        user.

        For example, to invite ``'spez'`` with ``'posts'`` and ``'mail'``
            permissions to ``'/r/test/``, try:

        .. code:: python

           reddit.subreddit('test').moderator.add('spez', ['posts', 'mail'])

        """
        other_settings = self._handle_permissions(permissions, other_settings)
        super(ModeratorRelationship, self).add(redditor, **other_settings)

    # pylint: enable=arguments-differ

    def invite(self, redditor, permissions=None, **other_settings):
        """Invite ``redditor`` to be a moderator of the subreddit.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be
            a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when not
            provided ``None``, indicates full permissions.

        For example, to invite ``'spez'`` with ``'posts'`` and ``'mail'``
            permissions to ``'/r/test/``, try:

        .. code:: python

           reddit.subreddit('test').moderator.invite('spez', ['posts', 'mail'])

        """
        data = self._handle_permissions(permissions, other_settings)
        data.update({"name": str(redditor), "type": "moderator_invite"})
        url = API_PATH["friend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def leave(self):
        """Abdicate the moderator position (use with care).

        Example:

        .. code:: python

           reddit.subreddit('subredditname').moderator.leave()

        """
        self.remove(self.subreddit._reddit.config.username)

    def remove_invite(self, redditor):
        """Remove the moderator invite for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        Example:

        .. code:: python

           reddit.subreddit('subredditname').moderator.remove_invite('spez')

        """
        data = {"name": str(redditor), "type": "moderator_invite"}
        url = API_PATH["unfriend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def update(self, redditor, permissions=None):
        """Update the moderator permissions for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be
            a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when not
            provided, ``None``, indicates full permissions.

        For example, to add all permissions to the moderator, try:

        .. code:: python

           subreddit.moderator.update('spez')

        To remove all permissions from the moderator, try:

        .. code:: python

           subreddit.moderator.update('spez', [])

        """
        url = API_PATH["setpermissions"].format(subreddit=self.subreddit)
        data = self._handle_permissions(
            permissions, {"name": str(redditor), "type": "moderator"}
        )
        self.subreddit._reddit.post(url, data=data)

    def update_invite(self, redditor, permissions=None):
        """Update the moderator invite permissions for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be
            a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when not
            provided, ``None``, indicates full permissions.

        For example, to grant the flair and mail permissions to the moderator
        invite, try:

        .. code:: python

           subreddit.moderator.update_invite('spez', ['flair', 'mail'])

        """
        url = API_PATH["setpermissions"].format(subreddit=self.subreddit)
        data = self._handle_permissions(
            permissions, {"name": str(redditor), "type": "moderator_invite"}
        )
        self.subreddit._reddit.post(url, data=data)


class Modmail(object):
    """Provides modmail functions for a subreddit."""

    def __call__(self, id=None, mark_read=False):  # noqa: D207, D301
        """Return an individual conversation.

        :param id: A reddit base36 conversation ID, e.g., ``2gmz``.
        :param mark_read: If True, conversation is marked as read
            (default: False).

        Example:

        .. code:: python

           reddit.subreddit('redditdev').modmail('2gmz', mark_read=True)

        To print all messages from a conversation as Markdown source:

        .. code:: python

           conversation = reddit.subreddit('redditdev').modmail('2gmz', \
mark_read=True)
           for message in conversation.messages:
               print(message.body_markdown)

        ``ModmailConversation.user`` is a special instance of
        :class:`.Redditor` with extra attributes describing the non-moderator
        user's recent posts, comments, and modmail messages within the
        subreddit, as well as information on active bans and mutes. This
        attribute does not exist on internal moderator discussions.

        For example, to print the user's ban status:

        .. code:: python

           conversation = reddit.subreddit('redditdev').modmail('2gmz', \
mark_read=True)
           print(conversation.user.ban_status)

        To print a list of recent submissions by the user:

        .. code:: python

           conversation = reddit.subreddit('redditdev').modmail('2gmz', \
mark_read=True)
           print(conversation.user.recent_posts)

        """
        # pylint: disable=invalid-name,redefined-builtin
        return ModmailConversation(
            self.subreddit._reddit, id=id, mark_read=mark_read
        )

    def __init__(self, subreddit):
        """Construct an instance of the Modmail object."""
        self.subreddit = subreddit

    def _build_subreddit_list(self, other_subreddits):
        """Return a comma-separated list of subreddit display names."""
        subreddits = [self.subreddit] + (other_subreddits or [])
        return ",".join(str(subreddit) for subreddit in subreddits)

    def bulk_read(self, other_subreddits=None, state=None):
        """Mark conversations for subreddit(s) as read.

        Due to server-side restrictions, 'all' is not a valid subreddit for
        this method. Instead, use :meth:`~.Modmail.subreddits` to get a list of
        subreddits using the new modmail.

        :param other_subreddits: A list of :class:`.Subreddit` instances for
            which to mark conversations (default: None).
        :param state: Can be one of: all, archived, highlighted, inprogress,
            mod, new, notifications, (default: all). "all" does not include
            internal or archived conversations.
        :returns: A list of :class:`.ModmailConversation` instances that were
            marked read.

        For example, to mark all notifications for a subreddit as read:

        .. code:: python

           subreddit = reddit.subreddit('redditdev')
           subreddit.modmail.bulk_read(state='notifications')

        """
        params = {"entity": self._build_subreddit_list(other_subreddits)}
        if state:
            params["state"] = state
        response = self.subreddit._reddit.post(
            API_PATH["modmail_bulk_read"], params=params
        )
        return [
            self(conversation_id)
            for conversation_id in response["conversation_ids"]
        ]

    def conversations(
        self,
        after=None,
        limit=None,
        other_subreddits=None,
        sort=None,
        state=None,
    ):  # noqa: D207, D301
        """Generate :class:`.ModmailConversation` objects for subreddit(s).

        :param after: A base36 modmail conversation id. When provided, the
            listing begins after this conversation (default: None).
        :param limit: The maximum number of conversations to fetch. If None,
            the server-side default is 25 at the time of writing
            (default: None).
        :param other_subreddits: A list of :class:`.Subreddit` instances for
            which to fetch conversations (default: None).
        :param sort: Can be one of: mod, recent, unread, user
            (default: recent).
        :param state: Can be one of: all, archived, highlighted, inprogress,
            mod, new, notifications, (default: all). "all" does not include
            internal or archived conversations.


        Example:

        .. code:: python

            conversations = reddit.subreddit('all').modmail.conversations(\
state='mod')

        """
        params = {}
        if self.subreddit != "all":
            params["entity"] = self._build_subreddit_list(other_subreddits)

        for name, value in {
            "after": after,
            "limit": limit,
            "sort": sort,
            "state": state,
        }.items():
            if value:
                params[name] = value

        response = self.subreddit._reddit.get(
            API_PATH["modmail_conversations"], params=params
        )
        for conversation_id in response["conversationIds"]:
            data = {
                "conversation": response["conversations"][conversation_id],
                "messages": response["messages"],
            }
            yield ModmailConversation.parse(
                data, self.subreddit._reddit, convert_objects=False
            )

    def create(self, subject, body, recipient, author_hidden=False):
        """Create a new modmail conversation.

        :param subject: The message subject. Cannot be empty.
        :param body: The message body. Cannot be empty.
        :param recipient: The recipient; a username or an instance of
            :class:`.Redditor`.
        :param author_hidden: When True, author is hidden from non-moderators
            (default: False).
        :returns: A :class:`.ModmailConversation` object for the newly created
            conversation.

        .. code:: python

           subreddit = reddit.subreddit('redditdev')
           redditor = reddit.redditor('bboe')
           subreddit.modmail.create('Subject', 'Body', redditor)

        """
        data = {
            "body": body,
            "isAuthorHidden": author_hidden,
            "srName": self.subreddit,
            "subject": subject,
            "to": recipient,
        }
        return self.subreddit._reddit.post(
            API_PATH["modmail_conversations"], data=data
        )

    def subreddits(self):
        """Yield subreddits using the new modmail that the user moderates.

        Example:

        .. code:: python

           subreddits = reddit.subreddit('all').modmail.subreddits()

        """
        response = self.subreddit._reddit.get(API_PATH["modmail_subreddits"])
        for value in response["subreddits"].values():
            subreddit = self.subreddit._reddit.subreddit(value["display_name"])
            subreddit.last_updated = value["lastUpdated"]
            yield subreddit

    def unread_count(self):
        """Return unread conversation count by conversation state.

        At time of writing, possible states are: archived, highlighted,
        inprogress, mod, new, notifications.

        :returns: A dict mapping conversation states to unread counts.

        For example, to print the count of unread moderator discussions:

        .. code:: python

           subreddit = reddit.subreddit('redditdev')
           unread_counts = subreddit.modmail.unread_count()
           print(unread_counts['mod'])

        """
        return self.subreddit._reddit.get(API_PATH["modmail_unread_count"])


class SubredditStream(object):
    """Provides submission and comment streams."""

    def __init__(self, subreddit):
        """Create a SubredditStream instance.

        :param subreddit: The subreddit associated with the streams.

        """
        self.subreddit = subreddit

    def comments(self, **stream_options):
        """Yield new comments as they become available.

        Comments are yielded oldest first. Up to 100 historical comments will
        initially be returned.

        Keyword arguments are passed to :func:`.stream_generator`.

        For example, to retrieve all new comments made to the ``iama``
        subreddit, try:

        .. code:: python

           for comment in reddit.subreddit('iama').stream.comments():
               print(comment)

        To only retreive new submissions starting when the stream is
        created, pass `skip_existing=True`:

        .. code:: python

           subreddit = reddit.subreddit('iama')
           for comment in subreddit.stream.comments(skip_existing=True):
               print(comment)

        """
        return stream_generator(self.subreddit.comments, **stream_options)

    def submissions(self, **stream_options):
        """Yield new submissions as they become available.

        Submissions are yielded oldest first. Up to 100 historical submissions
        will initially be returned.

        Keyword arguments are passed to :func:`.stream_generator`.

        For example to retrieve all new submissions made to all of Reddit, try:

        .. code:: python

           for submission in reddit.subreddit('all').stream.submissions():
               print(submission)

        """
        return stream_generator(self.subreddit.new, **stream_options)


class SubredditStylesheet(object):
    """Provides a set of stylesheet functions to a Subreddit."""

    def __call__(self):
        """Return the subreddit's stylesheet.

        To be used as:

        .. code:: python

           stylesheet = reddit.subreddit('SUBREDDIT').stylesheet()

        """
        url = API_PATH["about_stylesheet"].format(subreddit=self.subreddit)
        return self.subreddit._reddit.get(url)

    def __init__(self, subreddit):
        """Create a SubredditStylesheet instance.

        :param subreddit: The subreddit associated with the stylesheet.

        An instance of this class is provided as:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet

        """
        self.subreddit = subreddit

    def _update_structured_styles(self, style_data):
        url = API_PATH["structured_styles"].format(subreddit=self.subreddit)
        self.subreddit._reddit.patch(url, style_data)

    def _upload_image(self, image_path, data):
        with open(image_path, "rb") as image:
            header = image.read(len(JPEG_HEADER))
            image.seek(0)
            data["img_type"] = "jpg" if header == JPEG_HEADER else "png"
            url = API_PATH["upload_image"].format(subreddit=self.subreddit)
            response = self.subreddit._reddit.post(
                url, data=data, files={"file": image}
            )
            if response["errors"]:
                error_type = response["errors"][0]
                error_value = response.get("errors_values", [""])[0]
                assert error_type in [
                    "BAD_CSS_NAME",
                    "IMAGE_ERROR",
                ], "Please file a bug with PRAW"
                raise APIException(error_type, error_value, None)
            return response

    def _upload_style_asset(self, image_path, image_type):
        data = {"imagetype": image_type, "filepath": basename(image_path)}
        data["mimetype"] = "image/jpeg"
        if image_path.lower().endswith(".png"):
            data["mimetype"] = "image/png"
        url = API_PATH["style_asset_lease"].format(subreddit=self.subreddit)

        upload_lease = self.subreddit._reddit.post(url, data=data)[
            "s3UploadLease"
        ]
        upload_data = {
            item["name"]: item["value"] for item in upload_lease["fields"]
        }
        upload_url = "https:{}".format(upload_lease["action"])

        with open(image_path, "rb") as image:
            response = self.subreddit._reddit._core._requestor._http.post(
                upload_url, data=upload_data, files={"file": image}
            )
        response.raise_for_status()

        return "{}/{}".format(upload_url, upload_data["key"])

    def delete_banner(self):
        """Remove the current subreddit (redesign) banner image.

        Succeeds even if there is no banner image.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_banner()

        """
        data = {"bannerBackgroundImage": ""}
        self._update_structured_styles(data)

    def delete_banner_additional_image(self):
        """Remove the current subreddit (redesign) banner additional image.

        Succeeds even if there is no additional image.  Will also delete any
        configured hover image.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_banner_additional_image()

        """
        data = {
            "bannerPositionedImage": "",
            "secondaryBannerPositionedImage": "",
        }
        self._update_structured_styles(data)

    def delete_banner_hover_image(self):
        """Remove the current subreddit (redesign) banner hover image.

        Succeeds even if there is no hover image.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_banner_hover_image()

        """
        data = {"secondaryBannerPositionedImage": ""}
        self._update_structured_styles(data)

    def delete_header(self):
        """Remove the current subreddit header image.

        Succeeds even if there is no header image.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_header()

        """
        url = API_PATH["delete_sr_header"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def delete_image(self, name):
        """Remove the named image from the subreddit.

        Succeeds even if the named image does not exist.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_image('smile')

        """
        url = API_PATH["delete_sr_image"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data={"img_name": name})

    def delete_mobile_header(self):
        """Remove the current subreddit mobile header.

        Succeeds even if there is no mobile header.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_mobile_header()

        """
        url = API_PATH["delete_sr_header"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def delete_mobile_icon(self):
        """Remove the current subreddit mobile icon.

        Succeeds even if there is no mobile icon.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_mobile_icon()

        """
        url = API_PATH["delete_sr_icon"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def update(self, stylesheet, reason=None):
        """Update the subreddit's stylesheet.

        :param stylesheet: The CSS for the new stylesheet.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.update(
               'p { color: green; }', 'color text green')

        """
        data = {
            "op": "save",
            "reason": reason,
            "stylesheet_contents": stylesheet,
        }
        url = API_PATH["subreddit_stylesheet"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def upload(self, name, image_path):
        """Upload an image to the Subreddit.

        :param name: The name to use for the image. If an image already exists
            with the same name, it will be replaced.
        :param image_path: A path to a jpeg or png image.
        :returns: A dictionary containing a link to the uploaded image under
            the key ``img_src``.

        Raises ``prawcore.TooLarge`` if the overall request body is too large.

        Raises :class:`.APIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload('smile', 'img.png')

        """
        return self._upload_image(
            image_path, {"name": name, "upload_type": "img"}
        )

    def upload_banner(self, image_path):
        """Upload an image for the subreddit's (redesign) banner image.

        :param image_path: A path to a jpeg or png image.

        Raises ``prawcore.TooLarge`` if the overall request body is too large.

        Raises :class:`.APIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload_banner('banner.png')

        """
        image_type = "bannerBackgroundImage"
        image_url = self._upload_style_asset(image_path, image_type)
        self._update_structured_styles({image_type: image_url})

    def upload_banner_additional_image(self, image_path, align=None):
        """Upload an image for the subreddit's (redesign) additional image.

        :param image_path: A path to a jpeg or png image.
        :param align: Either ``left``, ``centered``, or ``right``. (default:
            ``left``).

        Raises ``prawcore.TooLarge`` if the overall request body is too large.

        Raises :class:`.APIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload_banner_additional_image('banner.png')

        """
        alignment = {}
        if align is not None:
            if align not in {"left", "centered", "right"}:
                raise ValueError(
                    "align argument must be either "
                    "`left`, `centered`, or `right`"
                )
            alignment["bannerPositionedImagePosition"] = align

        image_type = "bannerPositionedImage"
        image_url = self._upload_style_asset(image_path, image_type)
        style_data = {image_type: image_url}
        if alignment:
            style_data.update(alignment)
        self._update_structured_styles(style_data)

    def upload_banner_hover_image(self, image_path):
        """Upload an image for the subreddit's (redesign) additional image.

        :param image_path: A path to a jpeg or png image.

        Fails if the Subreddit does not have an additional image defined

        Raises ``prawcore.TooLarge`` if the overall request body is too large.

        Raises :class:`.APIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload_banner_hover_image('banner.png')

        """
        image_type = "secondaryBannerPositionedImage"
        image_url = self._upload_style_asset(image_path, image_type)
        self._update_structured_styles({image_type: image_url})

    def upload_header(self, image_path):
        """Upload an image to be used as the Subreddit's header image.

        :param image_path: A path to a jpeg or png image.
        :returns: A dictionary containing a link to the uploaded image under
            the key ``img_src``.

        Raises ``prawcore.TooLarge`` if the overall request body is too large.

        Raises :class:`.APIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        Example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload_header('header.png')

        """
        return self._upload_image(image_path, {"upload_type": "header"})

    def upload_mobile_header(self, image_path):
        """Upload an image to be used as the Subreddit's mobile header.

        :param image_path: A path to a jpeg or png image.
        :returns: A dictionary containing a link to the uploaded image under
            the key ``img_src``.

        Raises ``prawcore.TooLarge`` if the overall request body is too large.

        Raises :class:`.APIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        For example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload_mobile_header(
               'header.png')

        """
        return self._upload_image(image_path, {"upload_type": "banner"})

    def upload_mobile_icon(self, image_path):
        """Upload an image to be used as the Subreddit's mobile icon.

        :param image_path: A path to a jpeg or png image.
        :returns: A dictionary containing a link to the uploaded image under
            the key ``img_src``.

        Raises ``prawcore.TooLarge`` if the overall request body is too large.

        Raises :class:`.APIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        For example:

        .. code:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload_mobile_icon(
               'icon.png')

        """
        return self._upload_image(image_path, {"upload_type": "icon"})


class SubredditWiki(object):
    """Provides a set of moderation functions to a Subreddit."""

    def __getitem__(self, page_name):
        """Lazily return the WikiPage for the subreddit named ``page_name``.

        This method is to be used to fetch a specific wikipage, like so:

        .. code:: python

           wikipage = reddit.subreddit('iama').wiki['proof']
           print(wikipage.content_md)

        """
        return WikiPage(
            self.subreddit._reddit, self.subreddit, page_name.lower()
        )

    def __init__(self, subreddit):
        """Create a SubredditModeration instance.

        :param subreddit: The subreddit to moderate.

        """
        self.banned = SubredditRelationship(subreddit, "wikibanned")
        self.contributor = SubredditRelationship(subreddit, "wikicontributor")
        self.subreddit = subreddit

    def __iter__(self):
        """Iterate through the pages of the wiki.

        This method is to be used to discover all wikipages for a subreddit:

        .. code:: python

           for wikipage in reddit.subreddit('iama').wiki:
               print(wikipage)

        """
        response = self.subreddit._reddit.get(
            API_PATH["wiki_pages"].format(subreddit=self.subreddit),
            params={"unique": self.subreddit._reddit._next_unique},
        )
        for page_name in response["data"]:
            yield WikiPage(self.subreddit._reddit, self.subreddit, page_name)

    def create(self, name, content, reason=None, **other_settings):
        """Create a new wiki page.

        :param name: The name of the new WikiPage. This name will be
            normalized.
        :param content: The content of the new WikiPage.
        :param reason: (Optional) The reason for the creation.
        :param other_settings: Additional keyword arguments to pass.

        To create the wiki page ``'praw_test'`` in ``'/r/test'`` try:

        .. code:: python

           reddit.subreddit('test').wiki.create(
               'praw_test', 'wiki body text', reason='PRAW Test Creation')

        """
        name = name.replace(" ", "_").lower()
        new = WikiPage(self.subreddit._reddit, self.subreddit, name)
        new.edit(content=content, reason=reason, **other_settings)
        return new

    def revisions(self, **generator_kwargs):
        """Return a generator for recent wiki revisions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To view the wiki revisions for ``'praw_test'`` in ``'/r/test'`` try:

        .. code:: python

           for item in reddit.subreddit('test').wiki['praw_test'].revisions():
               print(item)

        """
        url = API_PATH["wiki_revisions"].format(subreddit=self.subreddit)
        return WikiPage._revision_generator(
            self.subreddit, url, generator_kwargs
        )
