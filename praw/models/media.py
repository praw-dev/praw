"""Provide classes for uploading media to Reddit."""

from __future__ import annotations

import sys
from functools import cached_property
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, ClassVar, cast

from defusedxml import ElementTree
from prawcore.exceptions import ServerError

from praw.const import API_PATH, JPEG_HEADER
from praw.exceptions import (
    ClientException,
    RedditAPIException,
    RedditErrorItem,
    TooLargeMediaException,
)

if sys.version_info >= (3, 13):  # pragma: no cover
    from mimetypes import guess_file_type
else:  # pragma: no cover
    from mimetypes import guess_type as guess_file_type

if TYPE_CHECKING:
    from requests import Response

    import praw
    from praw import models


class Media:
    """Base class representing media that can be uploaded to Reddit.

    Use one of the subclasses, e.g., :class:`.EmojiMedia` or :class:`.PostMedia`,
    depending on what the media is being uploaded for.

    """

    LEASE_API_PATH: ClassVar[str]
    LEASE_RESPONSE_KEY: ClassVar[str] = "s3UploadLease"

    @staticmethod
    def _raise_upload_error(response: Response, /) -> None:
        raise ServerError(response)

    def __eq__(self, other: object) -> bool:
        """Return whether the other instance equals the current."""
        return type(other) is type(self) and self.name == other.name and self._data == other._data

    def __hash__(self) -> int:
        """Return the hash of the current instance."""
        return hash((self.__class__.__name__, self.name, self._data))

    def __init__(self, fp: str | bytes, /, name: str | None = None) -> None:
        """Initialize a :class:`.Media` instance.

        :param fp: The path to a media file as a string, or the content of a media file
            as a :class:`bytes` object.
        :param name: The name of the media file, e.g., ``"picture.png"``. The name is
            used to infer the media's MIME type. When ``fp`` is a path the name is
            derived from it, otherwise this parameter is required.

        """
        if isinstance(fp, bytes):
            if not name:
                msg = "'name' is required when 'fp' is a bytes object."
                raise ValueError(msg)
            data = fp
        else:
            path = Path(fp)
            name = name or path.name
            data = path.read_bytes()
        self._data = data
        self.name = name

    def __repr__(self) -> str:
        """Return a string representation of the instance."""
        return f"<{self.__class__.__name__} name={self.name!r}>"

    def _build_lease_data(self, **additional_data: str) -> dict[str, str]:
        return {"filepath": self.name, "mimetype": self._mime_type, **additional_data}

    def _lease_and_post(
        self, lease_url: str, reddit: praw.Reddit, /, **additional_lease_data: str
    ) -> tuple[dict[str, Any], dict[str, str], str]:
        lease_data = self._build_lease_data(**additional_lease_data)
        lease_response, upload_data, upload_url = self._obtain_lease(lease_data, lease_url, reddit)
        response = self._post_to_s3(reddit, upload_data, upload_url)
        if not response.ok:
            self._raise_upload_error(response)
        return lease_response, upload_data, upload_url

    @cached_property
    def _mime_type(self) -> str:
        mime_type, _ = guess_file_type(self.name)
        if mime_type is None:
            msg = f"Unable to determine the MIME type of {self.name!r}."
            raise ClientException(msg)
        return mime_type

    def _obtain_lease(
        self, lease_data: dict[str, str], lease_url: str, reddit: praw.Reddit, /
    ) -> tuple[dict[str, Any], dict[str, str], str]:
        lease_response = reddit.post(lease_url, data=lease_data)
        upload_lease = lease_response[self.LEASE_RESPONSE_KEY]
        upload_data = {item["name"]: item["value"] for item in upload_lease["fields"]}
        upload_url = f"https:{upload_lease['action']}"
        return lease_response, upload_data, upload_url

    def _post_to_s3(self, reddit: praw.Reddit, upload_data: dict[str, str], upload_url: str, /) -> Response:
        assert reddit._core is not None
        return reddit._core.requestor.request(
            "POST",
            upload_url,
            data=upload_data,
            files={"file": (self.name, self._data)},
        )

    def _upload(self, subreddit: models.Subreddit, /, **additional_lease_data: str) -> str:
        """Upload the media to Reddit.

        :param subreddit: The subreddit the media is associated with.
        :param additional_lease_data: Additional data to include in the upload lease
            request.

        :returns: The URL of the uploaded media.

        """
        lease_url = self.LEASE_API_PATH.format(subreddit=subreddit)
        _, upload_data, upload_url = self._lease_and_post(lease_url, subreddit._reddit, **additional_lease_data)
        return f"{upload_url}/{upload_data['key']}"


class EmojiMedia(Media):
    """Media to be uploaded as a subreddit emoji.

    See :meth:`.SubredditEmoji.add`.

    """

    LEASE_API_PATH = API_PATH["emoji_lease"]

    def _upload(self, subreddit: models.Subreddit, /, **additional_lease_data: str) -> str:
        """Upload the media to Reddit.

        :param subreddit: The subreddit the emoji is associated with.
        :param additional_lease_data: Additional data to include in the upload lease
            request.

        :returns: The S3 key of the uploaded media.

        """
        lease_url = self.LEASE_API_PATH.format(subreddit=subreddit)
        _, upload_data, _ = self._lease_and_post(lease_url, subreddit._reddit, **additional_lease_data)
        return upload_data["key"]


