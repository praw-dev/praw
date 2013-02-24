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
import re
import requests
import six
import sys
from praw import decorators, errors, helpers
from praw.settings import CONFIG
from requests.compat import urljoin
from requests import Request
from six.moves import html_entities
from update_checker import update_check
from warnings import simplefilter, warn_explicit

__version__ = '2.0.11'
UA_STRING = '%%s PRAW/%s Python/%s %s' % (__version__,
                                          sys.version.split()[0],
                                          platform.platform(True))

MIN_IMAGE_SIZE = 128
MAX_IMAGE_SIZE = 512000
JPEG_HEADER = '\xff\xd8\xff'
PNG_HEADER = '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'

# Enable deprecation warnings
simplefilter('default')

# Compatability
if not six.PY3:
    chr = unichr


class Config(object):  # pylint: disable-msg=R0903

    """A class containing the configuration for a reddit site."""

    API_PATHS = {'accept_mod_invite':   'api/accept_moderator_invite',
                 'access_token_url':    'api/v1/access_token/',
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
                 'deleteflair':         'api/deleteflair',
                 'delete_sr_header':    'r/%s/api/delete_sr_header',
                 'delete_sr_image':     'r/%s/api/delete_sr_img',
                 'distinguish':         'api/distinguish/',
                 'edit':                'api/editusertext/',
                 'feedback':            'api/feedback/',
                 'flair':               'api/flair/',
                 'flairconfig':         'api/flairconfig/',
                 'flaircsv':            'api/flaircsv/',
                 'flairlist':           'r/%s/api/flairlist/',
                 'flairtemplate':       'api/flairtemplate/',
                 'friend':              'api/friend/',
                 'friends':             'prefs/friends/',
                 'help':                'help/',
                 'hide':                'api/hide/',
                 'inbox':               'message/inbox/',
                 'info':                'api/info/',
                 'login':               'api/login/',
                 'me':                  'api/v1/me',
                 'moderator':           'message/moderator/',
                 'moderators':          'r/%s/about/moderators/',
                 'modlog':              'r/%s/about/log/',
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
                 'subreddit_comments':  'r/%s/comments/',
                 'sub_comments_gilded': 'r/%s/comments/gilded/',
                 'subreddit_css':       'api/subreddit_stylesheet/',
                 'subreddit_settings':  'r/%s/about/edit/',
                 'subscribe':           'api/subscribe/',
                 'top':                 'top/',
                 'unfriend':            'api/unfriend/',
                 'unhide':              'api/unhide/',
                 'unmarknsfw':          'api/unmarknsfw/',
                 'unmoderated':         'r/%s/about/unmoderated/',
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
        def config_boolean(item):
            return item and item.lower() in ('1', 'yes', 'true', 'on')

        obj = dict(CONFIG.items(site_name))
        self._site_url = 'http://' + obj['domain']
        if 'ssl_domain' in obj:
            self._ssl_url = 'https://' + obj['ssl_domain']
        else:
            self._ssl_url = None
        if 'oauth_domain' in obj:
            if config_boolean(obj['oauth_https']):
                self._oauth_url = 'https://' + obj['oauth_domain']
            else:
                self._oauth_url = 'http://' + obj['oauth_domain']
        else:
            self._oauth_url = self._ssl_url

        self.api_request_delay = float(obj['api_request_delay'])
        self.by_kind = {obj['comment_kind']:    objects.Comment,
                        obj['message_kind']:    objects.Message,
                        obj['redditor_kind']:   objects.Redditor,
                        obj['submission_kind']: objects.Submission,
                        obj['subreddit_kind']:  objects.Subreddit,
                        'modaction':            objects.ModAction,
                        'more':                 objects.MoreComments,
                        'UserList':             objects.UserList}
        self.by_object = dict((value, key) for (key, value) in
                              six.iteritems(self.by_kind))
        self.by_object[objects.LoggedInRedditor] = obj['redditor_kind']
        self.cache_timeout = float(obj['cache_timeout'])
        self.check_for_updates = config_boolean(obj['check_for_updates'])
        self.decode_html_entities = config_boolean(obj['decode_html_entities'])
        self.domain = obj['domain']
        self.output_chars_limit = int(obj['output_chars_limit'])
        self.log_requests = int(obj['log_requests'])
        self.client_id = obj.get('oauth_client_id') or None
        self.client_secret = obj.get('oauth_client_secret') or None
        self.redirect_uri = obj.get('oauth_redirect_uri') or None

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

    """A base class that allows acccess to reddit's API."""

    RETRY_CODES = [502, 503, 504]
    update_checked = False

    def __init__(self, user_agent, site_name=None, disable_update_check=False):
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

        disable_update_check allows you to prevent an update check from
        occuring in spite of the check_for_updates setting in praw.ini.

        """
        if not user_agent or not isinstance(user_agent, six.string_types):
            raise TypeError('User agent must be a non-empty string.')

        self.config = Config(site_name or os.getenv('REDDIT_SITE') or 'reddit')
        self.http = requests.session()
        self.http.headers['User-Agent'] = UA_STRING % user_agent
        self.modhash = None

        # Check for updates if permitted and this is the first Reddit instance
        if not disable_update_check and not self.update_checked \
                and self.config.check_for_updates:
            update_check(__name__, __version__)
            self.update_checked = True

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
        def decode(match):
            return chr(html_entities.name2codepoint[match.group(1)])

        # pylint: disable-msg=W0212
        timeout = self.config.timeout if timeout is None else timeout
        remaining_attempts = 3
        while True:
            try:
                retval = helpers._request(self, url, params, data, files=files,
                                          auth=auth, raw_response=raw_response,
                                          timeout=timeout)
                if not raw_response and self.config.decode_html_entities:
                    retval = re.sub('&([^;]+);', decode, retval)
                return retval
            except requests.exceptions.HTTPError as error:
                remaining_attempts -= 1
                if error.response.status_code not in self.RETRY_CODES or \
                        remaining_attempts == 0:
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

    @decorators.oauth_generator
    def get_content(self, url, params=None, limit=0, place_holder=None,
                    root_field='data', thing_field='children',
                    after_field='after', _use_oauth=False):
        """A generator method to return reddit content from a URL.

        Starts at the initial url, and fetches content using the `after`
        JSON data until `limit` entries have been fetched, or the
        `place_holder` has been reached.

        :param url: the url to start fetching content from
        :param params: dictionary containing extra GET data to put in the url
        :param limit: the number of content entries to fetch. If limit <= 0,
            fetch the default for your account (25 for unauthenticated
            users). If limit is None, then fetch as many entries as possible
            (reddit returns at most 100 per request, however, PRAW will
            automatically make additional requests as necessary).
        :param place_holder: if not None, the method will fetch `limit`
            content, stopping if it finds content with `id` equal to
            `place_holder`.
        :param root_field: indicates the field in the json response that holds
            the data. Most objects use 'data', however some (flairlist) don't
            have the 'data' object. Use None for the root object.
        :param thing_field: indicates the field under the root_field which
            contains the list of things. Most objects use 'children'.
        :param after_field: indicates the field which holds the after item
            element
        :type place_holder: a string corresponding to a reddit content id, e.g.
            't3_asdfasdf'
        :returns: a list of reddit content, of type Subreddit, Comment,
            Submission or user flair.

        """
        objects_found = 0
        params = params or {}
        fetch_all = fetch_once = False
        if limit is None:
            fetch_all = True
            params['limit'] = 1024  # Just use a big number
        elif limit > 0:
            params['limit'] = limit
        else:
            fetch_once = True

        # While we still need to fetch more content to reach our limit, do so.
        while fetch_once or fetch_all or objects_found < limit:
            if _use_oauth:  # Set the necessary _use_oauth value
                assert self._use_oauth is False
                self._use_oauth = _use_oauth  # pylint: disable-msg=W0201
            try:
                page_data = self.request_json(url, params=params)
            finally:  # Restore _use_oauth value
                if _use_oauth:
                    self._use_oauth = False  # pylint: disable-msg=W0201
            fetch_once = False
            if root_field:
                root = page_data[root_field]
            else:
                root = page_data
            for thing in root[thing_field]:
                yield thing
                objects_found += 1
                # Terminate when we've reached the limit, or place holder
                if objects_found == limit or (place_holder and
                                              thing.id == place_holder):
                    return
            # Set/update the 'after' parameter for the next iteration
            if root.get(after_field):
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
        if isinstance(data, dict) and 'data' in data \
                and 'modhash' in data['data']:
            self.modhash = data['data']['modhash']
        return data


class OAuth2Reddit(BaseReddit):

    """Provides functionality for obtaining reddit OAuth2 access tokens."""

    def __init__(self, *args, **kwargs):
        super(OAuth2Reddit, self).__init__(*args, **kwargs)
        self.client_id = self.config.client_id
        self.client_secret = self.config.client_secret
        self.redirect_uri = self.config.redirect_uri

    def _handle_oauth_request(self, data):
        auth = (self.client_id, self.client_secret)
        url = self.config['access_token_url']
        response = self._request(url, auth=auth, data=data, raw_response=True)
        if response.status_code != 200:
            raise errors.OAuthException('Unexpected OAuthReturn: %d' %
                                        response.status_code, url)
        retval = response.json()
        if 'error' in retval:
            error = retval['error']
            if error == 'invalid_grant':
                raise errors.OAuthInvalidGrant(error, url)
            raise errors.OAuthException(retval['error'], url)
        return retval

    @decorators.require_oauth
    def get_access_information(self, code):
        """Return the access information for an OAuth2 authorization grant.

        :param code: the code received in the request from the OAuth2 server
        :returns: A dictionary with the key/value pairs for access_token,
            refresh_token and scope. The refresh_token value will be done when
            the OAuth2 grant is not refreshable. The scope value will be a set
            containing the scopes the tokens are valid for.

        """
        data = {'code': code, 'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri}
        retval = self._handle_oauth_request(data)
        return {'access_token': retval['access_token'],
                'refresh_token': retval.get('refresh_token'),
                'scope': set(retval['scope'].split(','))}

    @decorators.require_oauth
    def get_authorize_url(self, state, scope='identity', refreshable=False):
        """Return the URL to send the user to for OAuth2 authorization.

        :param state: a unique key that represents this individual client
        :param scope: the reddit scope to ask permissions for. Multiple scopes
            can be enabled by passing in a container of strings.
        :param refreshable: when True, a permanent "refreshable" token is
            issued

        """
        params = {'client_id': self.client_id, 'response_type': 'code',
                  'redirect_uri': self.redirect_uri, 'state': state}
        if isinstance(scope, six.string_types):
            params['scope'] = scope
        else:
            params['scope'] = ','.join(scope)
        params['duration'] = 'permanent' if refreshable else 'temporary'
        request = Request('GET', self.config['authorize'], params=params)
        return request.prepare().url

    @property
    def has_oauth_app_info(self):
        """Return True if all the necessary OAuth settings are set."""
        return all((self.client_id, self.client_secret, self.redirect_uri))

    @decorators.require_oauth
    def refresh_access_information(self, refresh_token):
        """Return updated access information for an OAuth2 authorization grant.

        :param refresh_token: the refresh token used to obtain the updated
            information
        :returns: A dictionary with the key/value pairs for access_token,
            refresh_token and scope. The refresh_token value will be done when
            the OAuth2 grant is not refreshable. The scope value will be a set
            containing the scopes the tokens are valid for.

        """
        data = {'grant_type': 'refresh_token',
                'redirect_uri': self.redirect_uri,
                'refresh_token': refresh_token}
        retval = self._handle_oauth_request(data)
        return {'access_token': retval['access_token'],
                'refresh_token': refresh_token,
                'scope': set(retval['scope'].split(','))}

    def set_oauth_app_info(self, client_id, client_secret, redirect_uri):
        """Set the App information to use with oauthentication.

        This function need only be called if your praw.ini site configuration
        does not already contain the neccessary information.

        Go to https://ssl.reddit.com/prefs/apps/ to discover the appropriate
        values for your application.

        :param client_id: the client_id of your application
        :param client_secret: the client_secret of your application
        :param redirect_uri: the redirect_uri of your application

        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri


class UnauthenticatedReddit(BaseReddit):

    """This mixin provides bindings for basic functions of reddit's API.

    None of these functions require authenticated access to reddit's API.

    """

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

    def get_all_comments(self, gilded_only=False, *args, **kwargs):
        """Return all comments (up to the reddit limit).

        :param gilded_only: If True only return gilded comments.

        """
        return self.get_comments('all', gilded_only, *args, **kwargs)

    @decorators.restrict_access(scope='read')
    def get_comments(self, subreddit, gilded_only=False, *args, **kwargs):
        """Return latest comments on the given subreddit.

        :param gilded_only: If True only return gilded comments.

        """
        if gilded_only:
            url = self.config['sub_comments_gilded'] % six.text_type(subreddit)
        else:
            url = self.config['subreddit_comments'] % six.text_type(subreddit)
        return self.get_content(url, *args, **kwargs)

    @decorators.restrict_access(scope='read')
    def get_controversial(self, *args, **kwargs):
        """Return controversial page."""
        return self.get_content(self.config['controversial'], *args, **kwargs)

    def get_flair(self, subreddit, redditor):
        """Return the flair for a user on the given subreddit."""
        params = {'name': six.text_type(redditor)}
        data = self.request_json(self.config['flairlist'] %
                                 six.text_type(subreddit), params=params)
        return data['users'][0]

    @decorators.restrict_access(scope='read')
    def get_front_page(self, *args, **kwargs):
        """Return the front page submissions.

        Default front page if not logged in, otherwise get logged in redditor's
        front page.

        """
        return self.get_content(self.config['reddit_url'], *args, **kwargs)

    @decorators.restrict_access(scope='read')
    def get_info(self, url=None, thing_id=None, limit=None):
        """Look up existing Submissions by thing_id (fullname) or url.

        :param url: The url to lookup.
        :param thing_id: The submission to lookup by fullname.
        :param limit: The maximum number of Submissions to return when looking
            up by url. When None, uses account default settings.
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

    def get_moderators(self, subreddit):
        """Return the list of moderators for the given subreddit."""
        return self.request_json(self.config['moderators'] %
                                 six.text_type(subreddit))

    @decorators.restrict_access(scope='read')
    def get_new(self, *args, **kwargs):
        """Return new page."""
        return self.get_content(self.config['new'], *args, **kwargs)

    def get_popular_reddits(self, *args, **kwargs):
        """Return the most active subreddits."""
        url = self.config['popular_reddits']
        return self.get_content(url, *args, **kwargs)

    def get_random_subreddit(self):
        """Return a random subreddit just like /r/random does."""
        response = self._request(self.config['subreddit'] % 'random',
                                 raw_response=True)
        return self.get_subreddit(response.url.rsplit('/', 2)[-2])

    def get_redditor(self, user_name, *args, **kwargs):
        """Return a Redditor instance for the user_name specified."""
        return objects.Redditor(self, user_name, *args, **kwargs)

    def get_submission(self, url=None, submission_id=None, comment_limit=0,
                       comment_sort=None):
        """Return a Submission object for the given url or submission_id.

        :param comment_limit: The desired number of comments to fetch. If <= 0
            fetch the default number for the session's user. If None, fetch the
            maximum possible.
        :param comment_sort: The sort order for retrived comments. When None
            use the default for the session's user.

        """
        if bool(url) == bool(submission_id):
            raise TypeError('One (and only one) of id or url is required!')
        if submission_id:
            url = urljoin(self.config['comments'], submission_id)
        return objects.Submission.from_url(self, url,
                                           comment_limit=comment_limit,
                                           comment_sort=comment_sort)

    def get_subreddit(self, subreddit_name, *args, **kwargs):
        """Return a Subreddit object for the subreddit_name specified."""
        if subreddit_name.lower() == 'random':
            return self.get_random_subreddit()
        return objects.Subreddit(self, subreddit_name, *args, **kwargs)

    @decorators.restrict_access(scope='read')
    def get_top(self, *args, **kwargs):
        """Return top page."""
        return self.get_content(self.config['top'], *args, **kwargs)

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


class AuthenticatedReddit(OAuth2Reddit, UnauthenticatedReddit):

    """This class adds the methods necessary for authenticating with reddit.

    Authentication can either be login based (through login), or OAuth2 based
    (via set_access_credentials).

    """

    def __init__(self, *args, **kwargs):
        super(AuthenticatedReddit, self).__init__(*args, **kwargs)
        # Add variable to distinguish between authentication type
        #  * None means unauthenticated
        #  * True mean login authenticated
        #  * set(...) means OAuth authenticated with the scopes in the set
        self._authentication = None
        self._use_oauth = False  # Updated on a request by request basis
        self.access_token = None
        self.refresh_token = None
        self.user = None

    def __str__(self):
        if isinstance(self._authentication, set):
            return 'OAuth2 reddit session (scopes: {0})'.format(
                ', '.join(self._authentication))
        elif self._authentication:
            return 'LoggedIn reddit session (user: {0})'.format(self.user)
        else:
            return 'Unauthenticated reddit sesssion'

    @decorators.restrict_access(scope=None, login=True)
    def accept_moderator_invite(self, subreddit):
        """Accept a moderator invite to the given subreddit.

        Callable upon an instance of Subreddit with no arguments.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit)}
        # Clear moderated subreddits and cache
        # pylint: disable-msg=W0212
        self.user._mod_subs = None
        helpers._request.evict([self.config['my_mod_reddits']])
        return self.request_json(self.config['accept_mod_invite'], data=data)

    def clear_authentication(self):
        """Clear any existing authentication on the reddit object.

        This function is implicitly called on `login` and
        `set_access_credentials`.

        """
        self._authentication = None
        self.access_token = None
        self.refresh_token = None
        self.http.cookies.clear()
        helpers._request.empty()  # pylint: disable-msg=W0212
        self.user = None

    def get_access_information(self, code,  # pylint: disable-msg=W0221
                               update_session=True):
        """Return the access information for an OAuth2 authorization grant.

        :param code: the code received in the request from the OAuth2 server
        :param update_session: Update the current session with the retrieved
        token(s).
        :returns: A dictionary with the key/value pairs for access_token,
        refresh_token and scope. The refresh_token value will be done when
        the OAuth2 grant is not refreshable.

        """
        retval = super(AuthenticatedReddit, self).get_access_information(code)
        if update_session:
            self.set_access_credentials(**retval)
        return retval

    @decorators.restrict_access(scope='identity', oauth_only=True)
    def get_me(self):
        """Return a LoggedInRedditor object."""
        response = self.request_json(self.config['me'])
        user = objects.Redditor(self, response['name'], response)
        user.__class__ = objects.LoggedInRedditor
        return user

    def has_scope(self, scope):
        """Return True if OAuth2 authorized for the passed in scope."""
        return self.is_oauth_session() and scope in self._authentication

    def is_logged_in(self):
        """Return True when session is authenticated via login."""
        return self._authentication is True

    def is_oauth_session(self):
        """Return True when the current session is an OAuth2 session."""
        return isinstance(self._authentication, set)

    def login(self, username=None, password=None):
        """Login to a reddit site.

        Look for username first in parameter, then praw.ini and finally if both
        were empty get it from stdin. Look for password in parameter, then
        praw.ini (but only if username matches that in praw.ini) and finally
        if they both are empty get it with getpass. Add the variables user
        (username) and pswd (password) to your praw.ini file to allow for auto-
        login.

        A succesful login will overwrite any existing authentication.

        """
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
        self.clear_authentication()
        self.request_json(self.config['login'], data=data)
        # Update authentication settings
        self._authentication = True
        self.user = self.get_redditor(user)
        self.user.__class__ = objects.LoggedInRedditor

    def refresh_access_information(self,  # pylint: disable-msg=W0221
                                   refresh_token=None,
                                   update_session=True):
        """Return updated access information for an OAuth2 authorization grant.

        :param refresh_token: The refresh token used to obtain the updated
            information. When not provided, use the storred refresh_token.
        :param update_session: Update the session with the returned data.
        :returns: A dictionary with the key/value pairs for access_token,
            refresh_token and scope. The refresh_token value will be done when
            the OAuth2 grant is not refreshable. The scope value will be a set
            containing the scopes the tokens are valid for.

        """
        response = super(AuthenticatedReddit, self).refresh_access_information(
            refresh_token=refresh_token or self.refresh_token)
        if update_session:
            self.set_access_credentials(**response)
        return response

    @decorators.require_oauth
    def set_access_credentials(self, scope, access_token, refresh_token=None,
                               update_user=True):
        """Set the credentials used for OAuth2 authentication.

        Calling this funciton will overwrite any currently existing access
        credentials.

        :param scope: A set of reddit scopes the tokens provide access to
        :param access_token: the access_token of the authentication
        :param refresh_token: the refresh token of the authentication
        :param update_user: Whether or not to set the user attribute for
            identity scopes

        """
        if not isinstance(scope, set):
            raise TypeError('`scope` parameter must be a set')
        self.clear_authentication()
        # Update authentication settings
        self._authentication = scope
        self.access_token = access_token
        self.refresh_token = refresh_token
        # Update the user object
        if update_user and 'identity' in scope:
            self.user = self.get_me()


