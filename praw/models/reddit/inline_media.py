"""Provide classes related to inline media."""


class InlineMedia:
    """Provides a way to embed media in self posts."""

    TYPE = None

    def __init__(self, path: str, caption: str = None):
        """Create an InlineMedia instance.

        :param path: The path to a media file.
        :param caption: An optional caption to add to the image. (default: None)

        """
        self.path = path
        self.caption = caption
        self.media_id = None

    def __eq__(self, other: "InlineMedia"):
        """Return whether the other instance equals the current."""
        return all(
            [
                getattr(self, attr) == getattr(other, attr)
                for attr in ["TYPE", "path", "caption", "media_id"]
            ]
        )

    def __repr__(self) -> str:
        """Return a string representation of the InlineMedia instance."""
        return f"<{self.__class__.__name__} caption={self.caption!r}>"

    def __str__(self):
        """Return a string representation of the media in Markdown format."""
        return f'\n\n![{self.TYPE}]({self.media_id} "{self.caption if self.caption else ""}")\n\n'


class InlineGif(InlineMedia):
    """Class to provide a gif to embed in text."""

    TYPE = "gif"


class InlineVideo(InlineMedia):
    """Class to provide a video to embed in text."""

    TYPE = "video"


class InlineImage(InlineMedia):
    """Class to provide am image to embed in text."""

    TYPE = "img"
