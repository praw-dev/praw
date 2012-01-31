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
from reddit.errors import ClientException
from reddit.helpers import _get_section, _get_sorter, _modify_relationship
from reddit.helpers import _request
from reddit.util import limit_chars


class RedditContentObject(object):
    """Base class that  represents actual reddit objects."""
    def __init__(self, reddit_session, json_dict=None, fetch=True,
                 info_url=None, underscore_names=None):
        """
        Create a new object from the dict of attributes returned by the API.

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

    def _populate(self, json_dict, fetch):
        if json_dict is None:
            if fetch:
                json_dict = self._get_json_dict()
            else:
                json_dict = {}
        for name, value in json_dict.iteritems():
            if self._underscore_names and name in self._underscore_names:
                name = '_' + name
            setattr(self, name, value)
        return bool(json_dict) or fetch

    def __getattr__(self, attr):
        if not self._populated:
            self._populated = self._populate(None, True)
            return getattr(self, attr)
        raise AttributeError('\'%s\' has no attribute \'%s\'' % (type(self),
                                                                 attr))

    def __setattr__(self, name, value):
        if value and name == 'subreddit':
            value = Subreddit(self.reddit_session, value, fetch=False)
        elif value and name in ['redditor', 'author'] and value != '[deleted]':
            value = Redditor(self.reddit_session, value, fetch=False)
        object.__setattr__(self, name, value)

    def __eq__(self, other):
        return (isinstance(other, RedditContentObject) and
                self.content_id == other.content_id)

    def _get_json_dict(self):
        response = self.reddit_session.request_json(self._info_url,
                                                    as_objects=False)
        return response['data']

    @classmethod
    def from_api_response(cls, reddit_session, json_dict):
        return cls(reddit_session, json_dict=json_dict)

    @property
    def content_id(self):
        """
        Get the content id for this object. Just prepends the appropriate
        content type to this object's id.
        """
        by_object = self.reddit_session.config.by_object
        return '%s_%s' % (by_object[self.__class__], self.id)


class Approvable(RedditContentObject):
    """Interface for Reddit content objects that can be approved."""
    @require_login
    def approve(self):
        url = self.reddit_session.config['approve']
        params = {'id': self.content_id,
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        response = self.reddit_session.request_json(url, params)
        urls = [self.reddit_session.config[x] for x in ['modqueue', 'spam']]
        _request.is_stale(urls)  # pylint: disable-msg=E1101
        return response

    @require_login
    def remove(self):
        url = self.reddit_session.config['remove']
        params = {'id': self.content_id,
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        response = self.reddit_session.request_json(url, params)
        urls = [self.reddit_session.config[x] for x in ['modqueue', 'spam']]
        _request.is_stale(urls)  # pylint: disable-msg=E1101
        return response


class Deletable(RedditContentObject):
    """Interface for Reddit content objects that can be deleted."""
    def delete(self):
        url = self.reddit_session.config['del']
        params = {'id': self.content_id,
                  'executed': 'deleted',
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        response = self.reddit_session.request_json(url, params)
        # pylint: disable-msg=E1101
        _request.is_stale([self.reddit_session.config['user']])
        return response


class Distinguishable(RedditContentObject):
    """Interface for Reddit content objects that can be distinguished.

    Presently there is no way to verify a distinguished post.
    """
    @require_login
    def distinguish(self):
        url = self.reddit_session.config['distinguish']
        params = {'id': self.content_id,
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        return self.reddit_session.request_json(url, params)

    @require_login
    def undistinguish(self):
        url = self.reddit_session.config['undistinguish']
        params = {'id': self.content_id,
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        return self.reddit_session.request_json(url, params)


class Inboxable(RedditContentObject):
    """Interface for RedditContentObjects that appear in the Inbox."""
    @require_login
    def reply(self, text):
        """Reply to the comment with the specified text."""
        # pylint: disable-msg=E1101,W0212
        response = self.reddit_session._add_comment(self.content_id, text)
        if isinstance(self, Comment):
            _request.is_stale([self.reddit_session.config['inbox'],
                               self.submission.permalink])
        elif isinstance(self, Message):
            _request.is_stale([self.reddit_session.config['inbox'],
                               self.reddit_session.config['sent']])
        return response

    @require_login
    def mark_as_read(self):
        """ Marks the comment as read."""
        return self.reddit_session.user.mark_as_read(self)

    @require_login
    def mark_as_unread(self):
        """ Marks the comment as unread."""
        return self.reddit_session.user.mark_as_read(self, unread=True)


class Reportable(RedditContentObject):
    """Interface for Reddit content objects that can be reported."""
    @require_login
    def report(self):
        url = self.reddit_session.config['report']
        params = {'id': self.content_id,
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        response = self.reddit_session.request_json(url, params)
        # pylint: disable-msg=E1101
        _request.is_stale([self.reddit_session.config['user']])
        return response


class Saveable(RedditContentObject):
    """Interface for Reddit content objects that can be saved."""
    @require_login
    def save(self, unsave=False):
        """If logged in, save the content."""
        url = self.reddit_session.config['unsave' if unsave else 'save']
        params = {'id': self.content_id,
                  'executed': 'unsaved' if unsave else 'saved',
                  'uh': self.reddit_session.modhash,
                  'api_type': 'json'}
        response = self.reddit_session.request_json(url, params)
        # pylint: disable-msg=E1101
        _request.is_stale([self.reddit_session.config['saved']])
        return response

    def unsave(self):
        return self.save(unsave=True)


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


class Comment(Approvable, Reportable, Deletable, Distinguishable, Inboxable,
              Voteable):
    """A class for comments."""
    def __init__(self, reddit_session, json_dict):
        super(Comment, self).__init__(reddit_session, json_dict,
                                      underscore_names=['replies'])
        if self._replies:
            self._replies = self._replies['data']['children']
        elif hasattr(self, 'context'):  # Comment not from submission
            self._replies = None
        else:
            self._replies = []
        self._submission = None

    @limit_chars()
    def __str__(self):
        return getattr(self, 'body', '[Unloaded Comment]').encode('utf8')

    @property
    def is_root(self):
        return self.parent_id is None

    @property
    def permalink(self):
        return urljoin(self.submission.permalink, self.id)

    @property
    def replies(self):
        if self._replies is None:
            response = self.reddit_session.request_json(self.permalink)
            # pylint: disable-msg=W0212
            self._replies = response[1]['data']['children'][0]._replies
        return self._replies

    @property
    def submission(self):
        if not self._submission:  # Comment not from submission
            if hasattr(self, 'link_id'):  # from user comments page
                sid = self.link_id.split('_')[1]
            else:  # from user inbox
                sid = self.context.split('/')[4]
            self._submission = self.reddit_session.get_submission(None, sid)
        return self._submission

    def _update_submission(self, submission):
        """Submission isn't set on __init__ thus we need to update it."""
        # pylint: disable-msg=W0212
        submission._comments_by_id[self.name] = self
        self._submission = submission
        for reply in self._replies:
            reply._update_submission(submission)


