"""Provide the Multireddit class."""
from json import dumps
import re

from ...const import API_PATH
from ...util.cache import cachedproperty
from ..listing.mixins import SubredditListingMixin
from .base import RedditBase
from .redditor import Redditor
from .subreddit import Subreddit, SubredditStream


class Multireddit(SubredditListingMixin, RedditBase):
    r"""A class for users' Multireddits.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``can_edit``            A ``bool`` representing whether or not the
                            authenticated user may edit the multireddit.
    ``copied_from``         The multireddit that the multireddit was copied
                            from, if it exists, otherwise ``None``.
    ``created_utc``         When the multireddit was created, in `Unix Time`_.
    ``description_html``    The description of the multireddit, as HTML.
    ``description_md``      The description of the multireddit, as Markdown.
    ``display_name``        The display name of the multireddit.
    ``name``                The name of the multireddit.
    ``over_18``             A ``bool`` representing whether or not the
                            multireddit is restricted for users over 18.
    ``subreddits``          A ``list`` of :class:`.Subreddit`\ s that make up
                            the multireddit.
    ``visibility``          The visibility of the multireddit, either
                            ``private``, ``public``, or ``hidden``.
    ======================= ===================================================

    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time
    """

    STR_FIELD = "path"
    RE_INVALID = re.compile(r"[\W_]+", re.UNICODE)

    @staticmethod
    def sluggify(title):
        """Return a slug version of the title.

        :param title: The title to make a slug of.

        Adapted from reddit's utils.py.

        """
        title = Multireddit.RE_INVALID.sub("_", title).strip("_").lower()
        if len(title) > 21:  # truncate to nearest word
            title = title[:21]
            last_word = title.rfind("_")
            if last_word > 0:
                title = title[:last_word]
        return title or "_"

    @cachedproperty
    def stream(self):
        """Provide an instance of :class:`.SubredditStream`.

        Streams can be used to indefinitely retrieve new comments made to a
        subreddit, like:

        .. code:: python

           for comment in reddit.multireddit('spez', 'fun').stream.comments():
               print(comment)

        Additionally, new submissions can be retrieved via the stream. In the
        following example all submissions are fetched via the special subreddit
        ``all``:

        .. code:: python

           for submission in reddit.multireddit('bboe',
                                                'games').stream.submissions():
               print(submission)

        """
        return SubredditStream(self)

    def __init__(self, reddit, _data):
        """Construct an instance of the Multireddit object."""
        self.path = None
        super(Multireddit, self).__init__(reddit, _data=_data)
        self._author = Redditor(reddit, self.path.split("/", 3)[2])
        self._path = API_PATH["multireddit"].format(
            multi=self.name, user=self._author
        )
        self.path = "/" + self._path[:-1]  # Prevent requests for path
        if "subreddits" in self.__dict__:
            self.subreddits = [
                Subreddit(reddit, x["name"]) for x in self.subreddits
            ]

    def _fetch_info(self):
        return (
            "multireddit_api",
            {"multi": self.name, "user": self._author.name},
            None,
        )

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

    def add(self, subreddit):
        """Add a subreddit to this multireddit.

        :param subreddit: The subreddit to add to this multi.

        """
        url = API_PATH["multireddit_update"].format(
            multi=self.name, user=self._author, subreddit=subreddit
        )
        self._reddit.request(
            "PUT", url, data={"model": dumps({"name": str(subreddit)})}
        )
        self._reset_attributes("subreddits")

    def copy(self, display_name=None):
        """Copy this multireddit and return the new multireddit.

        :param display_name: (optional) The display name for the copied
            multireddit. Reddit will generate the ``name`` field from this
            display name. When not provided the copy will use the same display
            name and name as this multireddit.

        """
        if display_name:
            name = self.sluggify(display_name)
        else:
            display_name = self.display_name
            name = self.name
        data = {
            "display_name": display_name,
            "from": self.path,
            "to": API_PATH["multireddit"].format(
                multi=name, user=self._reddit.user.me()
            ),
        }
        return self._reddit.post(API_PATH["multireddit_copy"], data=data)

    def delete(self):
        """Delete this multireddit."""
        path = API_PATH["multireddit_api"].format(
            multi=self.name, user=self._author.name
        )
        self._reddit.request("DELETE", path)

    def remove(self, subreddit):
        """Remove a subreddit from this multireddit.

        :param subreddit: The subreddit to remove from this multi.

        """
        url = API_PATH["multireddit_update"].format(
            multi=self.name, user=self._author, subreddit=subreddit
        )
        self._reddit.request(
            "DELETE", url, data={"model": dumps({"name": str(subreddit)})}
        )
        self._reset_attributes("subreddits")

    def rename(self, display_name):
        """Rename this multireddit.

        :param display_name: The new display name for this multireddit. Reddit
            will generate the ``name`` field from this display name.

        """
        data = {"from": self.path, "display_name": display_name}
        updated = self._reddit.post(API_PATH["multireddit_rename"], data=data)
        self.__dict__.update(updated.__dict__)

    def update(self, **updated_settings):
        """Update this multireddit.

        Keyword arguments are passed for settings that should be updated. They
        can any of:

        :param display_name: The display name for this multireddit.
        :param subreddits: Subreddits for this multireddit.
        :param description_md: Description for this multireddit, formatted in
            markdown.
        :param icon_name: Can be one of: ``art and design``, ``ask``,
            ``books``, ``business``, ``cars``, ``comics``, ``cute animals``,
            ``diy``, ``entertainment``, ``food and drink``, ``funny``,
            ``games``, ``grooming``, ``health``, ``life advice``, ``military``,
            ``models pinup``, ``music``, ``news``, ``philosophy``, ``pictures
            and gifs``, ``science``, ``shopping``, ``sports``, ``style``,
            ``tech``, ``travel``, ``unusual stories``, ``video``, or ``None``.
        :param key_color: RGB hex color code of the form ``'#FFFFFF'``.
        :param visibility: Can be one of: ``hidden``, ``private``, ``public``.
        :param weighting_scheme: Can be one of: ``classic``, ``fresh``.

        """
        if "subreddits" in updated_settings:
            updated_settings["subreddits"] = [
                {"name": str(sub)} for sub in updated_settings["subreddits"]
            ]
        path = API_PATH["multireddit_api"].format(
            multi=self.name, user=self._author.name
        )
        response = self._reddit.request(
            "PUT", path, data={"model": dumps(updated_settings)}
        )
        new = Multireddit(self._reddit, response["data"])
        self.__dict__.update(new.__dict__)
