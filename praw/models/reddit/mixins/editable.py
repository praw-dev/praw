"""Provide the EditableMixin class."""
from ....const import API_PATH


class EditableMixin(object):
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
        self._reddit.post(API_PATH['del'], {'id': self.fullname})

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
        data = {'text': body, 'thing_id': self.fullname}
        updated = self._reddit.post(API_PATH['edit'], data=data)[0]
        for attribute in ['_fetched', '_reddit', '_submission', 'replies',
                          'subreddit']:
            if attribute in updated.__dict__:
                delattr(updated, attribute)
        self.__dict__.update(updated.__dict__)
        return self