class Message(Inboxable):
    """A class for reddit messages (orangereds)."""
    def __init__(self, reddit_session, json_dict):
        super(Message, self).__init__(reddit_session, json_dict)

    @limit_chars()
    def __str__(self):
        return 'From: %s\nSubject: %s\n\n%s' % (self.author, self.subject,
                                                self.body)


class MoreComments(RedditContentObject):
    """A class indicating there are more comments."""
    def __init__(self, reddit_session, json_dict):
        super(MoreComments, self).__init__(reddit_session, json_dict)
        self.submission = None
        self._comments = None

    def _update_submission(self, submission):
        self.submission = submission

    def __str__(self):
        return '[More Comments]'.encode('utf8')

    def comments(self):
        """Use this to fetch the comments for a single MoreComments object."""
        if not self._comments:
            params = {'children': ','.join(self.children),
                      'link_id': self.submission.content_id,
                      'r': str(self.submission.subreddit),
                      'api_type': 'json'}
            url = self.reddit_session.config['morechildren']
            response = self.reddit_session.request_json(url, params)
            self._comments = response['data']['things']
            for comment in self._comments:
                # pylint: disable-msg=W0212
                comment._update_submission(self.submission)
        return self._comments


class Redditor(RedditContentObject):
    """A class for Redditor methods."""
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
        return _modify_relationship('friend')(self.reddit_session.user, self)

    @require_login
    def mark_as_read(self, messages, unread=False):
        """Mark message(s) as read or unread."""
        ids = []
        if isinstance(messages, Inboxable):
            ids.append(messages.content_id)
        elif hasattr(messages, '__iter__'):
            for msg in messages:
                if not isinstance(msg, Inboxable):
                    raise ClientException('Invalid message type: %s'
                                          % type(msg))
                ids.append(msg.content_id)
        else:
            raise ClientException('Invalid message type: %s' % type(messages))
        # pylint: disable-msg=W0212
        return self.reddit_session._mark_as_read(ids, unread=unread)

    @require_login
    def unfriend(self):
        """Unfriend the user."""
        return _modify_relationship('friend', unlink=True)(
            self.reddit_session.user, self)