class ModConfigMixin(AuthenticatedReddit):

    """Adds methods requiring the 'modconfig' scope (or mod access)."""

    @decorators.restrict_access(scope='modconfig')
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

    @decorators.restrict_access(scope='modconfig')
    def delete_image(self, subreddit, name=None, header=False):
        """Delete an image from the subreddit.

        :param name: The name of the image if removing a CSS image.
        :param header: When true, delete the subreddit header.
        :returns: The json response from the server.

        """
        if name and header:
            raise TypeError('Both name and header cannot be set.')
        elif name:
            data = {'img_name': name}
            url = self.config['delete_sr_image']
            # pylint: disable-msg=E1101,W0212
            helpers._request.evict([self.config['stylesheet'] %
                                    six.text_type(subreddit)])
        else:
            data = True
            url = self.config['delete_sr_header']
        return self.request_json(url % six.text_type(subreddit), data=data)

    @decorators.restrict_access(scope='modconfig')
    def get_settings(self, subreddit):
        """Return the settings for the given subreddit."""
        return self.request_json(self.config['subreddit_settings'] %
                                 six.text_type(subreddit))['data']

    @decorators.restrict_access(scope='modconfig')
    def set_settings(self, subreddit, title, public_description='',
                     description='', language='en', subreddit_type='public',
                     content_options='any', over_18=False, default_set=True,
                     show_media=False, domain='', domain_css=False,
                     domain_sidebar=False, header_hover_text='',
                     prev_description_id=None,
                     prev_public_description_id=None, wikimode='disabled',
                     wiki_edit_age=30, wiki_edit_karma=100, **kwargs):
        """Set the settings for the given subreddit.

        :param subreddit: Must be  a subreddit object.
        :returns: The json response from the server.

        """
        data = {'sr': subreddit.fullname,
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

    @decorators.restrict_access(scope='modconfig')
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

    @decorators.restrict_access(scope='modconfig')
    def upload_image(self, subreddit, image_path, name=None, header=False):
        """Upload an image to the subreddit.

        :param image_path: A path to the jpg or png image you want to upload.
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
        with open(image_path, 'rb') as image:
            size = os.path.getsize(image.name)
            if size < MIN_IMAGE_SIZE:
                raise errors.ClientException('`image` is not a valid image')
            elif size > MAX_IMAGE_SIZE:
                raise errors.ClientException('`image` is too big. Max: {0} '
                                             'bytes'.format(MAX_IMAGE_SIZE))
            first_bytes = image.read(MIN_IMAGE_SIZE)
            image.seek(0)
            if first_bytes.startswith(JPEG_HEADER):
                image_type = 'jpg'
            elif first_bytes.startswith(PNG_HEADER):
                image_type = 'png'
            else:
                raise errors.ClientException('`image` must be either jpg or '
                                             'png.')
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


class ModFlairMixin(AuthenticatedReddit):

    """Adds methods requring the 'modflair' scope (or mod access)."""

    @decorators.restrict_access(scope='modflair')
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

    @decorators.restrict_access(scope='modflair')
    def clear_flair_templates(self, subreddit, is_link=False):
        """Clear flair templates for the given subreddit.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'flair_type': 'LINK_FLAIR' if is_link else 'USER_FLAIR'}
        return self.request_json(self.config['clearflairtemplates'], data=data)

    @decorators.restrict_access(scope='modflair')
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

    @decorators.restrict_access(scope='modflair')
    def delete_flair(self, subreddit, user):
        """Delete the flair for the given user on the given subreddit.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit),
                'name': six.text_type(user)}
        return self.request_json(self.config['deleteflair'], data=data)

    @decorators.restrict_access(scope='modflair')
    def get_flair_list(self, subreddit, limit=0):
        """Return a get_content generator of flair mappings.

        Each flair mapping is a dict with three keys. 'user', 'flair_text' and
        'flair_css_class'.

        """
        return self.get_content(self.config['flairlist'] %
                                six.text_type(subreddit),
                                limit=limit, root_field=None,
                                thing_field='users', after_field='next')

    @decorators.restrict_access(scope='modflair')
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
            data['link'] = item.fullname
            evict = item.permalink
        else:
            data['name'] = six.text_type(item)
            evict = self.config['flairlist'] % six.text_type(subreddit)
        response = self.request_json(self.config['flair'], data=data)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([evict])
        return response

    @decorators.restrict_access(scope='modflair')
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


class ModLogMixin(AuthenticatedReddit):

    """Adds methods requring the 'modlog' scope (or mod access)."""

    @decorators.restrict_access(scope='modlog')
    def get_mod_log(self, subreddit, limit=0, mod=None, action=None):
        """Return a get_content generator for moderation log items.

        :param mod: If given, only return the actions made by this moderator.
                    Both a moderator name or Redditor object can be used here.
        :param action: If given, only return entries for the specified action.

        """
        params = {}
        if mod is not None:
            params['mod'] = six.text_type(mod)
        if type is not None:
            params['type'] = six.text_type(action)
        return self.get_content(self.config['modlog'] %
                                six.text_type(subreddit), limit=limit,
                                params=params)


class ModOnlyMixin(AuthenticatedReddit):

    """Adds methods requring the logged in moderator access."""

    @decorators.restrict_access(scope=None, mod=True)
    def get_banned(self, subreddit):
        """Return the list of banned users for the given subreddit."""
        return self.request_json(self.config['banned'] %
                                 six.text_type(subreddit))

    @decorators.restrict_access(scope=None, mod=True)
    def get_contributors(self, subreddit):
        """Return the list of contributors for the given subreddit."""
        return self.request_json(self.config['contributors'] %
                                 six.text_type(subreddit))

    @decorators.restrict_access(scope=None, mod=True)
    def get_mod_queue(self, subreddit='mod', limit=0):
        """Return a get_content_generator for the  moderator queue."""
        return self.get_content(self.config['modqueue'] %
                                six.text_type(subreddit), limit=limit)

    @decorators.restrict_access(scope=None, mod=True)
    def get_reports(self, subreddit='mod', limit=0):
        """Return a get_content generator of reported submissions."""
        return self.get_content(self.config['reports'] %
                                six.text_type(subreddit), limit=limit)

    @decorators.restrict_access(scope=None, mod=True)
    def get_spam(self, subreddit='mod', limit=0):
        """Return a get_content generator of spam-filtered items."""
        return self.get_content(self.config['spam'] % six.text_type(subreddit),
                                limit=limit)

    @decorators.restrict_access(scope=None, mod=True)
    def get_stylesheet(self, subreddit):
        """Return the stylesheet and images for the given subreddit."""
        return self.request_json(self.config['stylesheet'] %
                                 six.text_type(subreddit))['data']

    @decorators.restrict_access(scope=None, mod=True)
    def get_unmoderated(self, subreddit='mod', limit=0):
        """Return a get_content generator of unmoderated items."""
        return self.get_content(self.config['unmoderated'] %
                                six.text_type(subreddit), limit=limit)


class MySubredditsMixin(AuthenticatedReddit):

    """Adds methods requiring the 'mysubreddits' scope (or login)."""

    @decorators.restrict_access(scope='mysubreddits')
    def get_my_contributions(self, limit=0):
        """Return the subreddits where the session's user is a contributor."""
        return self.get_content(self.config['my_con_reddits'], limit=limit)

    @decorators.restrict_access(scope='mysubreddits')
    def get_my_moderation(self, limit=0):
        """Return the subreddits where the session's user is a mod."""
        return self.get_content(self.config['my_mod_reddits'], limit=limit)

    @decorators.restrict_access(scope='mysubreddits')
    def get_my_reddits(self, limit=0):
        """Return the subreddits that the logged in user is subscribed to."""
        return self.get_content(self.config['my_reddits'], limit=limit)


