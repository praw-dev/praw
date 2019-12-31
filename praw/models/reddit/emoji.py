"""Provide the Emoji class."""
import os
from typing import Any, Dict, List, Optional, TypeVar, Union

from ...const import API_PATH
from ...exceptions import ClientException
from .base import RedditBase

_Emoji = TypeVar("_Emoji")
Reddit = TypeVar("Reddit")
Subreddit = TypeVar("Subreddit")


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
    ``name``                The name of the emoji.
    ``url``                 The URL of the emoji image.
    ======================= ===================================================
    """

    STR_FIELD = "name"

    def __eq__(self, other: Union[str, _Emoji]) -> bool:
        """Return whether the other instance equals the current."""
        if isinstance(other, str):
            return other == str(self)
        return (
            isinstance(other, self.__class__)
            and str(self) == str(other)
            and other.subreddit == self.subreddit
        )

    def __hash__(self) -> int:
        """Return the hash of the current instance."""
        return (
            hash(self.__class__.__name__)
            ^ hash(str(self))
            ^ hash(self.subreddit)
        )

    def __init__(
        self,
        reddit: Reddit,
        subreddit: Subreddit,
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
            "/r/{} does not have the emoji {}".format(
                self.subreddit, self.name
            )
        )

    def delete(self):
        """Delete an emoji from this subreddit by Emoji.

        To delete ``'test'`` as an emoji on the subreddit ``'praw_test'`` try:

        .. code-block:: python

           reddit.subreddit('praw_test').emoji['test'].delete()

        """
        url = API_PATH["emoji_delete"].format(
            emoji_name=self.name, subreddit=self.subreddit
        )
        self._reddit.request("DELETE", url)


class SubredditEmoji:
    """Provides a set of functions to a Subreddit for emoji."""

    def __getitem__(self, name: str) -> Emoji:
        """Lazily return the Emoji for the subreddit named ``name``.

        :param name: The name of the emoji

        This method is to be used to fetch a specific emoji url, like so:

        .. code-block:: python

           emoji = reddit.subreddit('praw_test').emoji['test']
           print(emoji)

        """
        return Emoji(self._reddit, self.subreddit, name)

    def __init__(self, subreddit: Subreddit):
        """Create a SubredditEmoji instance.

        :param subreddit: The subreddit whose emoji are affected.

        """
        self.subreddit = subreddit
        self._reddit = subreddit._reddit

    def __iter__(self) -> List[Emoji]:
        """Return a list of Emoji for the subreddit.

        This method is to be used to discover all emoji for a subreddit:

        .. code-block:: python

           for emoji in reddit.subreddit('praw_test').emoji:
               print(emoji)

        """
        response = self.subreddit._reddit.get(
            API_PATH["emoji_list"].format(subreddit=self.subreddit)
        )
        for emoji_name, emoji_data in response[
            self.subreddit.fullname
        ].items():
            yield Emoji(
                self._reddit, self.subreddit, emoji_name, _data=emoji_data
            )

    def add(self, name: str, image_path: str):
        """Add an emoji to this subreddit.

        :param name: The name of the emoji
        :param image_path: A path to a jpeg or png image.
        :returns: The Emoji added.

        To add ``'test'`` to the subreddit ``'praw_test'`` try:

        .. code-block:: python

           reddit.subreddit('praw_test').emoji.add('test','test.png')

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
        upload_data = {
            item["name"]: item["value"] for item in upload_lease["fields"]
        }
        upload_url = "https:{}".format(upload_lease["action"])

        with open(image_path, "rb") as image:
            response = self._reddit._core._requestor._http.post(
                upload_url, data=upload_data, files={"file": image}
            )
        response.raise_for_status()

        url = API_PATH["emoji_upload"].format(subreddit=self.subreddit)
        self._reddit.post(
            url, data={"name": name, "s3_key": upload_data["key"]}
        )
        return Emoji(self._reddit, self.subreddit, name)
