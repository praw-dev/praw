"""Provide the SubredditStylesheet class."""

from os.path import basename

from ....const import API_PATH, JPEG_HEADER
from ....exceptions import RedditAPIException


class SubredditStylesheet:
    """Provides a set of stylesheet functions to a Subreddit.

    For example, to add the css data ``.test{color:blue}`` to the existing
    stylesheet:

    .. code-block:: python

        subreddit = reddit.subreddit('SUBREDDIT')
        stylesheet = subreddit.stylesheet()
        stylesheet += ".test{color:blue}"
        subreddit.stylesheet.update(stylesheet)

    """

    def __call__(self):
        """Return the subreddit's stylesheet.

        To be used as:

        .. code-block:: python

           stylesheet = reddit.subreddit('SUBREDDIT').stylesheet()

        """
        url = API_PATH["about_stylesheet"].format(subreddit=self.subreddit)
        return self.subreddit._reddit.get(url)

    def __init__(self, subreddit):
        """Create a SubredditStylesheet instance.

        :param subreddit: The subreddit associated with the stylesheet.

        An instance of this class is provided as:

        .. code-block:: python

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
                raise RedditAPIException([[error_type, error_value, None]])
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

        For example:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_banner()

        """
        data = {"bannerBackgroundImage": ""}
        self._update_structured_styles(data)

    def delete_banner_additional_image(self):
        """Remove the current subreddit (redesign) banner additional image.

        Succeeds even if there is no additional image.  Will also delete any
        configured hover image.

        For example:

        .. code-block:: python

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

        For example:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_banner_hover_image()

        """
        data = {"secondaryBannerPositionedImage": ""}
        self._update_structured_styles(data)

    def delete_header(self):
        """Remove the current subreddit header image.

        Succeeds even if there is no header image.

        For example:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_header()

        """
        url = API_PATH["delete_sr_header"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def delete_image(self, name):
        """Remove the named image from the subreddit.

        Succeeds even if the named image does not exist.

        For example:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_image('smile')

        """
        url = API_PATH["delete_sr_image"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data={"img_name": name})

    def delete_mobile_header(self):
        """Remove the current subreddit mobile header.

        Succeeds even if there is no mobile header.

        For example:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_mobile_header()

        """
        url = API_PATH["delete_sr_header"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def delete_mobile_icon(self):
        """Remove the current subreddit mobile icon.

        Succeeds even if there is no mobile icon.

        For example:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').stylesheet.delete_mobile_icon()

        """
        url = API_PATH["delete_sr_icon"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url)

    def update(self, stylesheet, reason=None):
        """Update the subreddit's stylesheet.

        :param stylesheet: The CSS for the new stylesheet.

        For example:

        .. code-block:: python

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

        Raises :class:`.RedditAPIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        For example:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload('smile', 'img.png')

        """
        return self._upload_image(
            image_path, {"name": name, "upload_type": "img"}
        )

    def upload_banner(self, image_path):
        """Upload an image for the subreddit's (redesign) banner image.

        :param image_path: A path to a jpeg or png image.

        Raises ``prawcore.TooLarge`` if the overall request body is too large.

        Raises :class:`.RedditAPIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        For example:

        .. code-block:: python

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

        Raises :class:`.RedditAPIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        For example:

        .. code-block:: python

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

        Raises :class:`.RedditAPIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        For example:

        .. code-block:: python

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

        Raises :class:`.RedditAPIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        For example:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload_header('header.png')

        """
        return self._upload_image(image_path, {"upload_type": "header"})

    def upload_mobile_header(self, image_path):
        """Upload an image to be used as the Subreddit's mobile header.

        :param image_path: A path to a jpeg or png image.
        :returns: A dictionary containing a link to the uploaded image under
            the key ``img_src``.

        Raises ``prawcore.TooLarge`` if the overall request body is too large.

        Raises :class:`.RedditAPIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        For example:

        .. code-block:: python

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

        Raises :class:`.RedditAPIException` if there are other issues with the
        uploaded image. Unfortunately the exception info might not be very
        specific, so try through the website with the same image to see what
        the problem actually might be.

        For example:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').stylesheet.upload_mobile_icon(
               'icon.png')

        """
        return self._upload_image(image_path, {"upload_type": "icon"})
