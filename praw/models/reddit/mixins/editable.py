"""Provide the EditableMixin class."""


class EditableMixin(object):
    """Interface for classes that can be edited and deleted."""

    def delete(self):
        """Delete this object.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['del']
        data = {'id': self.fullname}
        return self.reddit_session.request_json(url, data=data)

    def edit(self, text):
        """Replace the body of the object with `text`.

        :returns: The updated object.

        """
        url = self.reddit_session.config['edit']
        data = {'thing_id': self.fullname,
                'text': text}
        response = self.reddit_session.request_json(url, data=data)
        return response['data']['things'][0]
