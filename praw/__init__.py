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
Python Reddit API Wrapper.

PRAW, an acronym for "Python Reddit API Wrapper", is a python package that
allows for simple access to reddit's API. PRAW aims to be as easy to use as
possible and is designed to follow all of reddit's API rules. You have to give
a useragent, everything else is handled by PRAW so you needn't worry about
violating them.

More information about PRAW can be found at https://github.com/praw-dev/praw
"""

import json
import os
import platform
import requests
import six
import sys
from requests.compat import urljoin
from requests import Request
from update_checker import update_check
from warnings import warn_explicit

from praw import decorators, errors, helpers, objects
from praw.settings import CONFIG

__version__ = '1.1.0rc10'
UA_STRING = '%%s PRAW/%s Python/%s %s' % (__version__,
                                          sys.version.split()[0],
                                          platform.platform(True))

MIN_IMAGE_SIZE = 128
MAX_IMAGE_SIZE = 512000
JPEG_HEADER = '\xff\xd8\xff'
PNG_HEADER = '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'


class Config(object):  # pylint: disable-msg=R0903

    """A class containing the configuration for a reddit site."""

    API_PATHS = {'access_token_url':    'api/v1/access_token/',
                 'approve':             'api/approve/',
                 'authorize':           'api/v1/authorize/',
                 'banned':              'r/%s/about/banned/',
                 'captcha':             'captcha/',
                 'clearflairtemplates': 'api/clearflairtemplates/',
                 'comment':             'api/comment/',
                 'comments':            'comments/',
                 'compose':             'api/compose/',
                 'contributors':        'r/%s/about/contributors/',
                 'controversial':       'controversial/',
                 'del':                 'api/del/',
                 'distinguish':         'api/distinguish/',
                 'edit':                'api/editusertext/',
                 'feedback':            'api/feedback/',
                 'flair':               'api/flair/',
                 'flairconfig':         'api/flairconfig/',
                 'flaircsv':            'api/flaircsv/',
                 'flairlist':           'r/%s/api/flairlist/',
                 'flairtemplate':       'api/flairtemplate/',
                 'friend':              'api/friend/',
                 'help':                'help/',
                 'hide':                'api/hide/',
                 'inbox':               'message/inbox/',
                 'info':                'api/info/',
                 'login':               'api/login/',
                 'me':                  'api/v1/me',
                 'moderator':           'message/moderator/',
                 'moderators':          'r/%s/about/moderators/',
                 'modqueue':            'r/%s/about/modqueue/',
                 'morechildren':        'api/morechildren/',
                 'my_con_reddits':      'reddits/mine/contributor/',
                 'my_mod_reddits':      'reddits/mine/moderator/',
                 'my_reddits':          'reddits/mine/subscriber/',
                 'new':                 'new/',
                 'marknsfw':            'api/marknsfw/',
                 'popular_reddits':     'reddits/popular/',
                 'read_message':        'api/read_message/',
                 'reddit_url':          '/',
                 'register':            'api/register/',
                 'remove':              'api/remove/',
                 'report':              'api/report/',
                 'reports':             'r/%s/about/reports/',
                 'save':                'api/save/',
                 'saved':               'saved/',
                 'search':              'r/%s/search/',
                 'search_reddit_names': 'api/search_reddit_names/',
                 'sent':                'message/sent/',
                 'site_admin':          'api/site_admin/',
                 'spam':                'r/%s/about/spam/',
                 'stylesheet':          'r/%s/about/stylesheet/',
                 'submit':              'api/submit/',
                 'subreddit':           'r/%s/',
                 'subreddit_about':     'r/%s/about/',
                 'subreddit_css':       'api/subreddit_stylesheet/',
                 'subreddit_settings':  'r/%s/about/edit/',
                 'subscribe':           'api/subscribe/',
                 'top':                 'top/',
                 'unfriend':            'api/unfriend/',
                 'unhide':              'api/unhide/',
                 'unmarknsfw':          'api/unmarknsfw/',
                 'unread':              'message/unread/',
                 'unread_message':      'api/unread_message/',
                 'unsave':              'api/unsave/',
                 'upload_image':        'api/upload_sr_img',
                 'user':                'user/%s/',
                 'user_about':          'user/%s/about/',
                 'username_available':  'api/username_available/',
                 'vote':                'api/vote/'}
    SSL_PATHS = ('access_token_url', 'authorize', 'login')

    def __init__(self, site_name):
        obj = dict(CONFIG.items(site_name))
        self._site_url = 'http://' + obj['domain']
        if 'ssl_domain' in obj:
            self._ssl_url = 'https://' + obj['ssl_domain']
        else:
            self._ssl_url = None
        if 'oauth_domain' in obj:
            self._oauth_url = 'https://' + obj['oauth_domain']
        else:
            self._oauth_url = self._ssl_url
        self.api_request_delay = float(obj['api_request_delay'])
        self.by_kind = {obj['comment_kind']:    objects.Comment,
                        obj['message_kind']:    objects.Message,
                        obj['redditor_kind']:   objects.Redditor,
                        obj['submission_kind']: objects.Submission,
                        obj['subreddit_kind']:  objects.Subreddit,
                        'more':                 objects.MoreComments,
                        'UserList':             objects.UserList}
        self.by_object = dict((value, key) for (key, value) in
                              six.iteritems(self.by_kind))
        self.by_object[objects.LoggedInRedditor] = obj['redditor_kind']
        self.cache_timeout = float(obj['cache_timeout'])
        if obj['check_for_updates'] \
                and obj['check_for_updates'].lower() == 'true':
            self.check_for_updates = True
        else:
            self.check_for_updates = False
        self.comment_limit = int(obj['comment_limit'])
        self.comment_sort = obj['comment_sort']
        self.default_content_limit = int(obj['default_content_limit'])
        self.domain = obj['domain']
        self.gold_comments_max = int(obj['gold_comments_max'])
        self.more_comments_max = int(obj['more_comments_max'])
        self.output_chars_limit = int(obj['output_chars_limit'])
        self.log_requests = int(obj['log_requests'])
        self.regular_comments_max = int(obj['regular_comments_max'])
        self.client_id = obj.get('oauth_client_id')
        self.client_secret = obj.get('oauth_client_secret')
        self.redirect_uri = obj.get('oauth_redirect_uri')

        if 'short_domain' in obj:
            self._short_domain = 'http://' + obj['short_domain']
        else:
            self._short_domain = None
        self.timeout = float(obj['timeout'])
        try:
            self.user = obj['user'] if obj['user'] else None
            self.pswd = obj['pswd']
        except KeyError:
            self.user = self.pswd = None
        self.is_reddit = obj['domain'].endswith('reddit.com')

    def __getitem__(self, key):
        """Return the URL for key."""
        if self._ssl_url and key in self.SSL_PATHS:
            return urljoin(self._ssl_url, self.API_PATHS[key])
        return urljoin(self._site_url, self.API_PATHS[key])

    @property
    def short_domain(self):
        """Return the short domain of the reddit.

        Used to generate the shortlink. For reddit.com the short_domain is
        redd.it and generate shortlinks like http://redd.it/y3r8u

        """
        if self._short_domain:
            return self._short_domain
        else:
            raise errors.ClientException('No short domain specified.')


class BaseReddit(object):

    """The base class for a reddit session."""

    RETRY_CODES = [502, 503, 504]
    update_checked = False

    def __init__(self, user_agent, site_name=None, access_token=None,
                 refresh_token=None, disable_update_check=False):
        """Initialize our connection with a reddit server.

        The user_agent is how your application identifies itself. Read the
        official API guidelines for user_agents
        https://github.com/reddit/reddit/wiki/API.  Applications using default
        user_agents such as "Python/urllib" are drastically limited.

        site_name allows you to specify which reddit you want to connect to.
        The installation defaults are reddit.com, if you only need to connect
        to reddit.com then you can safely ignore this. If you want to connect
        to another reddit, set site_name to the name of that reddit. This must
        match with an entry in praw.ini. If site_name is None, then the site
        name will be looked for in the environment variable REDDIT_SITE. If it
        is not found there, the default site name reddit matching reddit.com
        will be used.

        If access_token is given, then all requests will use OAuth 2.0. If
        refresh_token is given, then the refresh_access_token method can be
        used to update the access token.

        disable_update_check allows you to prevent an update check from
        occuring in spite of the check_for_updates setting in praw.ini.

        """
        if not user_agent or not isinstance(user_agent, six.string_types):
            raise TypeError('User agent must be a non-empty string.')

        self.access_token = access_token
        self.refresh_token = refresh_token
        self.config = Config(site_name or os.getenv('REDDIT_SITE') or 'reddit')
        self.http = requests.session()
        self.http.headers['User-Agent'] = UA_STRING % user_agent
        self.modhash = self.user = None

        # Check for updates if permitted and this is the first Reddit instance
        if not disable_update_check and not self.update_checked \
                and self.config.check_for_updates:
            update_check(__name__, __version__)
            self.update_checked = True

    def __str__(self):
        return 'Open Session (%s)' % (self.user or 'Unauthenticated')

    def _request(self, url, params=None, data=None, files=None, timeout=None,
                 raw_response=False, auth=None):
        """Given a page url and a dict of params, open and return the page.

        :param url: the url to grab content from.
        :param params: a dictionary containing the GET data to put in the url
        :param data: a dictionary containing the extra data to submit
        :param files: a dictionary specifying the files to upload
        :param raw_response: return the response object rather than the
            response body
        :param auth: Add the HTTP authentication headers (see requests)
        :returns: either the response body or the response object

        """
        # pylint: disable-msg=W0212
        timeout = self.config.timeout if timeout is None else timeout
        remaining_attempts = 3
        while True:
            try:
                return helpers._request(self, url, params, data, files=files,
                                        auth=auth, raw_response=raw_response,
                                        timeout=timeout)
            except requests.exceptions.HTTPError as error:
                remaining_attempts -= 1
                if (error.response.status_code not in self.RETRY_CODES or
                    remaining_attempts == 0):
                    raise
            except requests.exceptions.RequestException:
                remaining_attempts -= 1
                if remaining_attempts == 0:
                    raise

    def _json_reddit_objecter(self, json_data):
        """Return an appropriate RedditObject from json_data when possible."""
        try:
            object_class = self.config.by_kind[json_data['kind']]
        except KeyError:
            if 'json' in json_data:
                if len(json_data) != 1:
                    warn_explicit('Unknown object type: %s' %
                                  json_data, UserWarning, '', 0)
                return json_data['json']
        else:
            return object_class.from_api_response(self, json_data['data'])
        return json_data

    def get_content(self, url, params=None, limit=0, place_holder=None,
                    root_field='data', thing_field='children',
                    after_field='after'):
        """A generator method to return reddit content from a URL.

        Starts at the initial url, and fetches content using the `after`
        JSON data until `limit` entries have been fetched, or the
        `place_holder` has been reached.

        :param url: the url to start fetching content from
        :param params: dictionary containing extra GET data to put in the url
        :param limit: the maximum number of content entries to fetch. If
            limit <= 0, fetch the default_content_limit for the site. If None,
            then fetch unlimited entries--this would be used in conjunction
            with the place_holder param.
        :param place_holder: if not None, the method will fetch `limit`
            content, stopping if it finds content with `id` equal to
            `place_holder`.
        :param data_field: indicates the field in the json response that holds
            the data. Most objects use 'data', however some (flairlist) don't
            have the 'data' object. Use None for the root object.
        :param thing_field: indicates the field under the data_field which
            contains the list of things. Most objects use 'children'.
        :param after_field: indicates the field which holds the after item
            element
        :type place_holder: a string corresponding to a reddit content id, e.g.
            't3_asdfasdf'
        :returns: a list of reddit content, of type Subreddit, Comment,
            Submission or user flair.

        """
        objects_found = 0

        if params is None:
            params = {}
        if limit is None:
            fetch_all = True
        elif limit <= 0:
            fetch_all = False
            limit = int(self.config.default_content_limit)
        else:
            fetch_all = False

        # While we still need to fetch more content to reach our limit, do so.
        while fetch_all or objects_found < limit:
            page_data = self.request_json(url, params=params)
            if root_field:
                root = page_data[root_field]
            else:
                root = page_data
            for thing in root[thing_field]:
                yield thing
                objects_found += 1
                # Terminate when we've reached the limit, or place holder
                if (objects_found == limit or
                    place_holder and thing.id == place_holder):
                    return
            # Set/update the 'after' parameter for the next iteration
            if after_field in root and root[after_field]:
                params['after'] = root[after_field]
            else:
                return

    @decorators.parse_api_json_response
    def request_json(self, url, params=None, data=None, as_objects=True):
        """Get the JSON processed from a page.

        :param url: the url to grab content from.
        :param params: a dictionary containing the GET data to put in the url
        :param data: a dictionary containing the extra data to submit
        :param as_objects: if true return reddit objects else raw json dict.
        :returns: JSON processed page

        """
        url += '.json'
        response = self._request(url, params, data)
        if as_objects:
            hook = self._json_reddit_objecter
        else:
            hook = None
        data = json.loads(response, object_hook=hook)
        # Update the modhash
        if self.user and 'data' in data and 'modhash' in data['data']:
            self.modhash = data['data']['modhash']
        return data


class SubredditExtension(BaseReddit):

    """Adds methods that operate on Subreddit objects."""

    def __init__(self, *args, **kwargs):
        super(SubredditExtension, self).__init__(*args, **kwargs)

    @decorators.require_login
    def _subscribe(self, sr_id=None, sr_name=None, unsubscribe=False):
        """(Un)subscribe to the given subreddit.

        Provide either the subreddit id (sr_id) or the name (sr_name).

        :returns: The json response from the server.

        """
        if bool(sr_id) == bool(sr_name):
            raise TypeError('One (and only one) of text or url is required!')
        action = 'unsub' if unsubscribe else 'sub'
        data = {'action': action}
        if sr_id:
            data['sr'] = sr_id
        else:
            data['sr_name'] = sr_name

        response = self.request_json(self.config['subscribe'], data=data)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([self.config['my_reddits']])
        return response

    @decorators.require_login
    @decorators.require_moderator
    def add_flair_template(self, subreddit, text='', css_class='',
                           text_editable=False, is_link=False):
        """Add a flair template to the given subreddit.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'text': text,
                'css_class': css_class,
                'text_editable': six.text_type(text_editable),
                'flair_type': 'LINK_FLAIR' if is_link else 'USER_FLAIR'}
        return self.request_json(self.config['flairtemplate'], data=data)

    @decorators.require_login
    @decorators.require_moderator
    def clear_flair_templates(self, subreddit, is_link=False):
        """Clear flair templates for the given subreddit.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'flair_type': 'LINK_FLAIR' if is_link else 'USER_FLAIR'}
        return self.request_json(self.config['clearflairtemplates'], data=data)

    @decorators.require_login
    @decorators.require_moderator
    def configure_flair(self, subreddit, flair_enabled=False,
                        flair_position='right',
                        flair_self_assign=False,
                        link_flair_enabled=False,
                        link_flair_position='left',
                        link_flair_self_assign=False):
        """Configure the flair setting for the given subreddit.

        :returns: The json response from the server.

        """
        flair_enabled = 'on' if flair_enabled else 'off'
        flair_self_assign = 'on' if flair_self_assign else 'off'
        if not link_flair_enabled:
            link_flair_position = ''
        link_flair_self_assign = 'on' if link_flair_self_assign else 'off'
        data = {'r': six.text_type(subreddit),
                'flair_enabled': flair_enabled,
                'flair_position': flair_position,
                'flair_self_assign_enabled': flair_self_assign,
                'link_flair_position': link_flair_position,
                'link_flair_self_assign_enabled': link_flair_self_assign}
        return self.request_json(self.config['flairconfig'], data=data)

    def flair_list(self, subreddit, limit=None):
        """Return generator of flair mappings.

        Each flair mapping is a dict with three keys. 'user', 'flair_text' and
        'flair_css_class'.

        """
        return self.get_content(self.config['flairlist'] %
                                six.text_type(subreddit),
                                limit=limit, root_field=None,
                                thing_field='users', after_field='next')

    @decorators.require_login
    @decorators.require_moderator
    def get_banned(self, subreddit):
        """Return the list of banned users for the given subreddit."""
        return self.request_json(self.config['banned'] %
                                 six.text_type(subreddit))

    @decorators.require_login
    @decorators.require_moderator
    def get_contributors(self, subreddit):
        """Return the list of contributors for the given subreddit."""
        return self.request_json(self.config['contributors'] %
                                 six.text_type(subreddit))

    def get_flair(self, subreddit, redditor):
        """Return the flair for a user on the given subreddit."""
        params = {'name': six.text_type(redditor)}
        data = self.request_json(self.config['flairlist'] %
                                 six.text_type(subreddit), params=params)
        return data['users'][0]

    def get_moderators(self, subreddit):
        """Return the list of moderators for the given subreddit."""
        return self.request_json(self.config['moderators'] %
                                 six.text_type(subreddit))

    @decorators.require_login
    @decorators.require_moderator
    def get_modqueue(self, subreddit='mod', limit=None):
        """Return the mod-queue for the given subreddit."""
        return self.get_content(self.config['modqueue'] %
                                six.text_type(subreddit),
                                limit=limit)

    @decorators.require_login
    @decorators.require_moderator
    def get_reports(self, subreddit='mod', limit=None):
        """Return the list of reported submissions for the given subreddit."""
        return self.get_content(self.config['reports'] %
                                six.text_type(subreddit),
                                limit=limit)

    @decorators.require_login
    @decorators.require_moderator
    def get_settings(self, subreddit):
        """Return the settings for the given subreddit."""
        return self.request_json(self.config['subreddit_settings'] %
                                 six.text_type(subreddit))['data']

    @decorators.require_login
    @decorators.require_moderator
    def get_spam(self, subreddit='mod', limit=None):
        """Return the list of spam-filtered items for the given subreddit."""
        return self.get_content(self.config['spam'] % six.text_type(subreddit),
                                limit=limit)

    @decorators.require_login
    @decorators.require_moderator
    def get_stylesheet(self, subreddit):
        """Return the stylesheet and images for the given subreddit."""
        return self.request_json(self.config['stylesheet'] %
                                 six.text_type(subreddit))['data']

    @decorators.require_login
    @decorators.require_moderator
    def set_flair(self, subreddit, item, flair_text='', flair_css_class=''):
        """Set flair for the user in the given subreddit.

        Item can be a string, Redditor object, or Submission object. If item is
        a string it will be treated as the name of a Redditor.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'text': flair_text or '',
                'css_class': flair_css_class or ''}
        if isinstance(item, objects.Submission):
            data['link'] = item.content_id
            evict = item.permalink
        else:
            data['name'] = six.text_type(item)
            evict = self.config['flairlist'] % six.text_type(subreddit)
        response = self.request_json(self.config['flair'], data=data)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([evict])
        return response

    @decorators.require_login
    @decorators.require_moderator
    def set_flair_csv(self, subreddit, flair_mapping):
        """Set flair for a group of users in the given subreddit.

        flair_mapping should be a list of dictionaries with the following keys:
          user: the user name
          flair_text: the flair text for the user (optional)
          flair_css_class: the flair css class for the user (optional)

        :returns: The json response from the server.

        """
        if not flair_mapping:
            raise errors.ClientException('flair_mapping must be set')
        item_order = ['user', 'flair_text', 'flair_css_class']
        lines = []
        for mapping in flair_mapping:
            if 'user' not in mapping:
                raise errors.ClientException('flair_mapping must '
                                             'contain `user` key')
            lines.append(','.join([mapping.get(x, '') for x in item_order]))
        response = []
        while len(lines):
            data = {'r': six.text_type(subreddit),
                    'flair_csv': '\n'.join(lines[:100])}
            response.extend(self.request_json(self.config['flaircsv'],
                                              data=data))
            lines = lines[100:]
        stale_url = self.config['flairlist'] % six.text_type(subreddit)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([stale_url])
        return response

    @decorators.require_login
    @decorators.require_moderator
    def set_settings(self, subreddit, title, public_description='',
                     description='', language='en', subreddit_type='public',
                     content_options='any', over_18=False, default_set=True,
                     show_media=False, domain='', domain_css=False,
                     domain_sidebar=False, header_hover_text='',
                     prev_description_id=None,
                     prev_public_description_id=None, wikimode='disabled',
                     wiki_edit_age=30, wiki_edit_karma=100, **kwargs):
        """Set the settings for the given subreddit.

        :returns: The json response from the server.

        """

        # Temporary support for no longer valid entries
        wiki_edit_age = wiki_edit_age or ''
        wiki_edit_karma = wiki_edit_karma or ''

        data = {'r': six.text_type(subreddit),
                'sr': subreddit.content_id,
                'title': title,
                'public_description': public_description,
                'description': description,
                'lang': language,
                'type': subreddit_type,
                'link_type': content_options,
                'over_18': 'on' if over_18 else 'off',
                'allow_top': 'on' if default_set else 'off',
                'show_media': 'on' if show_media else 'off',
                'domain': domain or '',
                'domain_css': 'on' if domain_css else 'off',
                'domain_sidebar': 'on' if domain_sidebar else 'off',
                'header-title': header_hover_text or '',
                'wikimode': wikimode,
                'wiki_edit_age': six.text_type(wiki_edit_age),
                'wiki_edit_karma': six.text_type(wiki_edit_karma)}
        if prev_description_id is not None:
            data['prev_description_id'] = prev_description_id
        if prev_public_description_id is not None:
            data['prev_public_description_id'] = prev_public_description_id
        if kwargs:
            msg = 'Extra settings fields: {0}'.format(kwargs.keys())
            warn_explicit(msg, UserWarning, '', 0)
            data.update(kwargs)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([self.config['subreddit_settings'] %
                                six.text_type(subreddit)])
        return self.request_json(self.config['site_admin'], data=data)

    @decorators.require_login
    @decorators.require_moderator
    def set_stylesheet(self, subreddit, stylesheet, prevstyle=None):
        """Set stylesheet for the given subreddit.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'stylesheet_contents': stylesheet,
                'op': 'save'}  # Options: save / preview
        if prevstyle is not None:
            data['prevstyle'] = prevstyle
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([self.config['stylesheet'] %
                                six.text_type(subreddit)])
        return self.request_json(self.config['subreddit_css'], data=data)

    @decorators.require_login
    @decorators.RequireCaptcha
    def submit(self, subreddit, title, text=None, url=None, captcha=None):
        """Submit a new link to the given subreddit.

        Accepts either a Subreddit object or a str containing the subreddit's
        display name.

        :returns: The url to the submission.

        """
        if bool(text) == bool(url):
            raise TypeError('One (and only one) of text or url is required!')
        data = {'sr': six.text_type(subreddit),
                'title': title}
        if text:
            data['kind'] = 'self'
            data['text'] = text
        else:
            data['kind'] = 'link'
            data['url'] = url
        if captcha:
            data.update(captcha)
        result = self.request_json(self.config['submit'], data=data)
        # pylint: disable-msg=E1101
        return self.get_submission(result['data']['url'])

    def subscribe(self, subreddit):
        """Subscribe to the given subreddit by display name."""
        self._subscribe(sr_name=subreddit)

    def unsubscribe(self, subreddit):
        """Unsubscribe from the given subreddit by display name."""
        self._subscribe(sr_name=subreddit, unsubscribe=True)

    def update_settings(self, subreddit, **kwargs):
        """Update only the given settings for the given subreddit.

        The settings to update must be given by keyword and match one of the
        parameter names in `set_settings`.

        :returns: The json response from the server.

        """
        settings = self.get_settings(subreddit)
        settings.update(kwargs)
        del settings['subreddit_id']
        return self.set_settings(subreddit, **settings)

    def upload_image(self, subreddit, image, name=None, header=False):
        """Upload an image to the subreddit.

        :param image: A readable file object
        :param name: The name to provide the image. When None the name will be
            filename less any extension.
        :param header: When true, upload the image as the subreddit header.
        :returns: True when the upload was successful. False otherwise. Note
            this is subject to change.

        """
        if name and header:
            raise TypeError('Both name and header cannot be set.')
        image_type = None
        # Verify image is a jpeg or png and meets size requirements
        if not isinstance(image, file):
            raise TypeError('`image` argument must be a file object')
        size = os.path.getsize(image.name)
        if size < MIN_IMAGE_SIZE:
            raise errors.ClientException('`image` is not a valid image')
        elif size > MAX_IMAGE_SIZE:
            raise errors.ClientException('`image` is too big. Max: {0} bytes'
                                         .format(MAX_IMAGE_SIZE))
        first_bytes = image.read(MIN_IMAGE_SIZE)
        image.seek(0)
        if first_bytes.startswith(JPEG_HEADER):
            image_type = 'jpg'
        elif first_bytes.startswith(PNG_HEADER):
            image_type = 'png'
        else:
            raise errors.ClientException('`image` is not a valid image')
        data = {'r': six.text_type(subreddit), 'img_type': image_type}
        if header:
            data['header'] = 1
        else:
            if not name:
                name = os.path.splitext(os.path.basename(image.name))[0]
            data['name'] = name
        response = self._request(self.config['upload_image'], data=data,
                                 files={'file': image})
        # HACK: Until json response, attempt to parse the errors
        json_start = response.find('[[')
        json_end = response.find(']]')
        try:
            image_errors = dict(json.loads(response[json_start:json_end + 2]))
        except Exception:  # pylint: disable-msg=W0703
            warn_explicit('image_upload parsing issue', UserWarning, '', 0)
            return False
        if image_errors['BAD_CSS_NAME']:
            raise errors.APIException(image_errors['BAD_CSS_NAME'], None)
        elif image_errors['IMAGE_ERROR']:
            raise errors.APIException(image_errors['IMAGE_ERROR'], None)
        return True


class LoggedInExtension(BaseReddit):

    """Contains methods relevent only to a logged in user."""

    def __init__(self, *args, **kwargs):
        super(LoggedInExtension, self).__init__(*args, **kwargs)

    @decorators.require_login
    def _add_comment(self, thing_id, text):
        """Comment on the given thing with the given text.

        :returns: A Comment object for the newly created comment.

        """
        data = {'thing_id': thing_id,
                'text': text}
        retval = self.request_json(self.config['comment'], data=data)
        # REDDIT: reddit's end should only ever return a single comment
        return retval['data']['things'][0]

    @decorators.require_login
    def _mark_as_read(self, thing_ids, unread=False):
        """Mark each of the supplied thing_ids as (un)read.

        :returns: The json response from the server.

        """
        data = {'id': ','.join(thing_ids)}
        key = 'unread_message' if unread else 'read_message'
        response = self.request_json(self.config[key], data=data)
        urls = [self.config[x] for x in ['inbox', 'moderator', 'unread']]
        helpers._request.evict(urls)  # pylint: disable-msg=E1101,W0212
        return response

    @decorators.require_login
    def create_subreddit(self, name, title, description='', language='en',
                         subreddit_type='public', content_options='any',
                         over_18=False, default_set=True, show_media=False,
                         domain='', wikimode='disabled'):
        """Create a new subreddit.

        :returns: The json response from the server.

        """
        data = {'name': name,
                'title': title,
                'description': description,
                'lang': language,
                'type': subreddit_type,
                'link_type': content_options,
                'over_18': 'on' if over_18 else 'off',
                'allow_top': 'on' if default_set else 'off',
                'show_media': 'on' if show_media else 'off',
                'wikimode': wikimode,
                'domain': domain}
        return self.request_json(self.config['site_admin'], data=data)

    def get_redditor(self, user_name, *args, **kwargs):
        """Return a Redditor instance for the user_name specified."""
        return objects.Redditor(self, user_name, *args, **kwargs)

    def login(self, username=None, password=None):
        """Login to a reddit site.

        Look for username first in parameter, then praw.ini and finally if both
        were empty get it from stdin. Look for password in parameter, then
        praw.ini (but only if username matches that in praw.ini) and finally
        if they both are empty get it with getpass. Add the variables user
        (username) and pswd (password) to your praw.ini file to allow for auto-
        login.

        If an OAuth2 access token is configured, arguments will be ignored and
        user details will be fetched from the site.

        """
        if self.access_token:
            response = self.request_json(self.config['me'])
            self.user = objects.Redditor(self, response['name'], response)
            self.user.__class__ = objects.LoggedInRedditor
            return

        if password and not username:
            raise Exception('Username must be provided when password is.')
        user = username or self.config.user
        if not user:
            sys.stdout.write('Username: ')
            sys.stdout.flush()
            user = sys.stdin.readline().strip()
            pswd = None
        else:
            pswd = password or self.config.pswd
        if not pswd:
            import getpass
            pswd = getpass.getpass('Password for %s: ' % user)

        data = {'passwd': pswd,
                'user': user}
        response = self.request_json(self.config['login'], data=data)
        self.modhash = response['data']['modhash']
        self.user = self.get_redditor(user)
        self.user.__class__ = objects.LoggedInRedditor

    @decorators.require_login
    @decorators.RequireCaptcha
    def send_message(self, recipient, subject, message, captcha=None):
        """Send a message to a redditor or a subreddit's moderators (mod mail).

        When sending a message to a subreddit the recipient parameter must
        either be a subreddit object or the subreddit name needs to be prefixed
        with either '/r/' or '#'.

        :returns: The json response from the server.

        """
        if isinstance(recipient, objects.Subreddit):
            recipient = '/r/%s' % six.text_type(recipient)
        else:
            recipient = six.text_type(recipient)

        data = {'text': message,
                'subject': subject,
                'to': recipient}
        if captcha:
            data.update(captcha)
        response = self.request_json(self.config['compose'], data=data)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([self.config['sent']])
        return response


class OAuth2Extension(BaseReddit):

    """Contains functions specific to working with reddit's OAuth2."""

    def __init__(self, *args, **kwargs):
        super(OAuth2Extension, self).__init__(*args, **kwargs)

    def _handle_oauth_request(self, data):
        auth = (self.config.client_id, self.config.client_secret)
        response = self._request(self.config['access_token_url'], auth=auth,
                                 data=data, raw_response=True)
        if response.status_code != 200:
            raise errors.OAuthException('Unexpected OAuthReturn: %d' %
                                        response.status_code)
        retval = response.json()
        if 'error' in retval:
            raise errors.OAuthException(retval['error'])
        return retval

    @decorators.require_oauth
    def get_access_token(self, code, update_session=True):
        """Return the access token for an OAuth 2 authorization grant.

        :param code: the code received in the request from the OAuth 2 server
        :param update_session: Update the current session with the retrieved
            token(s).
        :returns: A tuple with access_token first and refresh_token second. If
            we have temporary access, then refresh_token will be None.

        """
        data = {'code': code, 'grant_type': 'authorization_code',
                'redirect_uri': self.config.redirect_uri}
        retval = self._handle_oauth_request(data)
        if 'refresh_token' in retval:
            response = (retval['access_token'], retval['refresh_token'])
        else:
            response = (retval['access_token'], None)
        if update_session:
            self.access_token, self.refresh_token = response
        return response

    @decorators.require_oauth
    def get_authorize_url(self, state, scope='identity', refreshable=False):
        """Return the URL to send the user to for OAuth 2 authorization.

        :param state: a unique key that represents this individual client
        :param scope: the reddit scope to ask permissions for. Multiple scopes
            can be enabled by passing in a list of strings.
        :param refreshable: when True, a permanent "refreshable" token is
            issued

        """
        params = {'client_id': self.config.client_id, 'response_type': 'code',
                  'redirect_uri': self.config.redirect_uri, 'state': state}
        if isinstance(scope, six.string_types):
            params['scope'] = scope
        else:
            params['scope'] = ','.join(scope)
        params['duration'] = 'permanent' if refreshable else 'temporary'
        request = Request('GET', self.config['authorize'], params=params)
        return request.prepare().url

    @property
    def has_oauth_app_info(self):
        """Return True when all the necessary OAuth settings are set."""
        return all((self.config.client_id, self.config.client_secret,
                    self.config.redirect_uri))

    @decorators.require_oauth
    def refresh_access_token(self, refresh_token=None):
        """Refresh the access token of a refreshable OAuth 2 grant.

        When provided, the passed in refresh token will be refreshed.
        Otherwise, the current session's refresh token will be used.

        :param refresh_token: the token to refresh
        :returns: The new access token.

        """
        refresh_token = refresh_token or self.refresh_token
        data = {'grant_type': 'refresh_token',
                'redirect_uri': self.config.redirect_uri,
                'refresh_token': refresh_token}
        self.access_token = self._handle_oauth_request(data)['access_token']
        return self.access_token


