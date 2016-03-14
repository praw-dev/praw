"""Provide the ModeratableMixin class."""


class ModeratableMixin(object):
    """Interface for classes that can be moderated."""

    def approve(self):
        """Approve object.

        This reverts a removal, resets the report counter, marks it with a
        green check mark (only visible to other moderators) on the website view
        and sets the approved_by attribute to the logged in user.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['approve']
        data = {'id': self.fullname}
        return self.reddit_session.request_json(url, data=data)

    def distinguish(self, as_made_by='mod'):
        """Distinguish object as made by mod, admin or special.

        Distinguished objects have a different author color. With Reddit
        Enhancement Suite it is the background color that changes.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['distinguish']
        data = {'id': self.fullname,
                'how': 'yes' if as_made_by == 'mod' else as_made_by}
        return self.reddit_session.request_json(url, data=data)

    def ignore_reports(self):
        """Ignore future reports on this object.

        This prevents future reports from causing notifications or appearing
        in the various moderation listing. The report count will still
        increment.

        """
        url = self.reddit_session.config['ignore_reports']
        data = {'id': self.fullname}
        return self.reddit_session.request_json(url, data=data)

    def remove(self, spam=False):
        """Remove object. This is the moderator version of delete.

        The object is removed from the subreddit listings and placed into the
        spam listing. If spam is set to True, then the automatic spam filter
        will try to remove objects with similar attributes in the future.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['remove']
        data = {'id': self.fullname,
                'spam': 'True' if spam else 'False'}
        return self.reddit_session.request_json(url, data=data)

    def undistinguish(self):
        """Remove mod, admin or special distinguishing on object.

        :returns: The json response from the server.

        """
        return self.distinguish(as_made_by='no')

    def unignore_reports(self):
        """Remove ignoring of future reports on this object.

        Undoes 'ignore_reports'. Future reports will now cause notifications
        and appear in the various moderation listings.

        """
        url = self.reddit_session.config['unignore_reports']
        data = {'id': self.fullname}
        return self.reddit_session.request_json(url, data=data)
