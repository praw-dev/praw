"""Provide the EditableMixin class."""
from ....const import API_PATH


class EditableMixin:
    """Interface for classes that can be edited and deleted."""

    def delete(self):
        """Delete the object.

        Example usage:

        .. code:: python

           comment = reddit.comment('dkk4qjd')
           comment.delete()

           submission = reddit.submission('8dmv8z')
           submission.delete()

        """
        self._reddit._request_and_check_error(
            "POST", API_PATH["del"], data={"id": self.fullname}
        )

    def edit(self, body):
        """Replace the body of the object with ``body``.

        :param body: The markdown formatted content for the updated object.
        :returns: The current instance after updating its attributes.

        Example usage:

        .. code:: python

           comment = reddit.comment('dkk4qjd')

           #construct edited comment text by appending to old body
           edited_body = comment.body + "Edit: thanks for the gold!"
           comment.edit(edited_body)

        """
        data = {"text": body, "thing_id": self.fullname}
        response_data = self._reddit._request_and_check_error(
            "POST", API_PATH["edit"], data=data
        )

        updated = None
        schema = response_data["json"]["data"]["things"][0]
        if schema["kind"] == self._reddit.config.kinds["comment"]:
            updated = self._reddit._objector.parsers[
                self._reddit.config.kinds["comment"]
            ](self._reddit, _data=schema["data"])
        elif schema["kind"] == self._reddit.config.kinds["submission"]:
            updated = self._reddit._objector.parsers[
                self._reddit.config.kinds["submission"]
            ](self._reddit, _data=schema["data"])

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
