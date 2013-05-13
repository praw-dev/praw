# This file is part of PRAW.
#
# PRAW is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PRAW is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PRAW.  If not, see <http://www.gnu.org/licenses/>.

"""
Contains code about objects such as Submissions, Redditors or Commments.

There are two main groups of objects in this file. The first are objects that
correspond to a Thing or part of a Thing as specified in reddit's API overview,
https://github.com/reddit/reddit/wiki/API. The second gives functionality that
extends over multiple Things. An object that extends from Saveable indicates
that it can be saved and unsaved in the context of a logged in user.
"""

import six
from heapq import heappop, heappush
from requests.compat import urljoin
from praw import (AuthenticatedReddit as AR, ModConfigMixin as MCMix,
                  ModFlairMixin as MFMix, ModLogMixin as MLMix,
                  ModOnlyMixin as MOMix, PrivateMessagesMixin as PMMix,
                  SubmitMixin, SubscribeMixin, UnauthenticatedReddit as UR)
from praw.decorators import alias_function, limit_chars, restrict_access
from praw.errors import ClientException
from praw.internal import _get_section, _get_sorter, _modify_relationship


REDDITOR_KEYS = ('approved_by', 'author', 'banned_by', 'redditor')


class RedditContentObject(object):

    """Base class that represents actual reddit objects."""

    @classmethod
    def from_api_response(cls, reddit_session, json_dict):
        """Return an instance of the appropriate class from the json_dict."""
        if cls == WikiPage:  # Temporary HACK for WikiPage
            # pylint: disable-msg=W0212
            parts = reddit_session._request_url.split('/', 6)
            # pylint: enable-msg=W0212
            subreddit = parts[4]
            page = parts[6].split('.', 1)[0]
            return cls(reddit_session, subreddit, page, json_dict=json_dict)
        return cls(reddit_session, json_dict=json_dict)

    def __init__(self, reddit_session, json_dict=None, fetch=True,
                 info_url=None, underscore_names=None):
        """Create a new object from the dict of attributes returned by the API.

        The fetch parameter specifies whether to retrieve the object's
        information from the API (only matters when it isn't provided using
        json_dict).

        """
        if info_url:
            self._info_url = info_url
        else:
            self._info_url = reddit_session.config['info']
        self.reddit_session = reddit_session
        self._underscore_names = underscore_names
        self._populated = self._populate(json_dict, fetch)

    def __eq__(self, other):
        return (isinstance(other, RedditContentObject) and
                self.fullname == other.fullname)

    def __getattr__(self, attr):
        if not self._populated:
            self._populated = self._populate(None, True)
            return getattr(self, attr)
        raise AttributeError('\'%s\' has no attribute \'%s\'' % (type(self),
                                                                 attr))

    def __ne__(self, other):
        return not (self == other)

    def __setattr__(self, name, value):
        if value and name == 'subreddit':
            value = Subreddit(self.reddit_session, value, fetch=False)
        elif value and name in REDDITOR_KEYS:
            if isinstance(value, bool):
                pass
            elif not value or value == '[deleted]':
                value = None
            else:
                value = Redditor(self.reddit_session, value, fetch=False)
        object.__setattr__(self, name, value)

    def __str__(self):
        retval = self.__unicode__()
        if not six.PY3:
            retval = retval.encode('utf-8')
        return retval

    def _get_json_dict(self):
        # (disbled for entire function) pylint: disable-msg=W0212

        # OAuth handling needs to be special cased here. For instance, the user
        # might be calling a method on a Subreddit object that requires first
        # loading the information about the subreddit. Unless the `read` scope
        # is set, then this function should try to obtain the information in a
        # scope-less manner.
        prev_use_oauth = self.reddit_session._use_oauth
        self.reddit_session._use_oauth = self.reddit_session.has_scope('read')
        try:
            response = self.reddit_session.request_json(self._info_url,
                                                        as_objects=False)
        finally:
            self.reddit_session._use_oauth = prev_use_oauth
        return response['data']

    def _populate(self, json_dict, fetch):
        if json_dict is None:
            if fetch:
                json_dict = self._get_json_dict()
            else:
                json_dict = {}

        # TODO: Remove this wikipagelisting hack
        if isinstance(json_dict, list):
            json_dict = {'_tmp': json_dict}

        for name, value in six.iteritems(json_dict):
            if self._underscore_names and name in self._underscore_names:
                name = '_' + name
            setattr(self, name, value)
        return bool(json_dict) or fetch

    @property
    def fullname(self):
        """Return the object's fullname.

        A fullname is an object's kind mapping like `t3` followed by an
        underscore and the object's base36 id, e.g., `t1_c5s96e0`.

        """
        by_object = self.reddit_session.config.by_object
        return '%s_%s' % (by_object[self.__class__], self.id)