class Reddit(LoggedInExtension,  # pylint: disable-msg=R0904
             OAuth2Extension,
             SubredditExtension):

    """Contains the base set of reddit API functions."""

    def __init__(self, *args, **kwargs):
        super(Reddit, self).__init__(*args, **kwargs)

    @decorators.RequireCaptcha
    def create_redditor(self, user_name, password, email='', captcha=None):
        """Register a new user.

        :returns: The json response from the server.

        """
        data = {'email': email,
                'passwd': password,
                'passwd2': password,
                'user': user_name}
        if captcha:
            data.update(captcha)
        return self.request_json(self.config['register'], data=data)

    def get_all_comments(self, *args, **kwargs):
        """Return all comments (up to the reddit limit)."""
        return self.get_content(self.config['comments'], *args, **kwargs)

    def get_controversial(self, *args, **kwargs):
        """Return controversial page."""
        return self.get_content(self.config['controversial'], *args, **kwargs)

    def get_front_page(self, *args, **kwargs):
        """Return the front page submissions.

        Default front page if not logged in, otherwise get logged in redditor's
        front page.

        """
        return self.get_content(self.config['reddit_url'], *args, **kwargs)

    def get_info(self, url=None, thing_id=None, limit=None):
        """Look up existing Submissions by thing_id (fullname) or url.

        :param url: The url to lookup.
        :param thing_id: The submission to lookup by fullname.
        :param limit: The maximum number of Submissions to return when looking
            up by url. Default: 25, Max: 100.
        :returns: When thing_id is provided, return the corresponding
            Submission object, or None if not found. When url is provided
            return a list of Submission objects (up to limit) for the url.

        """
        if bool(url) == bool(thing_id):
            raise TypeError('Only one of url or thing_id is required!')
        elif thing_id and limit:
            raise TypeError('Limit keyword is not applicable with thing_id.')
        if url:
            params = {'url': url}
            if limit:
                params['limit'] = limit
        else:
            params = {'id': thing_id}
        items = self.request_json(self.config['info'],
                                  params=params)['data']['children']
        if url:
            return items
        elif items:
            return items[0]
        else:
            return None

    def get_new(self, *args, **kwargs):
        """Return new page."""
        return self.get_content(self.config['new'], *args, **kwargs)

    def get_top(self, *args, **kwargs):
        """Return top page."""
        return self.get_content(self.config['top'], *args, **kwargs)

    def get_popular_reddits(self, *args, **kwargs):
        """Return the most active subreddits."""
        url = self.config['popular_reddits']
        return self.get_content(url, *args, **kwargs)

    def get_random_subreddit(self):
        """Return a random subreddit just like /r/random does."""
        response = self._request(self.config['subreddit'] % 'random',
                                 raw_response=True)
        return self.get_subreddit(response.url.rsplit('/', 2)[-2])

    def get_submission(self, url=None, submission_id=None):
        """Return a Submission object for the given url or submission_id."""
        if bool(url) == bool(submission_id):
            raise TypeError('One (and only one) of id or url is required!')
        if submission_id:
            url = urljoin(self.config['comments'], submission_id)
        return objects.Submission.from_url(self, url)

    def get_subreddit(self, subreddit_name, *args, **kwargs):
        """Return a Subreddit object for the subreddit_name specified."""
        if subreddit_name.lower() == 'random':
            return self.get_random_subreddit()
        return objects.Subreddit(self, subreddit_name, *args, **kwargs)

    def is_username_available(self, username):
        """Return True if username is valid and available, otherwise False."""
        params = {'user': username}
        try:
            result = self.request_json(self.config['username_available'],
                                       params=params)
        except errors.APIException as exception:
            if exception.error_type == 'BAD_USERNAME':
                result = False
            else:
                raise
        return result

    def search(self, query, subreddit=None, sort=None, limit=0, *args,
               **kwargs):
        """Return submissions that match the search query.

        See http://www.reddit.com/help/search for more information on how to
        build a search query.

        """
        params = {'q': query}
        if sort:
            params['sort'] = sort
        if subreddit:
            params['restrict_sr'] = 'on'
            url = self.config['search'] % subreddit
        else:
            url = self.config['search'] % 'all'
        return self.get_content(url, params=params, limit=limit, *args,
                                **kwargs)

    def search_reddit_names(self, query):
        """Return subreddits whose display name contains the query."""
        data = {'query': query}
        results = self.request_json(self.config['search_reddit_names'],
                                    data=data)
        return [self.get_subreddit(name) for name in results['names']]

    @decorators.RequireCaptcha
    def send_feedback(self, name, email, message, reason='feedback',
                      captcha=None):
        """Send feedback to the admins.

        Please don't abuse this. Read the send feedback page at
        http://www.reddit.com/feedback/ (for reddit.com) before use.

        :returns: The json response from the server.

        """
        data = {'name': name,
                'email': email,
                'reason': reason,
                'text': message}
        if captcha:
            data.update(captcha)
        return self.request_json(self.config['feedback'], data=data)