class LoggedInRedditor(Redditor):
    """A class for a currently logged in redditor"""
    @require_login
    def my_reddits(self, limit=0):
        """Return all of the current user's subscribed subreddits."""
        url = self.reddit_session.config['my_reddits']
        return self.reddit_session.get_content(url, limit=limit)

    @require_login
    def my_moderation(self, limit=0):
        """Return all of the current user's subreddits that they moderate."""
        url = self.reddit_session.config['my_mod_reddits']
        return self.reddit_session.get_content(url, limit=limit)

    @require_login
    def get_inbox(self, limit=0):
        """Return a generator for inbox messages."""
        url = self.reddit_session.config['inbox']
        return self.reddit_session.get_content(url, limit=limit)

    @require_login
    def get_modmail(self, limit=0):
        """Return a generator for moderator messages."""
        url = self.reddit_session.config['moderator']
        return self.reddit_session.get_content(url, limit=limit)

    @require_login
    def get_sent(self, limit=0):
        """Return a generator for sent messages."""
        url = self.reddit_session.config['sent']
        return self.reddit_session.get_content(url, limit=limit)

    @require_login
    def get_unread(self, limit=0):
        """Return a generator for unread messages."""
        url = self.reddit_session.config['unread']
        return self.reddit_session.get_content(url, limit=limit)


class Submission(Approvable, Deletable, Distinguishable, Reportable, Saveable,
                 Voteable):
    """A class for submissions to Reddit."""
    def __init__(self, reddit_session, json_dict):
        super(Submission, self).__init__(reddit_session, json_dict)
        self.permalink = urljoin(reddit_session.config['reddit_url'],
                                 self.permalink)
        self._comments_by_id = {}
        self._all_comments = False
        self._comments = None
        self._comments_flat = None

    def __str__(self):
        title = self.title.replace('\r\n', ' ').encode('utf-8')
        return '{0} :: {1}'.format(self.score, title)

    def _extract_morecomments(self):
        more_comments = []
        queue = [(None, x) for x in self.comments]
        while len(queue) > 0:
            parent, comm = queue.pop(0)
            if isinstance(comm, MoreComments):
                more_comments.append(comm)
                if parent:
                    parent.replies.remove(comm)
                else:
                    self._comments.remove(comm)
            else:
                queue[0:0] = [(comm, x) for x in comm.replies]
        return more_comments

    def _fetch_morecomments(self, more_comments):
        """Fetch each more_comments object one at a time."""
        if len(more_comments) > 10:
            raise ClientException(('Fetching more than 10 MoreComment objects '
                                   'is not supported at this time.'))

        results = []
        url = self.reddit_session.config['morechildren']
        for comment_ids in [x.children for x in more_comments]:
            ids = ','.join(comment_ids)
            params = {'children': ids,
                      'link_id': self.content_id,
                      'r': str(self.subreddit),
                      'api_type': 'json'}
            response = self.reddit_session.request_json(url, params)
            results.extend(response['data']['things'])

        for comment in results:
            comment._update_submission(self)  # pylint: disable-msg=W0212
            if isinstance(comment, MoreComments):
                self._comments.append(comment)  # Handle in the next iteration
            elif comment.parent_id == self.content_id:
                assert len(comment.replies) == 0
                assert comment not in self._comments
                self._comments.append(comment)
            else:
                assert len(comment.replies) == 0
                tmp = self._comments_by_id[comment.parent_id].replies
                assert comment not in tmp
                tmp.append(comment)

    def _update_comments(self, comments):
        self._comments = comments
        for comment in self._comments:
            comment._update_submission(self)  # pylint: disable-msg=W0212

    @property
    def comments(self):
        if self._comments == None:
            _, comment_info = self.reddit_session.request_json(self.permalink)
            self._update_comments(comment_info['data']['children'])
        return self._comments

    @comments.setter  # pylint: disable-msg=E1101
    def comments(self, new_comments):  # pylint: disable-msg=E0102
        self._update_comments(new_comments)
        self._all_comments = False
        self._comments_flat = None

    @property
    def all_comments(self):
        """Replace instances of MoreComments with the actual comments tree."""
        if not self._all_comments:
            more_comments = self._extract_morecomments()
            while more_comments:
                self._fetch_morecomments(more_comments)
                more_comments = self._extract_morecomments()
            self._all_comments = True
            self._comments_flat = None
        return self._comments

    @property
    def all_comments_flat(self):
        if not self.all_comments:
            self.all_comments  # pylint: disable-msg=W0104
        return self.comments_flat

    @property
    def comments_flat(self):
        if not self._comments_flat:
            self._comments_flat = []
            stack = self.comments[:]
            while len(stack) > 0:
                comment = stack.pop(0)
                assert(comment not in self._comments_flat)
                if isinstance(comment, Comment):
                    stack[0:0] = comment.replies
                self._comments_flat.append(comment)
        return self._comments_flat

    def add_comment(self, text):
        """If logged in, comment on the submission using the specified text."""
        # pylint: disable-msg=E1101, W0212
        response = self.reddit_session._add_comment(self.content_id, text)
        _request.is_stale([self.permalink])
        return response


