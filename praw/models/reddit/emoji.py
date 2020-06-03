"""Provide the Emoji class."""
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ...const import API_PATH
from ...exceptions import ClientException
from .base import RedditBase

if TYPE_CHECKING:  # pragma: no cover
    from ... import Reddit
    from .subreddit import Subreddit


class Emoji(RedditBase):
    """An individual Emoji object.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``mod_flair_only``      Whether the emoji is restricted for mod use only.
    ``name``                The name of the emoji.
    ``post_flair_allowed``  Whether the emoji may appear in post flair.
    ``url``                 The URL of the emoji image.
    ``user_flair_allowed``  Whether the emoji may appear in user flair.
    ======================= ===================================================

    """

    STR_FIELD = "name"

    def __eq__(self, other: Union[str, "Emoji"]) -> bool:
        """Return whether the other instance equals the current."""
        if isinstance(other, str):
            return other == str(self)
        if isinstance(other, self.__class__):
            return str(self) == str(other) and other.subreddit == self.subreddit
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self)) ^ hash(self.subreddit)

    def __init__(
        self,
        reddit: "Reddit",
        subreddit: "Subreddit",
        name: str,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Construct an instance of the Emoji object."""
        self.name = name
        self.subreddit = subreddit
        super().__init__(reddit, _data=_data)

    def _fetch(self):
        for emoji in self.subreddit.emoji:
            if emoji.name == self.name:
                self.__dict__.update(emoji.__dict__)
                self._fetched = True
                return
        raise ClientException(
            "/r/{} does not have the emoji {}".format(self.subreddit, self.name)
        )

    def delete(self):
        """Delete an emoji from this subreddit by Emoji.

        To delete ``"test"`` as an emoji on the subreddit ``"praw_test"`` try:

        .. code-block:: python

           reddit.subreddit("praw_test").emoji["test"].delete()

        """
        url = API_PATH["emoji_delete"].format(
            emoji_name=self.name, subreddit=self.subreddit
        )
        self._reddit.delete(url)

    def update(
        self,
        mod_flair_only: Optional[bool] = None,
        post_flair_allowed: Optional[bool] = None,
        user_flair_allowed: Optional[bool] = None,
    ):
        """Update the permissions of an emoji in this subreddit.

        :param mod_flair_only: (boolean) Indicate whether the emoji is
            restricted to mod use only. Respects pre-existing settings if not
            provided.
        :param post_flair_allowed: (boolean) Indicate whether the emoji may
            appear in post flair. Respects pre-existing settings if not
            provided.
        :param user_flair_allowed: (boolean) Indicate whether the emoji may
            appear in user flair. Respects pre-existing settings if not
            provided.

        .. note:: In order to retain pre-existing values for those that are not
           explicitly passed, a network request is issued. To  avoid that
           network request, explicitly provide all values.

        To restrict the emoji ``test`` in subreddit ``wowemoji`` to mod use
        only, try:

        .. code-block:: python

           reddit.subreddit("wowemoji").emoji["test"].update(mod_flair_only=True)

        """
        locals_reference = locals()
        mapping = {
            attribute: locals_reference[attribute]
            for attribute in (
                "mod_flair_only",
                "post_flair_allowed",
                "user_flair_allowed",
            )
        }
        if all(value is None for value in mapping.values()):
            raise TypeError("At least one attribute must be provided")

        data = {"name": self.name}
        for attribute, value in mapping.items():
            if value is None:
                value = getattr(self, attribute)
            data[attribute] = value
        url = API_PATH["emoji_update"].format(subreddit=self.subreddit)
        self._reddit.post(url, data=data)
        for attribute, value in data.items():
            setattr(self, attribute, value)


class SubredditEmoji:
    """Provides a set of functions to a Subreddit for emoji."""

    def __getitem__(self, name: str) -> Emoji:
        """Lazily return the Emoji for the subreddit named ``name``.

        :param name: The name of the emoji

        This method is to be used to fetch a specific emoji url, like so:

        .. code-block:: python

           emoji = reddit.subreddit("praw_test").emoji["test"]
           print(emoji)

        """
        return Emoji(self._reddit, self.subreddit, name)

    def __init__(self, subreddit: "Subreddit"):
        """Create a SubredditEmoji instance.

        :param subreddit: The subreddit whose emoji are affected.

        """
        self.subreddit = subreddit
        self._reddit = subreddit._reddit

    def __iter__(self) -> List[Emoji]:
        """Return a list of Emoji for the subreddit.

        This method is to be used to discover all emoji for a subreddit:

        .. code-block:: python

           for emoji in reddit.subreddit("praw_test").emoji:
               print(emoji)

        """
        response = self._reddit.get(
            API_PATH["emoji_list"].format(subreddit=self.subreddit)
        )
        subreddit_keys = [
            key
            for key in response.keys()
            if key.startswith(self._reddit.config.kinds["subreddit"])
        ]
        assert len(subreddit_keys) == 1
        for emoji_name, emoji_data in response[subreddit_keys[0]].items():
            yield Emoji(self._reddit, self.subreddit, emoji_name, _data=emoji_data)

    def add(
        self,
        name: str,
        image_path: str,
        mod_flair_only: Optional[bool] = None,
        post_flair_allowed: Optional[bool] = None,
        user_flair_allowed: Optional[bool] = None,
    ) -> Emoji:
        """Add an emoji to this subreddit.

        :param name: The name of the emoji
        :param image_path: A path to a jpeg or png image.
        :param mod_flair_only: (boolean) When provided, indicate whether the
            emoji is restricted to mod use only. (Default: ``None``)
        :param post_flair_allowed: (boolean) When provided, indicate whether
            the emoji may appear in post flair. (Default: ``None``)
        :param user_flair_allowed: (boolean) When provided, indicate whether
            the emoji may appear in user flair. (Default: ``None``)
        :returns: The Emoji added.

        To add ``test`` to the subreddit ``praw_test`` try:

        .. code-block:: python

           reddit.subreddit("praw_test").emoji.add("test", "test.png")

        """
        data = {
            "filepath": os.path.basename(image_path),
            "mimetype": "image/jpeg",
        }
        if image_path.lower().endswith(".png"):
            data["mimetype"] = "image/png"
        url = API_PATH["emoji_lease"].format(subreddit=self.subreddit)

        # until we learn otherwise, assume this request always succeeds
        upload_lease = self._reddit.post(url, data=data)["s3UploadLease"]
        upload_data = {item["name"]: item["value"] for item in upload_lease["fields"]}
        upload_url = "https:{}".format(upload_lease["action"])

        with open(image_path, "rb") as image:
            response = self._reddit._core._requestor._http.post(
                upload_url, data=upload_data, files={"file": image}
            )
        response.raise_for_status()

        data = {
            "mod_flair_only": mod_flair_only,
            "name": name,
            "post_flair_allowed": post_flair_allowed,
            "s3_key": upload_data["key"],
            "user_flair_allowed": user_flair_allowed,
        }
        url = API_PATH["emoji_upload"].format(subreddit=self.subreddit)
        self._reddit.post(url, data=data)
        return Emoji(self._reddit, self.subreddit, name)