class Moderatable(RedditContentObject):

    """Interface for Reddit content objects that have can be moderated."""

    @restrict_access(scope='modposts')
    def approve(self):
        """Approve object.

        This reverts a removal, resets the report counter, marks it with a
        green check mark (only visible to other moderators) on the website view
        and sets the approved_by attribute to the logged in user.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['approve']
        data = {'id': self.fullname}
        response = self.reddit_session.request_json(url, data=data)
        urls = [self.reddit_session.config[x] for x in ['modqueue', 'spam']]
        if isinstance(self, Submission):
            urls += self.subreddit._listing_urls  # pylint: disable-msg=W0212
        self.reddit_session.evict(urls)
        return response

    @restrict_access(scope='modposts')
    def distinguish(self, as_made_by='mod'):
        """Distinguish object as made by mod, admin or special.

        Distinguished objects have a different author color. With Reddit
        enhancement suite it is the background color that changes.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['distinguish']
        data = {'id': self.fullname,
                'how': 'yes' if as_made_by == 'mod' else as_made_by}
        return self.reddit_session.request_json(url, data=data)

    @restrict_access(scope='modposts')
    def mark_as_nsfw(self, unmark_nsfw=False):
        """Mark object as Not Safe For Work.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['unmarknsfw' if unmark_nsfw else
                                         'marknsfw']
        data = {'id': self.fullname}
        return self.reddit_session.request_json(url, data=data)

    @restrict_access(scope='modposts')
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
        response = self.reddit_session.request_json(url, data=data)
        urls = [self.reddit_session.config[x] for x in ['modqueue', 'spam']]
        if isinstance(self, Submission) and hasattr(self, 'subreddit'):
            urls += self.subreddit._listing_urls  # pylint: disable-msg=W0212
        self.reddit_session.evict(urls)
        return response

    def undistinguish(self):
        """Remove mod, admin or special distinguishing on object.

        :returns: The json response from the server.

        """
        return self.distinguish(as_made_by='no')

    def unmark_as_nsfw(self):
        """Mark object as Safe For Work.

        :returns: The json response from the server.

        """
        return self.mark_as_nsfw(unmark_nsfw=True)


class Editable(RedditContentObject):

    """Interface for Reddit content objects that can be edited and deleted."""

    @restrict_access(scope='edit')
    def delete(self):
        """Delete this object.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['del']
        data = {'id': self.fullname}
        response = self.reddit_session.request_json(url, data=data)
        self.reddit_session.evict(self.reddit_session.config['user'])
        return response

    @restrict_access(scope='edit')
    def edit(self, text):
        """Replace the body of the object with `text`.

        :returns: The updated object.

        """
        url = self.reddit_session.config['edit']
        data = {'thing_id': self.fullname,
                'text': text}
        response = self.reddit_session.request_json(url, data=data)
        self.reddit_session.evict(self.reddit_session.config['user'])
        # REDDIT: reddit's end should only ever return a single comment
        return response['data']['things'][0]


