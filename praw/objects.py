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
import warnings
from requests.compat import urljoin
from praw import (AuthenticatedReddit as AR, ModConfigMixin as MCMix,
                  ModFlairMixin as MFMix, ModOnlyMixin as MOMix,
                  PrivateMessagesMixin as PMMix, SubmitMixin, SubscribeMixin,
                  UnauthenticatedReddit as UR)
from praw.decorators import alias_function, limit_chars, restrict_access
from praw.errors import ClientException
from praw.helpers import (_get_section, _get_sorter, _modify_relationship,
                          _request)


REDDITOR_KEYS = ('approved_by', 'author', 'banned_by', 'redditor')


class RedditContentObject(object):

    """Base class that represents actual reddit objects."""

    @classmethod
    def from_api_response(cls, reddit_session, json_dict):
        """Return an instance of the appropriate class from the json_dict."""
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
        response = self.reddit_session.request_json(self._info_url,
                                                    as_objects=False)
        return response['data']

    def _populate(self, json_dict, fetch):
        if json_dict is None:
            if fetch:
                json_dict = self._get_json_dict()
            else:
                json_dict = {}
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
        green checkmark (only visible to other moderators) on the webend and
        sets the approved_by attribute to the logged in user.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['approve']
        data = {'id': self.fullname}
        response = self.reddit_session.request_json(url, data=data)
        urls = [self.reddit_session.config[x] for x in ['modqueue', 'spam']]
        if isinstance(self, Submission):
            urls += self.subreddit._listing_urls  # pylint: disable-msg=W0212
        _request.evict(urls)  # pylint: disable-msg=E1101
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
        will try to remove objects with similair attributes in the future.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['remove']
        data = {'id': self.fullname,
                'spam': 'True' if spam else 'False'}
        response = self.reddit_session.request_json(url, data=data)
        urls = [self.reddit_session.config[x] for x in ['modqueue', 'spam']]
        if isinstance(self, Submission):
            urls += self.subreddit._listing_urls  # pylint: disable-msg=W0212
        _request.evict(urls)  # pylint: disable-msg=E1101
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
        # pylint: disable-msg=E1101
        _request.evict([self.reddit_session.config['user']])
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
        # pylint: disable-msg=E1101
        _request.evict([self.reddit_session.config['user']])
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
        _request.evict(urls)
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
        # pylint: disable-msg=E1101,W0212
        response = self.reddit_session._add_comment(self.fullname, text)
        if isinstance(self, Comment):
            _request.evict([self.reddit_session.config['inbox'],
                            self.submission.permalink])
        elif isinstance(self, Message):
            _request.evict([self.reddit_session.config['inbox'],
                            self.reddit_session.config['sent']])
        return response


class Messageable(RedditContentObject):

    """Interface for RedditContentObjects that can be messaged."""

    _methods = (('send_message', PMMix.send_message),)


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
        # pylint: disable-msg=E1101,W0212
        _request.evict([self.reddit_session.config['user'],
                        urljoin(self.reddit_session.user._url, 'hidden')])
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
        # pylint: disable-msg=E1101
        _request.evict([self.reddit_session.config['saved']])
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
        # pylint: disable-msg=W0212
        urls = [urljoin(self.reddit_session.user._url, 'disliked'),
                urljoin(self.reddit_session.user._url, 'liked')]
        _request.evict(urls)
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
        self._submission = submission
        for reply in self._replies:
            reply._update_submission(submission)

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
            if not children:
                return None
            data = {'children': ','.join(children),
                    'link_id': self.submission.fullname,
                    'r': str(self.submission.subreddit)}
            if self.reddit_session.config.comment_sort:
                data['where'] = self.reddit_session.config.comment_sort
            url = self.reddit_session.config['morechildren']
            response = self.reddit_session.request_json(url, data=data)
            self._comments = response['data']['things']
            if update:
                for comment in self._comments:
                    # pylint: disable-msg=W0212
                    comment._update_submission(self.submission)
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
        return self.reddit_session._mark_as_read(ids, unread=unread)

    def unfriend(self):
        """Unfriend the user.

        :returns: The json response from the server.

        """
        return _modify_relationship('friend', unlink=True)(
            self.reddit_session.user, self)


