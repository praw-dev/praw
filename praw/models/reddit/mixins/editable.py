"""Provide the EditableMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from praw.const import API_PATH

if TYPE_CHECKING:
    import datetime
    from collections.abc import Callable

    from typing_extensions import Self

    import praw


class EditableMixin:
    """Interface for classes that can be edited and deleted."""

    if TYPE_CHECKING:
        # Provided by the host class (:class:`.RedditBase`).
        _reddit: praw.Reddit
        _to_local_datetime: Callable[[float], datetime.datetime]
        edited: bool | float

        @property
        def fullname(self) -> str: ...  # noqa: D102

    @property
    def edited_datetime(self) -> datetime.datetime | None:
        """Return the last edit time as a timezone-aware :class:`datetime.datetime`.

        Returns ``None`` if the object has never been edited. The returned object is
        localized to the system's timezone.

        """
        if self.edited is False:
            return None
        return self._to_local_datetime(self.edited)

    def delete(self) -> None:
        """Delete the object.

        Example usage:

        .. code-block:: python

            comment = reddit.comment("dkk4qjd")
            comment.delete()

            submission = reddit.submission("8dmv8z")
            submission.delete()

        """
        self._reddit.post(API_PATH["del"], data={"id": self.fullname})

    def edit(self, body: str) -> Self:
        """Replace the body of the object with ``body``.

        :param body: The Markdown formatted content for the updated object.

        :returns: The current instance after updating its attributes.

        Example usage:

        .. code-block:: python

            comment = reddit.comment("dkk4qjd")

            # construct the text of an edited comment
            # by appending to the old body:
            edited_body = comment.body + "Edit: thanks for the gold!"
            comment.edit(edited_body)

        """
        data = {
            "text": body,
            "thing_id": self.fullname,
            "validate_on_submit": True,
        }
        updated = self._reddit.post(API_PATH["edit"], data=data)[0]
        for attribute in [
            "_fetched",
            "_reddit",
            "_submission",
            "replies",
            "subreddit",
        ]:
            if attribute in updated.__dict__:
                delattr(updated, attribute)
        self.__dict__.update(updated.__dict__)
        return self