class Hideable(RedditContentObject):

    """Interface for objects that can be hidden."""

    @restrict_access(scope=None, login=True)
    def hide(self, unhide=False):
        """Hide object in the context of the logged in user.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['unhide' if unhide else 'hide']
        data = {'id': self.fullname,
                'executed': 'unhide' if unhide else 'hide'}
        response = self.reddit_session.request_json(url, data=data)
        # pylint: disable-msg=W0212
        urls = [urljoin(self.reddit_session.user._url, 'hidden')]
        # pylint: enable-msg=W0212
        self.reddit_session.evict(urls)
        return response

    def unhide(self):
        """Unhide object in the context of the logged in user.

        :returns: The json response from the server.

        """
        return self.hide(unhide=True)


class Inboxable(RedditContentObject):

    """Interface for Reddit content objects that appear in the Inbox."""

    def mark_as_read(self):
        """Mark object as read.

        :returns: The json response from the server.

        """
        return self.reddit_session.user.mark_as_read(self)

    def mark_as_unread(self):
        """Mark object as unread.

        :returns: The json response from the server.

        """
        return self.reddit_session.user.mark_as_read(self, unread=True)

    def reply(self, text):
        """Reply to object with the specified text.

        :returns: A Comment object for the newly created comment (reply).

        """
        # pylint: disable-msg=W0212
        response = self.reddit_session._add_comment(self.fullname, text)
        # pylint: enable-msg=W0212
        urls = [self.reddit_session.config['inbox']]
        if isinstance(self, Comment):
            urls.append(self.submission.permalink)
        elif isinstance(self, Message):
            urls.append(self.reddit_session.config['sent'])
        self.reddit_session.evict(urls)
        return response


class Messageable(RedditContentObject):

    """Interface for RedditContentObjects that can be messaged."""

    _methods = (('send_message', PMMix),)


class Refreshable(RedditContentObject):

    """Interface for objects that can be refreshed."""

    def refresh(self):
        """Re-query to update object with latest values.

        Note that if this call is made within cache_timeout as specified in
        praw.ini then this will return the cached content. Any listing, such
        as the submissions on a subreddits top page, will automatically be
        refreshed serverside. Refreshing a submission will also refresh all its
        comments.

        """
        if isinstance(self, Redditor):
            other = Redditor(self.reddit_session, self.name)
        elif isinstance(self, Submission):
            other = Submission.from_url(self.reddit_session, self.permalink)
        elif isinstance(self, Subreddit):
            other = Subreddit(self.reddit_session, self.display_name)
        self.__dict__ = other.__dict__  # pylint: disable-msg=W0201


class Reportable(RedditContentObject):

    """Interface for RedditContentObjects that can be reported."""

    @restrict_access(scope=None, login=True)
    def report(self):
        """Report this object to the moderators.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['report']
        data = {'id': self.fullname}
        response = self.reddit_session.request_json(url, data=data)
        # Reported objects are automatically hidden as well
        # pylint: disable-msg=W0212
        urls = [self.reddit_session.config['user'],
                urljoin(self.reddit_session.user._url, 'hidden')]
        # pylint: enable-msg=W0212
        self.reddit_session.evict(urls)
        return response


class Saveable(RedditContentObject):

    """Interface for RedditContentObjects that can be saved."""

    @restrict_access(scope=None, login=True)
    def save(self, unsave=False):
        """Save the object.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['unsave' if unsave else 'save']
        data = {'id': self.fullname,
                'executed': 'unsaved' if unsave else 'saved'}
        response = self.reddit_session.request_json(url, data=data)
        self.reddit_session.evict(self.reddit_session.config['saved'])
        return response

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

        :returns: The json response from the server.

        """
        return self.vote()

    def downvote(self):
        """Downvote object. If there already is a vote, replace it.

        :returns: The json response from the server.

        """
        return self.vote(direction=-1)

    def upvote(self):
        """Upvote object. If there already is a vote, replace it.

        :returns: The json response from the server.

        """
        return self.vote(direction=1)

    @restrict_access(scope='vote')
    def vote(self, direction=0):
        """Vote for the given item in the direction specified.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['vote']
        data = {'id': self.fullname,
                'dir': six.text_type(direction)}
        if self.reddit_session.user:
            # pylint: disable-msg=W0212
            urls = [urljoin(self.reddit_session.user._url, 'disliked'),
                    urljoin(self.reddit_session.user._url, 'liked')]
            # pylint: enable-msg=W0212
            self.reddit_session.evict(urls)
        return self.reddit_session.request_json(url, data=data)


class Comment(Editable, Inboxable, Moderatable, Reportable, Voteable):

    """A class that represents a reddit comments."""

    def __init__(self, reddit_session, json_dict):
        super(Comment, self).__init__(reddit_session, json_dict,
                                      underscore_names=['replies'])
        if self._replies:
            self._replies = self._replies['data']['children']
        elif self._replies == '':  # Comment tree was built and there are none
            self._replies = []
        else:
            self._replies = None
        self._submission = None

    @limit_chars
    def __unicode__(self):
        return getattr(self, 'body', '[Unloaded Comment]')

    def _update_submission(self, submission):
        """Submission isn't set on __init__ thus we need to update it."""
        # pylint: disable-msg=W0212
        submission._comments_by_id[self.name] = self
        # pylint: enable-msg=W0212
        self._submission = submission
        if self._replies:
            for reply in self._replies:
                # pylint: disable-msg=W0212
                reply._update_submission(submission)
                # pylint: enable-msg=W0212

    @property
    def is_root(self):
        """Return True when the comment is a top level comment."""
        return (self.parent_id is None or
                self.parent_id == self.submission.fullname)

    @property
    def permalink(self):
        """Return a permalink to the comment."""
        return urljoin(self.submission.permalink, self.id)

    @property
    def replies(self):
        """Return a list of the comment replies to this comment."""
        if self._replies is None:
            response = self.reddit_session.request_json(self.permalink)
            # pylint: disable-msg=W0212
            self._replies = response[1]['data']['children'][0]._replies
            # pylint: enable-msg=W0212
        return self._replies

    @property
    def score(self):
        """Return the comment's score."""
        return self.ups - self.downs

    @property
    def submission(self):
        """Return the submission object this comment belongs to."""
        if not self._submission:  # Comment not from submission
            if hasattr(self, 'link_id'):  # from user comments page
                sid = self.link_id.split('_')[1]
            else:  # from user inbox
                sid = self.context.split('/')[4]
            self._submission = self.reddit_session.get_submission(None, sid)
        return self._submission


