# This file is part of reddit_api.
#
# reddit_api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# reddit_api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with reddit_api.  If not, see <http://www.gnu.org/licenses/>.

from urlparse import urljoin

from reddit.decorators import require_login
from reddit.helpers import _get_section, _get_sorter, _modify_relationship
from reddit.helpers import _request
from reddit.settings import DEFAULT_CONTENT_LIMIT
from reddit.util import limit_chars


class RedditContentObject(object):
    """Base class that  represents actual reddit objects."""
    def __init__(self, reddit_session, name=None, json_dict=None, fetch=True,
                 info_url=None):
        """
        Create a new object either by name or from the dict of attributes
        returned by the API. Creating by name will retrieve the proper dict
        from the API.

        The fetch parameter specifies whether to retrieve the object's
        information from the API (only matters when it isn't provided using
        json_dict).
        """
        if name is None and json_dict is None:
            raise TypeError("Either the name or json dict is required.")

        if info_url:
            self._info_url = info_url
        else:
            self._info_url = reddit_session.config["info"]
        self.reddit_session = reddit_session
        self._populate(json_dict, fetch)

    def _populate(self, json_dict, fetch):
        if json_dict is None:
            if fetch:
                json_dict = self._get_json_dict()
            else:
                json_dict = {}
        for name, value in json_dict.iteritems():
            setattr(self, name, value)
        self._populated = bool(json_dict) or fetch

    def __getattr__(self, attr):
        if not self._populated:
            self._populate(None, True)
            return getattr(self, attr)
        raise AttributeError

    def __setattr__(self, name, value):
        if name == "subreddit":
            value = Subreddit(self.reddit_session, value, fetch=False)
        elif name == "redditor" or name == "author":
            # Special case for deleted users
            if value != '[deleted]':
                value = Redditor(self.reddit_session, value, fetch=False)
        object.__setattr__(self, name, value)

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.content_id == other.content_id)

    def __ne__(self, other):
        return (type(self) != type(other) or
                self.content_id != other.content_id)

    def _get_json_dict(self):
        response = self.reddit_session.request_json(self._info_url,
                                                    as_objects=False)
        return response["data"]

    @classmethod
    def from_api_response(cls, reddit_session, json_dict):
        return cls(reddit_session, json_dict=json_dict)

    @property
    def content_id(self):
        """
        Get the content id for this object. Just prepends the appropriate
        content type to this object's id.
        """
        om = self.reddit_session.config.object_mapping
        return '%s_%s' % (om[self.__class__], self.id)