class LoggedInRedditor(Redditor):

    """A class representing a currently logged in Redditor."""

    get_disliked = _get_section('disliked')
    get_hidden = _get_section('hidden')
    get_liked = _get_section('liked')
    get_saved = _get_section('saved')

    def get_cached_moderated_reddits(self):
        """Return a cached dictionary of the user's moderated reddits.

        This list is used internally. Consider using the `my_moderation`
        function instead.

        """
        if self._mod_subs is None:
            self._mod_subs = {'mod': self.reddit_session.get_subreddit('mod')}
            for sub in self.my_moderation(limit=None):
                self._mod_subs[six.text_type(sub).lower()] = sub
        return self._mod_subs

    @restrict_access(scope='privatemessages')
    def get_inbox(self, limit=0):
        """Return a generator for inbox messages."""
        url = self.reddit_session.config['inbox']
        return self.reddit_session.get_content(url, limit=limit)

    @restrict_access(scope='privatemessages')
    def get_modmail(self, limit=0):
        """Return a generator for moderator messages."""
        url = self.reddit_session.config['moderator']
        return self.reddit_session.get_content(url, limit=limit)

    @restrict_access(scope='privatemessages')
    def get_sent(self, limit=0):
        """Return a generator for sent messages."""
        url = self.reddit_session.config['sent']
        return self.reddit_session.get_content(url, limit=limit)

    @restrict_access(scope='privatemessages')
    def get_unread(self, limit=0):
        """Return a generator for unread messages."""
        url = self.reddit_session.config['unread']
        return self.reddit_session.get_content(url, limit=limit)

    @restrict_access(scope='mysubreddits')
    def my_contributions(self, limit=0):
        """Return the subreddits where the logged in user is a contributor."""
        url = self.reddit_session.config['my_con_reddits']
        return self.reddit_session.get_content(url, limit=limit)

    @restrict_access(scope='mysubreddits')
    def my_moderation(self, limit=0):
        """Return the subreddits where the logged in user is a mod."""
        url = self.reddit_session.config['my_mod_reddits']
        retval = self.reddit_session.get_content(url, limit=limit)
        return retval

    @restrict_access(scope='mysubreddits')
    def my_reddits(self, limit=0):
        """Return the subreddits that the logged in user is subscribed to."""
        url = self.reddit_session.config['my_reddits']
        return self.reddit_session.get_content(url, limit=limit)