class Message(Inboxable):

    """A class for reddit messages (orangereds)."""

    def __init__(self, reddit_session, json_dict):
        super(Message, self).__init__(reddit_session, json_dict)
        if self.replies:
            self.replies = self.replies['data']['children']
        else:
            self.replies = []

    @limit_chars
    def __unicode__(self):
        return 'From: %s\nSubject: %s\n\n%s' % (self.author, self.subject,
                                                self.body)


class MoreComments(RedditContentObject):

    """A class indicating there are more comments."""

    def __init__(self, reddit_session, json_dict):
        super(MoreComments, self).__init__(reddit_session, json_dict)
        self.submission = None
        self._comments = None

    def __lt__(self, other):
        # To work with heapq a "smaller" item is the one with the most comments
        # We are intentionally making the biggest element the smallest element
        # to turn the min-heap implementation in heapq into a max-heap
        # implementation for Submission.replace_more_comments()
        return self.count > other.count

    def __unicode__(self):
        return '[More Comments: %d]' % self.count

    def _update_submission(self, submission):
        self.submission = submission

    def comments(self, update=True):
        """Fetch and return the comments for a single MoreComments object."""
        if not self._comments:
            # pylint: disable-msg=W0212
            children = [x for x in self.children if 't1_%s' % x
                        not in self.submission._comments_by_id]
            # pylint: enable-msg=W0212
            if not children:
                return None
            data = {'children': ','.join(children),
                    'link_id': self.submission.fullname,
                    'r': str(self.submission.subreddit)}
            # pylint: disable-msg=W0212
            if self.submission._comment_sort:
                data['where'] = self.submission._comment_sort
            # pylint: enable-msg=W0212
            url = self.reddit_session.config['morechildren']
            response = self.reddit_session.request_json(url, data=data)
            self._comments = response['data']['things']
            if update:
                for comment in self._comments:
                    # pylint: disable-msg=W0212
                    comment._update_submission(self.submission)
                    # pylint: enable-msg=W0212
        return self._comments


class Redditor(Messageable, Refreshable):

    """A class representing the users of reddit."""

    get_overview = _get_section('')
    get_comments = _get_section('comments')
    get_submitted = _get_section('submitted')

    def __init__(self, reddit_session, user_name=None, json_dict=None,
                 fetch=True):
        info_url = reddit_session.config['user_about'] % user_name
        super(Redditor, self).__init__(reddit_session, json_dict,
                                       fetch, info_url)
        self.name = user_name
        self._url = reddit_session.config['user'] % user_name
        self._mod_subs = None

    def __cmp__(self, other):
        """Compare two redditors based on the lowercase of their name.

        :returns: negative, 0, or positive depending on the comparision.

        """
        return cmp(self.name.lower(), other.name.lower())

    def __repr__(self):
        return 'Redditor(user_name=\'{0}\')'.format(self.name)

    def __unicode__(self):
        return self.name

    def friend(self):
        """Friend the user.

        :returns: The json response from the server.

        """
        self.reddit_session.evict(self.reddit_session.config['friends'])
        return _modify_relationship('friend')(self.reddit_session.user, self)

    def mark_as_read(self, messages, unread=False):
        """Mark message(s) as read or unread.

        :returns: The json response from the server.

        """
        ids = []
        if isinstance(messages, Inboxable):
            ids.append(messages.fullname)
        elif hasattr(messages, '__iter__'):
            for msg in messages:
                if not isinstance(msg, Inboxable):
                    raise ClientException('Invalid message type: %s'
                                          % type(msg))
                ids.append(msg.fullname)
        else:
            raise ClientException('Invalid message type: %s' % type(messages))
        # pylint: disable-msg=W0212
        retval = self.reddit_session._mark_as_read(ids, unread=unread)
        # pylint: enable-msg=W0212
        return retval

    def unfriend(self):
        """Unfriend the user.

        :returns: The json response from the server.

        """
        self.reddit_session.evict(self.reddit_session.config['friends'])
        return _modify_relationship('friend', unlink=True)(
            self.reddit_session.user, self)


