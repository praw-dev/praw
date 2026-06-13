"""Provide the SubredditStylesheet class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from praw.const import API_PATH

if TYPE_CHECKING:
    from praw import models


class SubredditStylesheet:
    """Provides a set of stylesheet functions to a :class:`.Subreddit`.

    For example, to add the css data ``.test{color:blue}`` to the existing stylesheet:

    .. code-block:: python

        subreddit = reddit.subreddit("test")
        stylesheet = subreddit.stylesheet()
        stylesheet.stylesheet += ".test{color:blue}"
        subreddit.stylesheet.update(stylesheet.stylesheet)

    """

    def __call__(self) -> models.Stylesheet:
        """Return the :class:`.Subreddit`'s stylesheet.

        To be used as:

        .. code-block:: python

            stylesheet = reddit.subreddit("test").stylesheet()

        """
        url = API_PATH["about_stylesheet"].format(subreddit=self.subreddit)
        return self.subreddit._reddit.get(url)

    def __init__(self, subreddit: models.Subreddit) -> None:
        """Initialize a :class:`.SubredditStylesheet` instance.

        :param subreddit: The :class:`.Subreddit` associated with the stylesheet.

        An instance of this class is provided as:

        .. code-block:: python

            reddit.subreddit("test").stylesheet

        """
        self.subreddit = subreddit

    def _update_structured_styles(self, style_data: dict[str, str | Any]) -> None:
        url = API_PATH["structured_styles"].format(subreddit=self.subreddit)
        self.subreddit._reddit.patch(url, data=style_data)

    def delete_banner(self) -> None:
        """Remove the current :class:`.Subreddit` (redesign) banner image.

        Succeeds even if there is no banner image.

        For example:

        .. code-block:: python

            reddit.subreddit("test").stylesheet.delete_banner()

        """
        data = {"bannerBackgroundImage": ""}
        self._update_structured_styles(data)

    def delete_banner_additional_image(self) -> None:
        """Remove the current :class:`.Subreddit` (redesign) banner additional image.

        Succeeds even if there is no additional image. Will also delete any configured
        hover image.

        For example:

        .. code-block:: python

            reddit.subreddit("test").stylesheet.delete_banner_additional_image()

        """
        data = {"bannerPositionedImage": "", "secondaryBannerPositionedImage": ""}
        self._update_structured_styles(data)

    def delete_banner_hover_image(self) -> None:
        """Remove the current :class:`.Subreddit` (redesign) banner hover image.

        Succeeds even if there is no hover image.

        For example:

        .. code-block:: python

            reddit.subreddit("test").stylesheet.delete_banner_hover_image()

        """
        data = {"secondaryBannerPositionedImage": ""}
        self._update_structured_styles(data)

    def delete_header(self) -> None:
        """Remove the current :class:`.Subreddit` header image.

        Succeeds even if there is no header image.

        For example:

        .. code-block:: python

            reddit.subreddit("test").stylesheet.delete_header()

        """
        url = API_PATH["delete_sr_header"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def delete_image(self, name: str) -> None:
        """Remove the named image from the :class:`.Subreddit`.

        Succeeds even if the named image does not exist.

        For example:

        .. code-block:: python

            reddit.subreddit("test").stylesheet.delete_image("smile")

        """
        url = API_PATH["delete_sr_image"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data={"img_name": name})

    def delete_mobile_banner(self) -> None:
        """Remove the current :class:`.Subreddit` (redesign) mobile banner.

        Succeeds even if there is no mobile banner.

        For example:

        .. code-block:: python

            subreddit = reddit.subreddit("test")
            subreddit.stylesheet.delete_banner_hover_image()

        """
        data = {"mobileBannerImage": ""}
        self._update_structured_styles(data)

    def delete_mobile_header(self) -> None:
        """Remove the current :class:`.Subreddit` mobile header.

        Succeeds even if there is no mobile header.

        For example:

        .. code-block:: python

            reddit.subreddit("test").stylesheet.delete_mobile_header()

        """
        url = API_PATH["delete_sr_header"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def delete_mobile_icon(self) -> None:
        """Remove the current :class:`.Subreddit` mobile icon.

        Succeeds even if there is no mobile icon.

        For example:

        .. code-block:: python

            reddit.subreddit("test").stylesheet.delete_mobile_icon()

        """
        url = API_PATH["delete_sr_icon"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def update(self, stylesheet: str, *, reason: str | None = None) -> None:
        """Update the :class:`.Subreddit`'s stylesheet.

        :param stylesheet: The CSS for the new stylesheet.
        :param reason: The reason for updating the stylesheet.

        For example:

        .. code-block:: python

            reddit.subreddit("test").stylesheet.update(
                "p { color: green; }", reason="color text green"
            )

        """
        data = {"op": "save", "reason": reason, "stylesheet_contents": stylesheet}
        url = API_PATH["subreddit_stylesheet"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def upload(self, media: models.StylesheetImage, /, *, name: str) -> dict[str, str]:
        """Upload an image to the :class:`.Subreddit`.

        :param media: The :class:`.StylesheetImage` to upload.
        :param name: The name to use for the image. If an image already exists with the
            same name, it will be replaced.

        :returns: A dictionary containing a link to the uploaded image under the key
            ``img_src``.

        :raises: ``prawcore.TooLarge`` if the overall request body is too large.
        :raises: :class:`.RedditAPIException` if there are other issues with the
            uploaded image. Unfortunately the exception info might not be very specific,
            so try through the website with the same image to see what the problem
            actually might be.

        For example:

        .. code-block:: python

            from praw.models import StylesheetImage

            reddit.subreddit("test").stylesheet.upload(StylesheetImage("img.png"), name="smile")

        """
        return media._upload(self.subreddit, name=name, upload_type="img")

    def upload_banner(self, media: models.StylesheetAsset, /) -> None:
        """Upload an image for the :class:`.Subreddit`'s (redesign) banner image.

        :param media: The :class:`.StylesheetAsset` to upload.

        :raises: ``prawcore.TooLarge`` if the overall request body is too large.
        :raises: :class:`.RedditAPIException` if there are other issues with the
            uploaded image. Unfortunately the exception info might not be very specific,
            so try through the website with the same image to see what the problem
            actually might be.

        For example:

        .. code-block:: python

            from praw.models import StylesheetAsset

            reddit.subreddit("test").stylesheet.upload_banner(StylesheetAsset("banner.png"))

        """
        image_type = "bannerBackgroundImage"
        image_url = media._upload(self.subreddit, image_type=image_type)
        self._update_structured_styles({image_type: image_url})

    def upload_banner_additional_image(
        self,
        media: models.StylesheetAsset,
        /,
        *,
        align: str | None = None,
    ) -> None:
        """Upload an image for the :class:`.Subreddit`'s (redesign) additional image.

        :param media: The :class:`.StylesheetAsset` to upload.
        :param align: Either ``"left"``, ``"centered"``, or ``"right"``. (default:
            ``"left"``).

        :raises: ``prawcore.TooLarge`` if the overall request body is too large.
        :raises: :class:`.RedditAPIException` if there are other issues with the
            uploaded image. Unfortunately the exception info might not be very specific,
            so try through the website with the same image to see what the problem
            actually might be.

        For example:

        .. code-block:: python

            from praw.models import StylesheetAsset

            subreddit = reddit.subreddit("test")
            subreddit.stylesheet.upload_banner_additional_image(StylesheetAsset("banner.png"))

        """
        alignment = {}
        if align is not None:
            if align not in {"left", "centered", "right"}:
                msg = "'align' argument must be either 'left', 'centered', or 'right'"
                raise ValueError(msg)
            alignment["bannerPositionedImagePosition"] = align

        image_type = "bannerPositionedImage"
        image_url = media._upload(self.subreddit, image_type=image_type)
        style_data = {image_type: image_url}
        if alignment:
            style_data.update(alignment)
        self._update_structured_styles(style_data)

    def upload_banner_hover_image(self, media: models.StylesheetAsset, /) -> None:
        """Upload an image for the :class:`.Subreddit`'s (redesign) additional image.

        :param media: The :class:`.StylesheetAsset` to upload.

        Fails if the :class:`.Subreddit` does not have an additional image defined.

        :raises: ``prawcore.TooLarge`` if the overall request body is too large.
        :raises: :class:`.RedditAPIException` if there are other issues with the
            uploaded image. Unfortunately the exception info might not be very specific,
            so try through the website with the same image to see what the problem
            actually might be.

        For example:

        .. code-block:: python

            from praw.models import StylesheetAsset

            subreddit = reddit.subreddit("test")
            subreddit.stylesheet.upload_banner_hover_image(StylesheetAsset("banner.png"))

        """
        image_type = "secondaryBannerPositionedImage"
        image_url = media._upload(self.subreddit, image_type=image_type)
        self._update_structured_styles({image_type: image_url})

    def upload_header(self, media: models.StylesheetImage, /) -> dict[str, str]:
        """Upload an image to be used as the :class:`.Subreddit`'s header image.

        :param media: The :class:`.StylesheetImage` to upload.

        :returns: A dictionary containing a link to the uploaded image under the key
            ``img_src``.

        :raises: ``prawcore.TooLarge`` if the overall request body is too large.
        :raises: :class:`.RedditAPIException` if there are other issues with the
            uploaded image. Unfortunately the exception info might not be very specific,
            so try through the website with the same image to see what the problem
            actually might be.

        For example:

        .. code-block:: python

            from praw.models import StylesheetImage

            reddit.subreddit("test").stylesheet.upload_header(StylesheetImage("header.png"))

        """
        return media._upload(self.subreddit, upload_type="header")

    def upload_mobile_banner(self, media: models.StylesheetAsset, /) -> None:
        """Upload an image for the :class:`.Subreddit`'s (redesign) mobile banner.

        :param media: The :class:`.StylesheetAsset` to upload.

        For example:

        .. code-block:: python

            from praw.models import StylesheetAsset

            subreddit = reddit.subreddit("test")
            subreddit.stylesheet.upload_mobile_banner(StylesheetAsset("banner.png"))

        Fails if the :class:`.Subreddit` does not have an additional image defined.

        :raises: ``prawcore.TooLarge`` if the overall request body is too large.
        :raises: :class:`.RedditAPIException` if there are other issues with the
            uploaded image. Unfortunately the exception info might not be very specific,
            so try through the website with the same image to see what the problem
            actually might be.

        """
        image_type = "mobileBannerImage"
        image_url = media._upload(self.subreddit, image_type=image_type)
        self._update_structured_styles({image_type: image_url})

    def upload_mobile_header(self, media: models.StylesheetImage, /) -> dict[str, str]:
        """Upload an image to be used as the :class:`.Subreddit`'s mobile header.

        :param media: The :class:`.StylesheetImage` to upload.

        :returns: A dictionary containing a link to the uploaded image under the key
            ``img_src``.

        :raises: ``prawcore.TooLarge`` if the overall request body is too large.
        :raises: :class:`.RedditAPIException` if there are other issues with the
            uploaded image. Unfortunately the exception info might not be very specific,
            so try through the website with the same image to see what the problem
            actually might be.

        For example:

        .. code-block:: python

            from praw.models import StylesheetImage

            reddit.subreddit("test").stylesheet.upload_mobile_header(StylesheetImage("header.png"))

        """
        return media._upload(self.subreddit, upload_type="banner")

    def upload_mobile_icon(self, media: models.StylesheetImage, /) -> dict[str, str]:
        """Upload an image to be used as the :class:`.Subreddit`'s mobile icon.

        :param media: The :class:`.StylesheetImage` to upload.

        :returns: A dictionary containing a link to the uploaded image under the key
            ``img_src``.

        :raises: ``prawcore.TooLarge`` if the overall request body is too large.
        :raises: :class:`.RedditAPIException` if there are other issues with the
            uploaded image. Unfortunately the exception info might not be very specific,
            so try through the website with the same image to see what the problem
            actually might be.

        For example:

        .. code-block:: python

            from praw.models import StylesheetImage

            reddit.subreddit("test").stylesheet.upload_mobile_icon(StylesheetImage("icon.png"))

        """
        return media._upload(self.subreddit, upload_type="icon")