class Submission(Editable, Hideable, Moderatable, Refreshable, Reportable,
                 Saveable, Voteable):

    """A class for submissions to reddit."""

    @staticmethod
    def from_url(reddit_session, url, comments_only=False):
        """Request the url and return a Submission object.

        :param reddit_session: The session to make the request with.
        :param url: The url to build the Submission object from.
        :param comments_only: Return only the list of comments.

        """
        params = {}
        comment_limit = reddit_session.config.comment_limit
        comment_sort = reddit_session.config.comment_sort

        if reddit_session.user and reddit_session.user.is_gold:
            class_max = reddit_session.config.gold_comments_max
        else:
            class_max = reddit_session.config.regular_comments_max

        if comment_limit < 0:  # Use max for user class
            comment_limit = class_max
        elif comment_limit == 0:  # Use default
            comment_limit = None
        else:  # Use specified value
            if comment_limit > class_max:
                warnings.warn_explicit('comment_limit %d is too high (max: %d)'
                                       % (comment_limit, class_max),
                                       UserWarning, '', 0)
                comment_limit = class_max

        if comment_limit:
            params['limit'] = comment_limit
        if comment_sort:
            params['sort'] = comment_sort
        s_info, c_info = reddit_session.request_json(url, params=params)
        if comments_only:
            return c_info['data']['children']
        submission = s_info['data']['children'][0]
        submission.comments = c_info['data']['children']
        return submission

    def __init__(self, reddit_session, json_dict):
        super(Submission, self).__init__(reddit_session, json_dict)
        self.permalink = urljoin(reddit_session.config['reddit_url'],
                                 self.permalink)
        self._comments_by_id = {}
        self._all_comments = False
        self._comments = None
        self._comments_flat = None
        self._orphaned = {}

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

    def _replace_more_comments(self):
        """Replace MoreComments objects with the actual comments."""
        queue = [(None, x) for x in self.comments]
        remaining = self.reddit_session.config.more_comments_max
        if remaining < 0:
            remaining = None
        skipped = []

        while len(queue) > 0:
            parent, comm = queue.pop(0)
            if isinstance(comm, MoreComments):
                if parent:
                    parent.replies.remove(comm)
                elif parent is None:
                    self._comments.remove(comm)

                # Skip after reaching the limit
                if remaining is not None and remaining <= 0:
                    skipped.append(comm)
                    continue

                new_comments = comm.comments(update=False)

                # Don't count if no request was made
                if new_comments is None:
                    continue
                elif remaining is not None:
                    remaining -= 1

                for comment in new_comments:
                    if isinstance(comment, MoreComments):
                        # pylint: disable-msg=W0212
                        comment._update_submission(self)
                        queue.insert(0, (0, comment))
                    else:
                        # pylint: disable-msg=W0212
                        assert not comment._replies
                        # Replies needs to be an empty list
                        comment._replies = []
                        self._insert_comment(comment)
            else:
                for item in comm.replies:
                    queue.append((comm, item))

        if skipped:
            warnings.warn_explicit('Skipped %d more comments objects on %r' %
                                   (len(skipped), six.text_type(self)),
                                   UserWarning, '', 0)

    def _update_comments(self, comments):
        self._comments = comments
        for comment in self._comments:
            comment._update_submission(self)  # pylint: disable-msg=W0212

    def add_comment(self, text):
        """Comment on the submission using the specified text.

        :returns: A Comment object for the newly created comment.

        """
        # pylint: disable-msg=E1101, W0212
        response = self.reddit_session._add_comment(self.fullname, text)
        _request.evict([self.permalink])
        return response

    @property
    def all_comments(self):
        """Return forest of all comments with top-level comments as tree roots.

        Use a comment's replies to walk down the tree. To get an unnested,
        flat list if comments use all_comments_flat. Multiple API
        requests may be needed to get all comments.

        """
        if not self._all_comments:
            self._replace_more_comments()
            self._all_comments = True
            self._comments_flat = None
        return self._comments

    @property
    def all_comments_flat(self):
        """Return all comments in an unnested, flat list.

        Multiple API requests may be needed to get all comments.

        """
        if not self._all_comments:
            self.all_comments  # pylint: disable-msg=W0104
        return self.comments_flat

    @property
    def comments(self):  # pylint: disable-msg=E0202
        """Return forest of comments, with top-level comments as tree roots.

        May contain instances of MoreComment objects. To easily replace
        these objects with Comment objects, use the all_comments property
        instead. Use comment's replies to walk down the tree. To get
        an unnested, flat list of comments use comments_flat.

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
        self._all_comments = False
        self._comments_flat = None
        self._orphaned = {}

    @property
    def comments_flat(self):
        """Return comments as an unnested, flat list.

        Note that there may be instances of MoreComment objects. To
        easily remove these objects, use the all_comments_flat property
        instead.

        """
        if not self._comments_flat:
            stack = self.comments[:]
            self._comments_flat = []
            while len(stack) > 0:
                comment = stack.pop(0)
                assert(comment not in self._comments_flat)
                if isinstance(comment, Comment):
                    stack[0:0] = comment.replies
                self._comments_flat.append(comment)
        return self._comments_flat

    def set_flair(self, *args, **kwargs):
        """Set flair for this submission.

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

    _methods = (('accept_moderator_invite', AR.accept_moderator_invite),
                ('add_flair_template', MFMix.add_flair_template),
                ('clear_flair_templates', MFMix.clear_flair_templates),
                ('configure_flair', MFMix.configure_flair),
                ('flair_list', MFMix.flair_list),
                ('get_banned', MOMix.get_banned),
                ('get_contributors', MOMix.get_contributors),
                ('get_flair', UR.get_flair),
                ('get_moderators', MOMix.get_moderators),
                ('get_modqueue', MOMix.get_modqueue),
                ('get_reports', MOMix.get_reports),
                ('get_settings', MCMix.get_settings),
                ('get_spam', MOMix.get_spam),
                ('get_stylesheet', MOMix.get_stylesheet),
                ('set_flair', MFMix.set_flair),
                ('set_flair_csv', MFMix.set_flair_csv),
                ('set_settings', MCMix.set_settings),
                ('set_stylesheet', MCMix.set_stylesheet),
                ('submit', SubmitMixin.submit),
                ('subscribe', SubscribeMixin.subscribe),
                ('unsubscribe', SubscribeMixin.unsubscribe),
                ('update_settings', MCMix.update_settings),
                ('upload_image', MCMix.upload_image))

    ban = _modify_relationship('banned', is_sub=True)
    unban = _modify_relationship('banned', unlink=True, is_sub=True)
    make_contributor = _modify_relationship('contributor', is_sub=True)
    remove_contributor = _modify_relationship('contributor', unlink=True,
                                              is_sub=True)
    make_moderator = _modify_relationship('moderator', is_sub=True)
    remove_moderator = _modify_relationship('moderator', unlink=True,
                                            is_sub=True)

    # Generic listing selectors
    get_comments = _get_section('comments')
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
    get_new_by_date = _get_sorter('new', sort='new')
    get_new_by_rising = _get_sorter('new', sort='rising')
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
        # Special case for when my_reddits is called as no name is returned so
        # we have to extract the name from the URL.  The URLs are returned as:
        # /r/reddit_name/
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
        csv = [{'user': x['user']} for x in self.flair_list()]
        if csv:
            return self.set_flair_csv(csv)
        else:
            return

    def search(self, query, *args, **kwargs):
        """Return submissions that match the search query from this subreddit.

        See http://www.reddit.com/help/search for more information on how to
        build a search query.

        """
        return self.reddit_session.search(query, self, *args, **kwargs)


class UserList(RedditContentObject):

    """A list of Redditors. Works just like a regular list."""

    def __init__(self, reddit_session, json_dict=None, fetch=False):
        super(UserList, self).__init__(reddit_session, json_dict, fetch)

        # HACK: Convert children to Redditor instances
        for i in range(len(self.children)):
            tmp = self.children[i]
            redditor = Redditor(reddit_session, tmp['name'], fetch=False)
            redditor.id = tmp['id'].split('_')[1]  # pylint: disable-msg=C0103
            self.children[i] = redditor

    def __contains__(self, item):
        return item in self.children

    def __getitem__(self, index):
        return self.children[index]

    def __iter__(self):
        return self.children.__iter__()

    def __len__(self):
        return len(self.children)


def _add_aliases():
    import inspect
    import sys
    predicate = lambda x: inspect.isclass(x) and hasattr(x, '_methods')
    for _, cls in inspect.getmembers(sys.modules[__name__], predicate):
        for name, method in cls._methods:  # pylint: disable-msg=W0212
            setattr(cls, name, alias_function(method))
_add_aliases()