class Saveable(RedditContentObject):
    """
    Additional interface for Reddit content objects that can be saved.
    Currently only Submissions, but this may change at a later date, as
    eventually Comments will probably end up being saveable.
    """
    @require_login
    def save(self, unsave=False):
        """If logged in, save the content."""
        url = self.reddit_session.config['unsave' if unsave else 'save']
        params = {'id': self.content_id,
                  'executed': 'unsaved' if unsave else 'saved',
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        response = self.reddit_session.request_json(url, params)
        _request.is_stale([self.reddit_session.config['saved']])
        return response

    def unsave(self):
        return self.save(unsave=True)


class Deletable(RedditContentObject):
    """
    Additional Interface for Reddit content objects that can be deleted
    (currently Submission and Comment).
    """
    def delete(self):
        url = self.reddit_session.config['del']
        params = {'id': self.content_id,
                  'executed': 'deleted',
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        response = self.reddit_session.request_json(url, params)
        _request.is_stale([self.reddit_session.config['user']])
        return response


class Voteable(RedditContentObject):
    """
    Additional interface for Reddit content objects that can be voted on
    (currently Submission and Comment).
    """
    @require_login
    def vote(self, direction=0):
        """
        Vote for the given item in the direction specified.
        """
        url = self.reddit_session.config['vote']
        params = {'id': self.content_id,
                  'dir': str(direction),
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        return self.reddit_session.request_json(url, params)

    def upvote(self):
        return self.vote(direction=1)

    def downvote(self):
        return self.vote(direction=-1)

    def clear_vote(self):
        return self.vote()


class Comment(Deletable, Voteable):
    """A class for comments."""
    def __init__(self, reddit_session, json_dict):
        super(Comment, self).__init__(reddit_session, None, json_dict)
        if self.replies:
            self.replies = self.replies['data']['children']
            for reply in self.replies:
                reply.parent = self
        else:
            self.replies = []
        self.parent = None
        self.submission = None

    @limit_chars()
    def __str__(self):
        return getattr(self, 'body', '[Unloaded Comment]').encode('utf8')

    @property
    def is_root(self):
        return hasattr(self, 'parent')

    @property
    def permalink(self):
        return urljoin(self.submission.permalink, self.id)

    def _update_submission(self, submission):
        """Submission isn't set on __init__ thus we need to update it."""
        self.submission = submission
        for reply in self.replies:
            reply._update_submission(submission)

    def reply(self, text):
        """Reply to the comment with the specified text."""
        return self.reddit_session._add_comment(self.content_id, text)

    def mark_read(self):
        """ Marks the comment as read """
        return self.reddit_session._mark_as_read([self.content_id])


class MoreComments(RedditContentObject):
    """A class indicating there are more comments."""
    def __init__(self, reddit_session, json_dict):
        super(MoreComments, self).__init__(reddit_session, None, json_dict)

    def _update_submission(self, _):
        pass

    def __str__(self):
        return '[More Comments]'.encode('utf8')

    @property
    def comments(self):
        url = urljoin(self.parent.submission.permalink, self.parent.id)
        submission_info, comment_info = self.reddit_session.request_json(url)
        comments = comment_info['data']['children']

        # We need to return the children of the parent as we already have
        # the parent
        assert(len(comments) == 1)
        return comments[0].replies


class Redditor(RedditContentObject):
    """A class for Redditor methods."""
    get_overview = _get_section('')
    get_comments = _get_section('comments')
    get_submitted = _get_section('submitted')

    def __init__(self, reddit_session, user_name=None, json_dict=None,
                 fetch=True):
        info_url = reddit_session.config['user_about'] % user_name
        super(Redditor, self).__init__(reddit_session, user_name, json_dict,
                                       fetch, info_url)
        self.name = user_name
        self._url = reddit_session.config['user'] % user_name

    @limit_chars()
    def __str__(self):
        """Display the user's name."""
        return self.name.encode('utf8')

    @require_login
    def compose_message(self, subject, message):
        return self.reddit_session.compose_message(self, subject, message)

    @require_login
    def friend(self):
        """Friend the user."""
        _modify_relationship('friend')(self.reddit_session.user, self)

    @require_login
    def unfriend(self):
        """Unfriend the user."""
        _modify_relationship('friend', unlink=True)(self.reddit_session.user,
                                                    self)


class LoggedInRedditor(Redditor):
    """A class for a currently logged in redditor"""
    @require_login
    def my_reddits(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return all of the current user's subscribed subreddits."""
        url = self.reddit_session.config['my_reddits']
        return self.reddit_session.get_content(url, limit=limit)

    @require_login
    def my_moderation(self, limit=DEFAULT_CONTENT_LIMIT):
        """Return all of the current user's subreddits that they moderate."""
        url = self.reddit_session.config['my_moderation']
        return self.reddit_session.get_content(url, limit=limit)

    @require_login
    def get_inbox(self):
        """Return a generator for inbox messages."""
        url = self.reddit_session.config['inbox']
        return self.reddit_session.get_content(url)

    @require_login
    def get_sent(self):
        """Return a generator for sent messages."""
        url = self.reddit_session.config['sent']
        return self.reddit_session.get_content(url)

    @require_login
    def get_modmail(self):
        """Return a generator for moderator messages."""
        url = self.reddit_session.config['moderator']
        return self.reddit_session.get_content(url)


class Submission(Deletable, Saveable, Voteable):
    """A class for submissions to Reddit."""
    def __init__(self, reddit_session, json_dict):
        super(Submission, self).__init__(reddit_session, None, json_dict)
        if not self.permalink.startswith(reddit_session.config['reddit_url']):
            self.permalink = urljoin(reddit_session.config['reddit_url'],
                                     self.permalink)
        self._comments = None

    def __str__(self):
        title = self.title.replace('\r\n', ' ').encode('utf-8')
        return '{0} :: {1}'.format(self.score, title)

    @property
    def comments(self):
        if self._comments == None:
            submission_info, comment_info = self.reddit_session.request_json(
                self.permalink)
            self._comments = comment_info['data']['children']
            for comment in self._comments:
                comment._update_submission(self)
        return self._comments

    @comments.setter
    def comments(self, new_comments):
        for comment in new_comments:
            comment._update_submission(self)
        self._comments = new_comments

    def add_comment(self, text):
        """If logged in, comment on the submission using the specified text."""
        return self.reddit_session._add_comment(self.content_id, text)


class Subreddit(RedditContentObject):
    """A class for Subreddits."""

    ban = _modify_relationship('banned')
    unban = _modify_relationship('banned', unlink=True)
    make_contributor = _modify_relationship('contributor')
    remove_contributor = _modify_relationship('contributor', unlink=True)
    make_moderator = _modify_relationship('moderator')
    remove_moderator = _modify_relationship('moderator', unlink=True)

    get_hot = _get_sorter('')
    get_controversial = _get_sorter('controversial', time='day')
    get_new = _get_sorter('new', sort='rising')
    get_top = _get_sorter('top', time='day')
    get_new_by_date = _get_sorter('new', sort='new')

    def __init__(self, reddit_session, subreddit_name=None, json_dict=None,
                 fetch=False):
        info_url = (reddit_session.config['subreddit_about'] %
                    subreddit_name)
        super(Subreddit, self).__init__(reddit_session, subreddit_name,
                                        json_dict, fetch, info_url)
        self.display_name = subreddit_name
        self._url = reddit_session.config['subreddit'] % subreddit_name

    @limit_chars()
    def __str__(self):
        """Display the subreddit name."""
        return self.display_name.encode('utf8')

    def add_flair_template(self, *args, **kwargs):
        """Adds a flair template to the subreddit."""
        return self.reddit_session.add_flair_template(self, *args, **kwargs)

    def clear_flair_templates(self, *args, **kwargs):
        """Clear flair templates for this subreddit."""
        return self.reddit_session.clear_flair_templates(self, *args, **kwargs)

    def flair_list(self, *args, **kwargs):
        """Return a list of flair for this subreddit."""
        return self.reddit_session.flair_list(self, *args, **kwargs)

    def set_flair(self, *args, **kwargs):
        """Set flair for a particular user."""
        return self.reddit_session.set_flair(self, *args, **kwargs)

    def set_flair_csv(self, *args, **kwargs):
        """Set flair for a group of users all at once."""
        return self.reddit_session.set_flair_csv(self, *args, **kwargs)

    def submit(self, *args, **kwargs):
        """Submit a new link."""
        return self.reddit_session.submit(self, *args, **kwargs)

    @require_login
    def _subscribe(self, unsubscribe=False):
        """Perform the (un)subscribe to the subreddit."""
        action = 'unsub' if unsubscribe else 'sub'
        params = {'sr': self.content_id,
                  'action': action,
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        url = self.reddit_session.config['subscribe']
        return self.reddit_session.request_json(url, params)

    def subscribe(self):
        """Subscribe to the given subreddit."""
        return self._subscribe()

    def unsubscribe(self):
        """Unsubscribe from the given subreddit."""
        return self._subscribe(unsubscribe=True)
