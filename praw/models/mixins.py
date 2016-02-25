"""Provide mixins used by other models."""

from six import text_type

from .redditcontentobject import RedditContentObject


class Moderatable(RedditContentObject):
    """Interface for Reddit content objects that have can be moderated."""

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


class Editable(RedditContentObject):
    """Interface for Reddit content objects that can be edited and deleted."""

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


class Gildable(RedditContentObject):
    """Interface for RedditContentObjects that can be gilded."""

    def gild(self, months=None):
        """Gild the Redditor or author of the content.

        :param months: Specifies the number of months to gild. This parameter
            is Only valid when the instance called upon is of type
            Redditor. When not provided, the value defaults to 1.
        :returns: True on success, otherwise raises an exception.

        """
        from .redditor import Redditor

        if isinstance(self, Redditor):
            months = int(months) if months is not None else 1
            if months < 1:
                raise TypeError('months must be at least 1')
            if months > 36:
                raise TypeError('months must be no more than 36')
            response = self.reddit_session.request(
                self.reddit_session.config['gild_user'].format(
                    username=text_type(self)), data={'months': months})
        elif months is not None:
            raise TypeError('months is not a valid parameter for {0}'
                            .format(type(self)))
        else:
            response = self.reddit_session.request(
                self.reddit_session.config['gild_thing']
                .format(fullname=self.fullname), data=True)
        return response.status_code == 200


class Hideable(RedditContentObject):
    """Interface for objects that can be hidden."""

    def hide(self, _unhide=False):
        """Hide object in the context of the logged in user.

        :param _unhide: If True, unhide the item instead.  Use
            :meth:`~praw.objects.Hideable.unhide` instead of setting this
            manually.

        :returns: The json response from the server.

        """
        return self.reddit_session.hide(self.fullname, _unhide=_unhide)

    def unhide(self):
        """Unhide object in the context of the logged in user.

        :returns: The json response from the server.

        """
        return self.hide(_unhide=True)


class Inboxable(RedditContentObject):
    """Interface for objects that appear in the inbox (orangereds)."""

    def mark_as_read(self):
        """Mark object as read.

        :returns: The json response from the server.

        """
        return self.reddit_session._mark_as_read([self.fullname])

    def mark_as_unread(self):
        """Mark object as unread.

        :returns: The json response from the server.

        """
        return self.reddit_session._mark_as_read([self.fullname], unread=True)

    def reply(self, text):
        """Reply to object with the specified text.

        :returns: A Comment object for the newly created comment (reply).

        """
        return self.reddit_session._add_comment(self.fullname, text)


class Messageable(RedditContentObject):
    """Interface for RedditContentObjects that can be messaged."""

    _methods = (('send_message', 'PMMix'),)


class Reportable(RedditContentObject):
    """Interface for RedditContentObjects that can be reported."""

    def report(self, reason=None):
        """Report this object to the moderators.

        :param reason: The user-supplied reason for reporting a comment
            or submission. Default: None (blank reason)
        :returns: The json response from the server.

        """
        url = self.reddit_session.config['report']
        data = {'id': self.fullname}
        if reason:
            data['reason'] = reason
        return self.reddit_session.request_json(url, data=data)


class Saveable(RedditContentObject):
    """Interface for RedditContentObjects that can be saved."""

    def save(self, unsave=False):
        """Save the object.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['unsave' if unsave else 'save']
        data = {'id': self.fullname,
                'executed': 'unsaved' if unsave else 'saved'}
        return self.reddit_session.request_json(url, data=data)

    def unsave(self):
        """Unsave the object.

        :returns: The json response from the server.

        """
        return self.save(unsave=True)


class Voteable(RedditContentObject):
    """Interface for RedditContentObjects that can be voted on."""

    def clear_vote(self):
        """Remove the logged in user's vote on the object.

        Running this on an object with no existing vote has no adverse effects.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        :returns: The json response from the server.

        """
        return self.vote()

    def downvote(self):
        """Downvote object. If there already is a vote, replace it.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        :returns: The json response from the server.

        """
        return self.vote(direction=-1)

    def upvote(self):
        """Upvote object. If there already is a vote, replace it.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        :returns: The json response from the server.

        """
        return self.vote(direction=1)

    def vote(self, direction=0):
        """Vote for the given item in the direction specified.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['vote']
        data = {'id': self.fullname,
                'dir': text_type(direction)}
        return self.reddit_session.request_json(url, data=data)