class Subreddit(RedditContentObject):
    """A class for Subreddits."""

    ban = _modify_relationship('banned', is_sub=True)
    unban = _modify_relationship('banned', unlink=True, is_sub=True)
    make_contributor = _modify_relationship('contributor', is_sub=True)
    remove_contributor = _modify_relationship('contributor', unlink=True,
                                              is_sub=True)
    make_moderator = _modify_relationship('moderator', is_sub=True)
    remove_moderator = _modify_relationship('moderator', unlink=True,
                                            is_sub=True)

    get_hot = _get_sorter('')
    get_controversial = _get_sorter('controversial', t='day')
    get_new = _get_sorter('new', sort='rising')
    get_top = _get_sorter('top', t='day')
    get_new_by_date = _get_sorter('new', sort='new')
    get_comments = _get_section('comments')

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

    @limit_chars()
    def __str__(self):
        """Display the subreddit name."""
        return self.display_name.encode('utf8')

    def add_flair_template(self, *args, **kwargs):
        """Adds a flair template to the subreddit."""
        return self.reddit_session.add_flair_template(self, *args, **kwargs)

    def clear_all_flair(self):
        """Helper method to remove all currently set flair."""
        csv = [{'user': x['user']} for x in self.flair_list()]
        if csv:
            return self.set_flair_csv(csv)
        else:
            return

    def update_community_settings(self, title, description='', language='en',
                                  subreddit_type='public',
                                  content_options='any', over_18=False,
                                  default_set=True, show_media=False,
                                  domain='', header_hover_text=''):
        params = {'r': str(self),
                  'sr': self.content_id,
                  'title': title,
                  'description': description,
                  'lang': language,
                  'type': subreddit_type,
                  'link_type': content_options,
                  'header-title': header_hover_text,
                  'over_18': 'on' if over_18 else 'off',
                  'allow_top': 'on' if default_set else 'off',
                  'show_media': 'on' if show_media else 'off',
                  'domain': domain,
                  'uh': self.reddit_session.modhash,
                  'id': '#sr-form',
                  'api_type': 'json'}
        return self.reddit_session.request_json(
                self.reddit_session.config['site_admin'], params)

    def clear_flair_templates(self, *args, **kwargs):
        """Clear flair templates for this subreddit."""
        return self.reddit_session.clear_flair_templates(self, *args, **kwargs)

    def get_banned(self, *args, **kwargs):
        """Get banned users for this subreddit."""
        return self.reddit_session.get_banned(self, *args, **kwargs)

    def get_contributors(self, *args, **kwargs):
        """Get contributors for this subreddit."""
        return self.reddit_session.get_contributors(self, *args, **kwargs)

    def get_moderators(self, *args, **kwargs):
        """Get moderators for this subreddit."""
        return self.reddit_session.get_moderators(self, *args, **kwargs)

    def get_modqueue(self, *args, **kwargs):
        """Get the modqueue on the given subreddit."""
        return self.reddit_session.get_modqueue(self, *args, **kwargs)

    def get_reports(self, *args, **kwargs):
        """Get the reported submissions on the given subreddit."""
        return self.reddit_session.get_reports(self, *args, **kwargs)

    def get_spam(self, *args, **kwargs):
        """Get the spam-filtered items on the given subreddit."""
        return self.reddit_session.get_spam(self, *args, **kwargs)

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

    def subscribe(self):
        """Subscribe to the given subreddit."""
        # pylint: disable-msg=W0212
        return self.reddit_session._subscribe(self.content_id)

    def unsubscribe(self):
        """Unsubscribe from the given subreddit."""
        # pylint: disable-msg=W0212
        return self.reddit_session._subscribe(self.content_id,
                                              unsubscribe=True)


class UserList(RedditContentObject):
    """A class for UserList."""

    def __init__(self, reddit_session, json_dict=None, fetch=False):
        super(UserList, self).__init__(reddit_session, json_dict, fetch)

        # HACK: Convert children to RedditorObjects
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