class LoggedInRedditor(Redditor):

    """A class representing a currently logged in Redditor."""

    get_disliked = _get_section('disliked')
    get_hidden = _get_section('hidden')
    get_liked = _get_section('liked')
    get_saved = _get_section('saved')

    def get_blocked(self):
        """Return a UserList of Redditors with whom the user has blocked."""
        url = self.reddit_session.config['friends']
        return self.reddit_session.request_json(url)[1]

    def get_cached_moderated_reddits(self):
        """Return a cached dictionary of the user's moderated reddits.

        This list is used internally. Consider using the `get_my_moderation`
        function instead.

        """
        if self._mod_subs is None:
            self._mod_subs = {'mod': self.reddit_session.get_subreddit('mod')}
            for sub in self.reddit_session.get_my_moderation(limit=None):
                self._mod_subs[six.text_type(sub).lower()] = sub
        return self._mod_subs

    def get_friends(self):
        """Return a UserList of Redditors with whom the user has friended."""
        url = self.reddit_session.config['friends']
        return self.reddit_session.request_json(url)[0]


class ModAction(RedditContentObject):

    """A moderator action."""

    def __init__(self, reddit_session, json_dict=None, fetch=False):
        super(ModAction, self).__init__(reddit_session, json_dict, fetch)

    def __unicode__(self):
        return 'Action: {0}'.format(self.action)