class PrivateMessagesMixin(AuthenticatedReddit):

    """Adds methods requring the 'privatemessages' scope (or login)."""

    @decorators.restrict_access(scope='privatemessages')
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

    @decorators.restrict_access(scope='privatemessages')
    def get_inbox(self, limit=0):
        """Return a generator for inbox messages."""
        return self.get_content(self.config['inbox'], limit=limit)

    @decorators.restrict_access(scope='privatemessages')
    def get_mod_mail(self, limit=0):
        """Return a generator for moderator messages."""
        return self.get_content(self.config['moderator'], limit=limit)

    @decorators.restrict_access(scope='privatemessages')
    def get_sent(self, limit=0):
        """Return a generator for sent messages."""
        return self.get_content(self.config['sent'], limit=limit)

    @decorators.restrict_access(scope='privatemessages')
    def get_unread(self, limit=0, unset_has_mail=False, update_user=False):
        """Return a generator for unread messages.

        :param unset_has_mail: When true, clear the has_mail flag (orangered)
            for the user.
        :param update_user: If both unset_has_mail and update user is true, set
            the has_mail attribute of the logged-in user to False.

        """
        params = {'mark': 'true'} if unset_has_mail else None
        # Update the user object
        if unset_has_mail and update_user and hasattr(self.user, 'has_mail'):
            self.user.has_mail = False
        return self.get_content(self.config['unread'], limit=limit,
                                params=params)

    @decorators.restrict_access(scope='privatemessages')
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