class PostMedia(Media):
    """Media to be uploaded as part of a submission.

    See :meth:`.Subreddit.submit` and :class:`.InlineMedia`.

    """

    LEASE_API_PATH = API_PATH["media_asset"]
    LEASE_RESPONSE_KEY = "args"

    @staticmethod
    def _parse_xml_response(response: Response, /) -> None:
        """Parse the XML from a response and raise any errors found."""
        root = ElementTree.fromstring(response.text)
        tags = [element.tag for element in root]
        if tags[:4] == ["Code", "Message", "ProposedSize", "MaxSizeAllowed"]:
            # Returned if media is too big
            *_, actual, maximum_size = (element.text for element in root[:4])
            raise TooLargeMediaException(actual=int(actual or 0), maximum_size=int(maximum_size or 0))

    @staticmethod
    def _raise_upload_error(response: Response, /) -> None:
        PostMedia._parse_xml_response(response)
        Media._raise_upload_error(response)

    def _upload(  # pyright: ignore[reportIncompatibleMethodOverride]  # post media is uploaded with a Reddit instance rather than a Subreddit
        self,
        reddit: praw.Reddit,
        /,
        *,
        expected_mime_prefix: str | None = None,
        upload_type: str = "link",
    ) -> str:
        """Upload the media to Reddit (undocumented endpoint).

        Unlike the other :class:`.Media` subclasses, post media is not associated with a
        subreddit when uploaded, so this method takes a :class:`.Reddit` instance.

        :param reddit: The :class:`.Reddit` instance to upload with.
        :param expected_mime_prefix: If provided, enforce that the media has a MIME type
            that starts with the provided prefix.
        :param upload_type: One of ``"link"``, ``"gallery"``, or ``"selfpost"``
            (default: ``"link"``).

        :returns: The URL of the uploaded media when ``upload_type`` is ``"link"``,
            otherwise the media's asset ID.

        """
        if expected_mime_prefix is not None and self._mime_type.partition("/")[0] != expected_mime_prefix:
            msg = f"Expected a mimetype starting with {expected_mime_prefix!r} but got mimetype {self._mime_type!r} (from file name {self.name!r})."
            raise ClientException(msg)
        lease_response, upload_data, upload_url = self._lease_and_post(self.LEASE_API_PATH, reddit)
        if upload_type == "link":
            return f"{upload_url}/{upload_data['key']}"
        return lease_response["asset"]["asset_id"]


class StylesheetAsset(Media):
    """Media to be uploaded as a subreddit style asset, e.g., a banner.

    See :meth:`.SubredditStylesheet.upload_banner`.

    """

    LEASE_API_PATH = API_PATH["style_asset_lease"]

    def _upload(  # pyright: ignore[reportIncompatibleMethodOverride]  # style assets require an image_type rather than arbitrary lease data
        self, subreddit: models.Subreddit, /, *, image_type: str
    ) -> str:
        """Upload the media to Reddit.

        :param subreddit: The subreddit the style asset is associated with.
        :param image_type: The type of style asset, e.g., ``"bannerBackgroundImage"``.

        :returns: The URL of the uploaded media.

        """
        return super()._upload(subreddit, imagetype=image_type)


class StylesheetImage(Media):
    """Media to be uploaded as a subreddit stylesheet image.

    See :meth:`.SubredditStylesheet.upload`.

    """

    UPLOAD_API_PATH = API_PATH["upload_image"]

    @cached_property
    def _image_type(self) -> str:
        return "jpg" if self._data.startswith(JPEG_HEADER) else "png"

    def _upload(  # pyright: ignore[reportIncompatibleMethodOverride]  # stylesheet image upload returns the raw response dict
        self, subreddit: models.Subreddit, /, **additional_data: str
    ) -> dict[str, Any]:
        """Upload the media to Reddit.

        :param subreddit: The subreddit the stylesheet image is associated with.
        :param additional_data: Additional data to include in the upload request.

        :returns: A dictionary containing a link to the uploaded image under the key
            ``img_src``.

        """
        data = {"img_type": self._image_type, **additional_data}
        url = self.UPLOAD_API_PATH.format(subreddit=subreddit)
        # ``requests`` accepts ``(filename, content)`` tuples for file uploads, but
        # ``Reddit.post`` types ``files`` as ``dict[str, IO]``.
        files = cast("dict[str, IO[Any]]", {"file": (self.name, self._data)})
        response = subreddit._reddit.post(url, data=data, files=files)
        if response["errors"]:
            error_type = response["errors"][0]
            error_value = response.get("errors_values", [""])[0]
            assert error_type in {
                "BAD_CSS_NAME",
                "IMAGE_ERROR",
            }, "Please file a bug with PRAW."
            raise RedditAPIException([RedditErrorItem(error_type=error_type, field="", message=error_value or "")])
        return response


class WidgetMedia(Media):
    """Media to be uploaded for use in a subreddit widget.

    See :meth:`.SubredditWidgetsModeration.upload_image`.

    """

    LEASE_API_PATH = API_PATH["widget_lease"]