class Submission(Editable, Hideable, Moderatable, Refreshable, Reportable,
                 Saveable, Voteable):

    """A class for submissions to reddit."""

    @staticmethod
    def _extract_more_comments(tree):
        """Return a list of MoreComments objects removed from tree."""
        more_comments = []
        queue = [(None, x) for x in tree]
        while len(queue) > 0:
            parent, comm = queue.pop(0)
            if isinstance(comm, MoreComments):
                heappush(more_comments, comm)
                if parent:  # Remove from parent listing
                    parent.replies.remove(comm)
                elif parent is None:  # Remove from tree root
                    tree.remove(comm)
            else:
                for item in comm.replies:
                    queue.append((comm, item))
        return more_comments

    @staticmethod
    def from_id(reddit_session, subreddit_id):
        """Return an edit-only submission object based on the id."""
        pseudo_data = {'id': subreddit_id,
                       'permalink': '/comments/{0}'.format(subreddit_id)}
        return Submission(reddit_session, pseudo_data)

    @staticmethod
    @restrict_access(scope='read')
    def from_url(reddit_session, url, comment_limit=0, comment_sort=None,
                 comments_only=False):
        """Request the url and return a Submission object.

        :param reddit_session: The session to make the request with.
        :param url: The url to build the Submission object from.
        :param comment_limit: The desired number of comments to fetch. If <= 0
            fetch the default number for the session's user. If None, fetch the
            maximum possible.
        :param comment_sort: The sort order for retrieved comments. When None
            use the default for the session's user.
        :param comments_only: Return only the list of comments.

        """
        params = {}
        if comment_limit is None:  # Fetch MAX
            params['limit'] = 2048  # Just use a big number
        elif comment_limit > 0:  # Use value
            params['limit'] = comment_limit
        if comment_sort:
            params['sort'] = comment_sort

        s_info, c_info = reddit_session.request_json(url, params=params)
        if comments_only:
            return c_info['data']['children']
        submission = s_info['data']['children'][0]
        submission.comments = c_info['data']['children']
        submission._comment_sort = comment_sort  # pylint: disable-msg=W0212
        return submission

    def __init__(self, reddit_session, json_dict):
        super(Submission, self).__init__(reddit_session, json_dict)
        self.permalink = urljoin(reddit_session.config['reddit_url'],
                                 self.permalink)
        self._comment_sort = None
        self._comments_by_id = {}
        self._comments = None
        self._orphaned = {}
        self._replaced_more = False

    @limit_chars
    def __unicode__(self):
        title = self.title.replace('\r\n', ' ')
        return six.text_type('{0} :: {1}').format(self.score, title)

    def _insert_comment(self, comment):
        if comment.name in self._comments_by_id:  # Skip existing comments
            return

        comment._update_submission(self)  # pylint: disable-msg=W0212

        if comment.name in self._orphaned:  # Reunite children with parent
            comment.replies.extend(self._orphaned[comment.name])
            del self._orphaned[comment.name]

        if comment.is_root:
            self._comments.append(comment)
        elif comment.parent_id in self._comments_by_id:
            self._comments_by_id[comment.parent_id].replies.append(comment)
        else:  # Orphan
            if comment.parent_id in self._orphaned:
                self._orphaned[comment.parent_id].append(comment)
            else:
                self._orphaned[comment.parent_id] = [comment]

    def _update_comments(self, comments):
        self._comments = comments
        for comment in self._comments:
            comment._update_submission(self)  # pylint: disable-msg=W0212

    def add_comment(self, text):
        """Comment on the submission using the specified text.

        :returns: A Comment object for the newly created comment.

        """
        # pylint: disable-msg=W0212
        response = self.reddit_session._add_comment(self.fullname, text)
        # pylint: enable-msg=W0212
        self.reddit_session.evict(self.permalink)
        return response

    @property
    def comments(self):  # pylint: disable-msg=E0202
        """Return forest of comments, with top-level comments as tree roots.

        May contain instances of MoreComment objects. To easily replace these
        objects with Comment objects, use the replace_more_comments method then
        fetch this attribute. Use comment replies to walk down the tree. To get
        an unnested, flat list of comments from this attribute use
        helpers.flatten_tree.

        """
        if self._comments is None:
            self.comments = Submission.from_url(self.reddit_session,
                                                self.permalink,
                                                comments_only=True)
        return self._comments

    @comments.setter  # NOQA
    def comments(self, new_comments):  # pylint: disable-msg=E0202
        """Update the list of comments with the provided nested list."""
        self._update_comments(new_comments)
        self._orphaned = {}

    def replace_more_comments(self, limit=32, threshold=1):
        """Update the comment tree by replacing instances of MoreComments.

        :param limit: The maximum number of MoreComments objects to
            replace. Each replacement requires 1 API request. Set to None to
            have no limit. Default: 32
        :param threshold: The minimum number of children comments a
            MoreComments object must have in order to be replaced. Default: 1
        :returns: A list of MoreComments objects that were not replaced.

        Note that after making this call, the `comments` attribute of the
        submission will no longer contain any MoreComments objects. Items that
        weren't replaced are still removed from the tree.

        """
        if self._replaced_more:
            return []

        remaining = limit
        more_comments = self._extract_more_comments(self.comments)

        # Fetch largest more_comments until reaching the limit or the threshold
        while more_comments:
            item = heappop(more_comments)
            # Skip after reaching the limit or below threshold
            if remaining is 0 or item.count < threshold:
                break

            # Fetch new comments and decrease remaining if a request was made
            new_comments = item.comments(update=False)
            if new_comments is not None and remaining is not None:
                remaining -= 1
            elif new_comments is None:
                continue

            # Insert into the tree or re-add to the list of more_comments
            for comment in new_comments:
                # pylint: disable-msg=W0212
                if isinstance(comment, MoreComments):
                    comment._update_submission(self)
                    heappush(more_comments, comment)
                else:
                    # Replies needs to be an empty list
                    assert not comment._replies
                    comment._replies = []
                    self._insert_comment(comment)
                # pylint: enable-msg=W0212

        self._replaced_more = True
        return more_comments

    def set_flair(self, *args, **kwargs):
        """Set flair for this submission.

        Convenience function that utilizes :meth:`.ModFlairMixin.set_flair`
        populating both the `subreddit` and `item` parameters.

        :returns: The json response from the server.

        """
        return self.subreddit.set_flair(self, *args, **kwargs)

    @property
    def short_link(self):
        """Return a short link to the submission.

        The short link points to a page on the short_domain that redirects to
        the main. http://redd.it/y3r8u is a short link for reddit.com.

        """
        return urljoin(self.reddit_session.config.short_domain, self.id)