class SubmitMixin(AuthenticatedReddit):

    """Adds methods requring the 'submit' scope (or login)."""

    @decorators.restrict_access(scope='submit')
    def _add_comment(self, thing_id, text):
        """Comment on the given thing with the given text.

        :returns: A Comment object for the newly created comment.

        """
        data = {'thing_id': thing_id,
                'text': text}
        retval = self.request_json(self.config['comment'], data=data)
        # REDDIT: reddit's end should only ever return a single comment
        return retval['data']['things'][0]

    @decorators.restrict_access(scope='submit')
    @decorators.RequireCaptcha
    def submit(self, subreddit, title, text=None, url=None, captcha=None):
        """Submit a new link to the given subreddit.

        Accepts either a Subreddit object or a str containing the subreddit's
        display name.

        :returns: The newly created Submission object if the reddit instance
            can access it. Otherwise, return the url to the submission.

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
        url = result['data']['url']
        # Clear the OAUth setting when attempting to fetch the submission
        # pylint: disable-msg=W0212
        if self._use_oauth:
            self._use_oauth = False
            # Hack until reddit/627 is resolved
            if url.startswith(self.config._oauth_url):
                url = self.config._site_url + url[len(self.config._oauth_url):]
        try:
            return self.get_submission(url)
        except requests.exceptions.HTTPError as error:
            # The request may still fail if the submission was made to a
            # private subreddit.
            if error.code == 403:
                return url
            raise


class SubscribeMixin(AuthenticatedReddit):

    """Adds methods requring the 'subscribe' scope (or login)."""

    @decorators.restrict_access(scope='subscribe')
    def subscribe(self, subreddit, unsubscribe=False):
        """Subscribe to the given subreddit.

        :param subreddit: Either the subreddit name or a subreddit object.
        :param unsubscribe: When true, unsubscribe.
        :returns: The json response from the server.

        """
        data = {'action': 'unsub' if unsubscribe else 'sub',
                'sr_name': six.text_type(subreddit)}
        response = self.request_json(self.config['subscribe'], data=data)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([self.config['my_reddits']])
        return response

    def unsubscribe(self, subreddit):
        """Unsubscribe from the given subreddit.

        :param subreddit: Either the subreddit name or a subreddit object.
        :returns: The json response from the server.

        """
        return self.subscribe(subreddit, unsubscribe=True)


class Reddit(ModConfigMixin, ModFlairMixin, ModLogMixin, ModOnlyMixin,
             MySubredditsMixin, PrivateMessagesMixin, SubmitMixin,
             SubscribeMixin):

    """Provides the fullest access to reddit's API."""


# Prevent recursive import
from praw import objects