class Subreddit(Messageable, Refreshable):

    """A class for Subreddits."""

    _methods = (('accept_moderator_invite', AR),
                ('add_flair_template', MFMix),
                ('clear_flair_templates', MFMix),
                ('configure_flair', MFMix),
                ('delete_flair', MFMix),
                ('delete_image', MCMix),
                ('edit_wiki_page', AR),
                ('get_banned', MOMix),
                ('get_comments', UR),
                ('get_contributors', MOMix),
                ('get_flair', UR),
                ('get_flair_list', MFMix),
                ('get_moderators', UR),
                ('get_mod_log', MLMix),
                ('get_mod_queue', MOMix),
                ('get_random_submission', UR),
                ('get_reports', MOMix),
                ('get_settings', MCMix),
                ('get_spam', MOMix),
                ('get_stylesheet', MOMix),
                ('get_unmoderated', MOMix),
                ('get_wiki_banned', MOMix),
                ('get_wiki_contributors', MOMix),
                ('get_wiki_page', UR),
                ('get_wiki_pages', UR),
                ('search', UR),
                ('set_flair', MFMix),
                ('set_flair_csv', MFMix),
                ('set_settings', MCMix),
                ('set_stylesheet', MCMix),
                ('submit', SubmitMixin),
                ('subscribe', SubscribeMixin),
                ('unsubscribe', SubscribeMixin),
                ('update_settings', MCMix),
                ('upload_image', MCMix))

    # Subreddit banned
    add_ban = _modify_relationship('banned', is_sub=True)
    ban = _modify_relationship('banned', is_sub=True, deprecated='add_ban')
    unban = _modify_relationship('banned', unlink=True, is_sub=True,
                                 deprecated='remove_ban')
    remove_ban = _modify_relationship('banned', unlink=True, is_sub=True)
    # Subreddit contributors
    add_contributor = _modify_relationship('contributor', is_sub=True)
    make_contributor = _modify_relationship('contributor', is_sub=True,
                                            deprecated='add_contributor')
    remove_contributor = _modify_relationship('contributor', unlink=True,
                                              is_sub=True)
    # Subreddit moderators
    add_moderator = _modify_relationship('moderator', is_sub=True)
    make_moderator = _modify_relationship('moderator', is_sub=True,
                                          deprecated='add_moderator')
    remove_moderator = _modify_relationship('moderator', unlink=True,
                                            is_sub=True)
    # Subreddit wiki banned
    add_wiki_ban = _modify_relationship('wikibanned', is_sub=True)
    remove_wiki_ban = _modify_relationship('wikibanned', unlink=True,
                                           is_sub=True)
    # Subreddit wiki contributors
    add_wiki_contributor = _modify_relationship('wikicontributor', is_sub=True)
    remove_wiki_contributor = _modify_relationship('wikicontributor',
                                                   unlink=True, is_sub=True)

    # Generic listing selectors
    get_controversial = _get_sorter('controversial')
    get_hot = _get_sorter('')
    get_new = _get_sorter('new')
    get_top = _get_sorter('top')

    # Explicit listing selectors
    get_controversial_from_all = _get_sorter('controversial', t='all')
    get_controversial_from_day = _get_sorter('controversial', t='day')
    get_controversial_from_hour = _get_sorter('controversial', t='hour')
    get_controversial_from_month = _get_sorter('controversial', t='month')
    get_controversial_from_week = _get_sorter('controversial', t='week')
    get_controversial_from_year = _get_sorter('controversial', t='year')
    get_new_by_date = _get_sorter('new', deprecated='get_new')
    get_new_by_rising = _get_sorter('rising', deprecated='get_rising')
    get_rising = _get_sorter('rising')
    get_top_from_all = _get_sorter('top', t='all')
    get_top_from_day = _get_sorter('top', t='day')
    get_top_from_hour = _get_sorter('top', t='hour')
    get_top_from_month = _get_sorter('top', t='month')
    get_top_from_week = _get_sorter('top', t='week')
    get_top_from_year = _get_sorter('top', t='year')

    def __cmp__(self, other):
        """Compare two subreddits based on the lowercase of their name.

        :returns: negative, 0, or positive depending on the comparision.

        """
        return cmp(self.display_name.lower(), other.display_name.lower())

    def __init__(self, reddit_session, subreddit_name=None, json_dict=None,
                 fetch=False):
        # Special case for when my_subreddits is called as no name is returned
        # so we have to extract the name from the URL.  The URLs are returned
        # as: /r/reddit_name/
        if not subreddit_name:
            subreddit_name = json_dict['url'].split('/')[2]

        info_url = reddit_session.config['subreddit_about'] % subreddit_name
        super(Subreddit, self).__init__(reddit_session, json_dict, fetch,
                                        info_url)
        self.display_name = subreddit_name
        self._url = reddit_session.config['subreddit'] % subreddit_name
        # '' is the hot listing
        listings = ['new/', '', 'top/', 'controversial/']
        base = (reddit_session.config['subreddit'] % self.display_name)
        self._listing_urls = [base + x + '.json' for x in listings]

    def __unicode__(self):
        return self.display_name

    def clear_all_flair(self):
        """Remove all user flair on this subreddit.

        :returns: The json response from the server when there is flair to
            clear, otherwise returns None.

        """
        csv = [{'user': x['user']} for x in self.get_flair_list(limit=None)]
        if csv:
            return self.set_flair_csv(csv)
        else:
            return


class PRAWListing(RedditContentObject):

    """An abstract class to coerce a listing into RedditContentObjects."""

    CHILD_ATTRIBUTE = None

    def __init__(self, reddit_session, json_dict=None, fetch=False):
        super(PRAWListing, self).__init__(reddit_session, json_dict, fetch)

        if not self.CHILD_ATTRIBUTE:
            raise NotImplementedError('PRAWListing must be extended.')

        child_list = getattr(self, self.CHILD_ATTRIBUTE)
        for i in range(len(child_list)):
            child_list[i] = self._convert(reddit_session, child_list[i])

    def __contains__(self, item):
        return item in getattr(self, self.CHILD_ATTRIBUTE)

    def __delitem__(self, index):
        del getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __getitem__(self, index):
        return getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __iter__(self):
        return getattr(self, self.CHILD_ATTRIBUTE).__iter__()

    def __len__(self):
        return len(getattr(self, self.CHILD_ATTRIBUTE))

    def __setitem__(self, index, item):
        getattr(self, self.CHILD_ATTRIBUTE)[index] = item

    def __unicode__(self):
        return six.text_type(getattr(self, self.CHILD_ATTRIBUTE))


class UserList(PRAWListing):

    """A list of Redditors. Works just like a regular list."""

    CHILD_ATTRIBUTE = 'children'

    @staticmethod
    def _convert(reddit_session, data):
        """Return a Redditor object from the data."""
        retval = Redditor(reddit_session, data['name'], fetch=False)
        retval.id = data['id'].split('_')[1]  # pylint: disable-msg=C0103,W0201
        return retval


class WikiPage(RedditContentObject):

    """An individual WikiPage object."""

    def __init__(self, reddit_session, subreddit=None, page=None,
                 json_dict=None, fetch=True):
        if not subreddit and not page:
            subreddit = json_dict['sr']
            page = json_dict['page']
        info_url = reddit_session.config['wiki_page'] % (
            six.text_type(subreddit), page)
        super(WikiPage, self).__init__(reddit_session, json_dict, fetch,
                                       info_url)
        self.page = page
        self.subreddit = subreddit

    def __unicode__(self):
        return six.text_type('{0}:{1}').format(self.subreddit, self.page)

    def edit(self, *args, **kwargs):
        """Edit the wiki page.

        Convenience function that utilizes
        :meth:`.AuthenticatedReddit.edit_wiki_page` populating both the
        `subreddit` and `page` parameters.

        """
        self.subreddit.edit_wiki_page(self.page, *args, **kwargs)


class WikiPageListing(PRAWListing):

    """A list of WikiPages. Works just like a regular list."""

    CHILD_ATTRIBUTE = '_tmp'

    @staticmethod
    def _convert(reddit_session, data):
        """Return a WikiPage object from the data."""
        # TODO: The _request_url hack shouldn't be necessary
        # pylint: disable-msg=W0212
        subreddit = reddit_session._request_url.rsplit('/', 4)[1]
        # pylint: enable-msg=W0212
        return WikiPage(reddit_session, subreddit, data, fetch=False)


def _add_aliases():
    import inspect
    import sys
    predicate = lambda x: inspect.isclass(x) and hasattr(x, '_methods')
    for _, cls in inspect.getmembers(sys.modules[__name__], predicate):
        for name, mixin in cls._methods:  # pylint: disable-msg=W0212
            setattr(cls, name, alias_function(getattr(mixin, name),
                                              mixin.__name__))
_add_aliases()
