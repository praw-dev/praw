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

"""Reddit object."""

import json
import os
import platform
import six
import sys
import uuid
from warnings import warn, warn_explicit

from praw import decorators, errors, helpers, objects
from praw.compat import (HTTPCookieProcessor,  # pylint: disable-msg=E0611
                         HTTPError, build_opener, http_cookiejar, http_client,
                         urljoin)
from praw.settings import CONFIG

from rauth.service import OAuth2Service

__version__ = '1.0.14'

UA_STRING = '%%s PRAW/%s Python/%s %s' % (__version__,
                                          sys.version.split()[0],
                                          platform.platform(True))


class Config(object):  # pylint: disable-msg=R0903
    """A class containing the configuration for a reddit site."""
    API_PATHS = {'approve':             'api/approve/',
                 'banned':              'r/%s/about/banned/',
                 'captcha':             'captcha/',
                 'clearflairtemplates': 'api/clearflairtemplates/',
                 'comment':             'api/comment/',
                 'comments':            'comments/',
                 'compose':             'api/compose/',
                 'contributors':        'r/%s/about/contributors/',
                 'controversial':       'controversial/',
                 'del':                 'api/del/',
                 'distinguish':         'api/distinguish/yes/',
                 'edit':                'api/editusertext/',
                 'feedback':            'api/feedback/',
                 'flair':               'api/flair/',
                 'flaircsv':            'api/flaircsv/',
                 'flairlist':           'r/%s/api/flairlist/',
                 'flairtemplate':       'api/flairtemplate/',
                 'friend':              'api/friend/',
                 'help':                'help/',
                 'inbox':               'message/inbox/',
                 'info':                'button_info/',
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
                 'undistinguish':       'api/distinguish/no/',
                 'unfriend':            'api/unfriend/',
                 'unmarknsfw':          'api/unmarknsfw/',
                 'unread':              'message/unread/',
                 'unread_message':      'api/unread_message/',
                 'unsave':              'api/unsave/',
                 'user':                'user/%s/',
                 'user_about':          'user/%s/about/',
                 'vote':                'api/vote/'}
    SSL_PATHS = ('login', )

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
        self.comment_limit = int(obj['comment_limit'])
        self.comment_sort = obj['comment_sort']
        self.default_content_limit = int(obj['default_content_limit'])
        self.domain = obj['domain']
        self.gold_comments_max = int(obj['gold_comments_max'])
        self.more_comments_max = int(obj['more_comments_max'])
        self.log_requests = int(obj['log_requests'])
        self.regular_comments_max = int(obj['regular_comments_max'])

        self.oauth_client_id = obj.get('oauth_client_id')
        self.oauth_client_secret = obj.get('oauth_client_secret')
        self.oauth = OAuth2Service(
            name='reddit',
            consumer_key=self.oauth_client_id,
            consumer_secret=self.oauth_client_secret,
            access_token_url='%s/api/v1/access_token' % self._ssl_url,
            authorize_url='%s/api/v1/authorize' % self._ssl_url)

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
        self.is_reddit = obj['domain'] == 'www.reddit.com'

    def __getitem__(self, key):
        """Return the URL for key."""
        if self._ssl_url and key in self.SSL_PATHS:
            return urljoin(self._ssl_url, self.API_PATHS[key])
        return urljoin(self._site_url, self.API_PATHS[key])

    @property
    def short_domain(self):
        """
        Return the short domain of the reddit.

        Used to generate the shortlink. For reddit.com the short_domain is
        redd.it and generate shortlinks like http://redd.it/y3r8u
        """
        if self._short_domain:
            return self._short_domain
        else:
            raise errors.ClientException('No short domain specified.')

    def get_authorize_url(self, scope, state, redirect_uri, refreshable=False):
        """Return the URL to send the user to for OAuth 2 authorization."""
        duration = "permanent" if refreshable else "temporary"
        return self.oauth.get_authorize_url(response_type='code',
                                            scope=scope,
                                            state=state,
                                            redirect_uri=redirect_uri,
                                            duration=duration)

    def get_access_token(self, code, redirect_uri, refreshable=False):
        """Fetch the access token for an OAuth 2 authorization grant."""
        data = dict(grant_type='authorization_code',
                    code=code,
                    redirect_uri=redirect_uri)
        response = self.oauth.get_access_token(
            auth=(self.oauth_client_id, self.oauth_client_secret), data=data)
        if refreshable:
            return (response.content['access_token'],
                    response.content['refresh_token'])
        else:
            return response.content['access_token']

    def refresh_access_token(self, refresh_token, redirect_uri):
        """
        Refresh the access token of a refreshable OAuth 2 authorization grant.
        """
        data = dict(grant_type='refresh_token',
                    refresh_token=refresh_token,
                    redirect_uri=redirect_uri)
        response = self.oauth.get_access_token(
            auth=(self.oauth_client_id, self.oauth_client_secret), data=data)
        return response.content['access_token']


class BaseReddit(object):
    """The base class for a reddit session."""
    DEFAULT_HEADERS = {}
    RETRY_CODES = [502, 503, 504]

    def __init__(self, user_agent, site_name=None, access_token=None,
                 refresh_token=None):
        """
        Initialize our connection with a reddit.

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
        """
        if not user_agent or not isinstance(user_agent, six.string_types):
            raise TypeError('User agent must be a non-empty string.')

        self.access_token = access_token
        self.refresh_token = refresh_token

        self.DEFAULT_HEADERS['User-agent'] = UA_STRING % user_agent
        self.config = Config(site_name or os.getenv('REDDIT_SITE') or 'reddit')

        _cookie_jar = http_cookiejar.CookieJar()
        self._opener = build_opener(HTTPCookieProcessor(_cookie_jar))

        self.modhash = self.user = None

    def __str__(self):
        return 'Open Session (%s)' % (self.user or 'Unauthenticated')

    def _request(self, page_url, params=None, url_data=None, timeout=None):
        """
        Given a page url and a dict of params, open and return the page.

        :param page_url: the url to grab content from.
        :param params: a dictionary containing the extra url data to submit
        :param url_data: a dictionary containing the GET data to put in the url
        :returns: the open page
        """
        # pylint: disable-msg=W0212
        timeout = self.config.timeout if timeout is None else timeout
        remaining_attempts = 3
        while True:
            try:
                return helpers._request(self, page_url, params,
                                        url_data, timeout)
            except HTTPError as error:
                remaining_attempts -= 1
                if (error.code not in self.RETRY_CODES or
                    remaining_attempts == 0):
                    raise
            except http_client.IncompleteRead:
                remaining_attempts -= 1
                if remaining_attempts == 0:
                    raise

    def _json_reddit_objecter(self, json_data):
        """
        Object hook to be used with json.load(s) to spit out RedditObjects
        while decoding.
        """
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

    def get_content(self, page_url, limit=0, url_data=None, place_holder=None,
                    root_field='data', thing_field='children',
                    after_field='after'):
        """
        A generator method to return reddit content from a URL.

        Starts at the initial page_url, and fetches content using the `after`
        JSON data until `limit` entries have been fetched, or the
        `place_holder` has been reached.

        :param page_url: the url to start fetching content from
        :param limit: the maximum number of content entries to fetch. If
            limit <= 0, fetch the default_content_limit for the site. If None,
            then fetch unlimited entries--this would be used in conjunction
            with the place_holder param.
        :param url_data: dictionary containing extra GET data to put in the url
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

        if url_data is None:
            url_data = {}
        if limit is None:
            fetch_all = True
        elif limit <= 0:
            fetch_all = False
            limit = int(self.config.default_content_limit)
        else:
            fetch_all = False

        # While we still need to fetch more content to reach our limit, do so.
        while fetch_all or objects_found < limit:
            page_data = self.request_json(page_url, url_data=url_data)
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
                url_data['after'] = root[after_field]
            else:
                return

    @decorators.parse_api_json_response
    def request_json(self, page_url, params=None, url_data=None,
                     as_objects=True):
        """
        Get the JSON processed from a page.

        Takes the same parameters as the _request method, plus a param to
        control whether objects are returned.

        :param page_url
        :param params
        :param url_data
        :param as_objects: Whether to return constructed reddit objects or the
        raw json dict.
        :returns: JSON processed page
        """
        page_url += '.json'
        response = self._request(page_url, params, url_data)
        if as_objects:
            hook = self._json_reddit_objecter
        else:
            hook = None
        data = json.loads(response.decode('utf-8'), object_hook=hook)
        # Update the modhash
        if self.user and 'data' in data and 'modhash' in data['data']:
            self.modhash = data['data']['modhash']
        return data

    def get_authorize_url(self, scope, state, redirect_uri, refreshable=False):
        """Return the URL to send the user to for OAuth 2 authorization."""
        return self.config.get_authorize_url(scope, state, redirect_uri,
                                             refreshable=refreshable)

    def get_access_token(self, code, redirect_uri, refreshable=False):
        """Fetch the access token for an OAuth 2 authorization grant."""
        result = self.config.get_access_token(code, redirect_uri,
                                              refreshable=refreshable)
        if refreshable:
            self.access_token, self.refresh_token = result
        else:
            self.access_token = result
        return result

    def refresh_access_token(self, redirect_uri):
        """
        Refresh the access token of a refreshable OAuth 2 authorization grant.
        """
        self.access_token = self.config.refresh_access_token(
            self.refresh_token, redirect_uri)


class SubredditExtension(BaseReddit):
    def __init__(self, *args, **kwargs):
        super(SubredditExtension, self).__init__(*args, **kwargs)

    @decorators.require_login
    def _subscribe(self, sr_id=None, sr_name=None, unsubscribe=False):
        """
        (Un)subscribe to the given subreddit.

        Provide either the subreddit id (sr_id) or the name (sr_name).
        """
        if bool(sr_id) == bool(sr_name):
            raise TypeError('One (and only one) of text or url is required!')
        action = 'unsub' if unsubscribe else 'sub'
        params = {'action': action}
        if sr_id:
            params['sr'] = sr_id
        else:
            params['sr_name'] = sr_name

        response = self.request_json(self.config['subscribe'], params)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([self.config['my_reddits']])
        return response

    @decorators.require_login
    @decorators.require_moderator
    def add_flair_template(self, subreddit, text='', css_class='',
                           text_editable=False, is_link=False):
        """Add a flair template to the given subreddit."""
        params = {'r': six.text_type(subreddit),
                  'text': text,
                  'css_class': css_class,
                  'text_editable': six.text_type(text_editable),
                  'flair_type': 'LINK_FLAIR' if is_link else 'USER_FLAIR'}
        return self.request_json(self.config['flairtemplate'], params)

    @decorators.require_login
    @decorators.require_moderator
    def clear_flair_templates(self, subreddit, is_link=False):
        """Clear flair templates for the given subreddit."""
        params = {'r': six.text_type(subreddit),
                  'flair_type': 'LINK_FLAIR' if is_link else 'USER_FLAIR'}
        return self.request_json(self.config['clearflairtemplates'], params)

    def flair_list(self, subreddit, limit=None):
        """
        Return generator of flair mappings.

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
        """Get the list of banned users for the given subreddit."""
        return self.request_json(self.config['banned'] %
                                 six.text_type(subreddit))

    @decorators.require_login
    @decorators.require_moderator
    def get_contributors(self, subreddit):
        """Get the list of contributors for the given subreddit."""
        return self.request_json(self.config['contributors'] %
                                 six.text_type(subreddit))

    def get_flair(self, subreddit, redditor):
        """Gets the flair for a user on the given subreddit."""
        url_data = {'name': six.text_type(redditor)}
        data = self.request_json(self.config['flairlist'] %
                                 six.text_type(subreddit), url_data=url_data)
        return data['users'][0]

    def get_moderators(self, subreddit):
        """Get the list of moderators for the given subreddit."""
        return self.request_json(self.config['moderators'] %
                                 six.text_type(subreddit))

    @decorators.require_login
    @decorators.require_moderator
    def get_modqueue(self, subreddit='mod', limit=None):
        """Get the mod-queue for the given subreddit."""
        return self.get_content(self.config['modqueue'] %
                                six.text_type(subreddit),
                                limit=limit)

    @decorators.require_login
    @decorators.require_moderator
    def get_reports(self, subreddit='mod', limit=None):
        """Get the list of reported submissions for the given subreddit."""
        return self.get_content(self.config['reports'] %
                                six.text_type(subreddit),
                                limit=limit)

    @decorators.require_login
    @decorators.require_moderator
    def get_settings(self, subreddit):
        """Get the settings for the given subreddit."""
        return self.request_json(self.config['subreddit_settings'] %
                                 six.text_type(subreddit))['data']

    @decorators.require_login
    @decorators.require_moderator
    def get_spam(self, subreddit='mod', limit=None):
        """Get the list of spam-filtered items for the given subreddit."""
        return self.get_content(self.config['spam'] % six.text_type(subreddit),
                                limit=limit)

    @decorators.require_login
    @decorators.require_moderator
    def get_stylesheet(self, subreddit):
        """Get the stylesheet and associated images for the given subreddit."""
        return self.request_json(self.config['stylesheet'] %
                                 six.text_type(subreddit))['data']

    @decorators.require_login
    @decorators.require_moderator
    def set_flair(self, subreddit, item, flair_text='', flair_css_class=''):
        """
        Set flair for the user in the given subreddit.

        Item can be a string, Redditor object, or Submission object. If item is
        a string it will be treated as the name of a Redditor.
        """
        params = {'r': six.text_type(subreddit),
                  'text': flair_text or '',
                  'css_class': flair_css_class or ''}
        if isinstance(item, objects.Submission):
            params['link'] = item.content_id
            evict = item.permalink
        else:
            params['name'] = six.text_type(item)
            evict = self.config['flairlist'] % six.text_type(subreddit)
        response = self.request_json(self.config['flair'], params)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([evict])
        return response

    @decorators.require_login
    @decorators.require_moderator
    def set_flair_csv(self, subreddit, flair_mapping):
        """
        Set flair for a group of users in the given subreddit.

        flair_mapping should be a list of dictionaries with the following keys:
          user: the user name
          flair_text: the flair text for the user (optional)
          flair_css_class: the flair css class for the user (optional)
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
            params = {'r': six.text_type(subreddit),
                      'flair_csv': '\n'.join(lines[:100])}
            response.extend(self.request_json(self.config['flaircsv'], params))
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
        """Set the settings for the given subreddit."""

        # Temporary support for no longer valid entries
        if wiki_edit_age is None:
            wiki_edit_age = ''
        if wiki_edit_karma is None:
            wiki_edit_karma = ''

        params = {'r': six.text_type(subreddit),
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
            params['prev_description_id'] = prev_description_id
        if prev_public_description_id is not None:
            params['prev_public_description_id'] = prev_public_description_id
        if kwargs:
            msg = 'Extra settings fields: {0}'.format(kwargs.keys())
            warn_explicit(msg, UserWarning, '', 0)
            params.update(kwargs)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([self.config['subreddit_settings'] %
                                six.text_type(subreddit)])
        return self.request_json(self.config['site_admin'], params)

    @decorators.require_login
    @decorators.require_moderator
    def set_stylesheet(self, subreddit, stylesheet, prevstyle=None):
        """Set stylesheet for the given subreddit."""
        params = {'r': six.text_type(subreddit),
                  'stylesheet_contents': stylesheet,
                  'op': 'save'}  # Options: save / preview
        if prevstyle is not None:
            params['prevstyle'] = prevstyle
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([self.config['stylesheet'] %
                                six.text_type(subreddit)])
        return self.request_json(self.config['subreddit_css'], params)

    @decorators.require_login
    @decorators.RequireCaptcha
    def submit(self, subreddit, title, text=None, url=None, captcha=None):
        """
        Submit a new link to the given subreddit.

        Accepts either a Subreddit object or a str containing the subreddit's
        display name.
        """
        if bool(text) == bool(url):
            raise TypeError('One (and only one) of text or url is required!')
        params = {'sr': six.text_type(subreddit),
                  'title': title}
        if text:
            params['kind'] = 'self'
            params['text'] = text
        else:
            params['kind'] = 'link'
            params['url'] = url
        if captcha:
            params.update(captcha)
        result = self.request_json(self.config['submit'], params)
        # pylint: disable-msg=E1101
        return self.get_submission(result['data']['url'])

    def subscribe(self, subreddit):
        """Subscribe to the given subreddit by display name."""
        self._subscribe(sr_name=subreddit)

    def unsubscribe(self, subreddit):
        """Unsubscribe from the given subreddit by display name."""
        self._subscribe(sr_name=subreddit, unsubscribe=True)

    def update_settings(self, subreddit, **kwargs):
        """
        Update only the given settings for the given subreddit.

        The settings to update must be given by keyword and match one of the
        parameter names in `set_settings`.
        """
        settings = self.get_settings(subreddit)
        settings.update(kwargs)
        del settings['subreddit_id']
        return self.set_settings(subreddit, **settings)


class LoggedInExtension(BaseReddit):
    def __init__(self, *args, **kwargs):
        super(LoggedInExtension, self).__init__(*args, **kwargs)

    @decorators.require_login
    def _add_comment(self, thing_id, text):
        """Comment on the given thing with the given text."""
        params = {'thing_id': thing_id,
                  'text': text}
        data = self.request_json(self.config['comment'], params)
        # REDDIT: reddit's end should only ever return a single comment
        return data['data']['things'][0]

    @decorators.require_login
    def _mark_as_read(self, thing_ids, unread=False):
        """Mark each of the supplied thing_ids as (un)read."""
        params = {'id': ','.join(thing_ids)}
        key = 'unread_message' if unread else 'read_message'
        response = self.request_json(self.config[key], params)
        urls = [self.config[x] for x in ['inbox', 'moderator', 'unread']]
        helpers._request.evict(urls)  # pylint: disable-msg=E1101,W0212
        return response

    @decorators.require_login
    @decorators.RequireCaptcha
    def compose_message(self, recipient, subject, message, captcha=None):
        """
        Send a message to another redditor or a subreddit (mod mail).

        Depreciated. compose_message has been renamed to send_message and will
        be removed in a future version.
        """
        # Remove around the end of 2012
        warn('compose_message has been renamed to send_message and will be '
             'removed in a future version. Please update.', DeprecationWarning)
        return self.send_message(recipient, subject, message, captcha)

    @decorators.require_login
    def create_subreddit(self, name, title, description='', language='en',
                         subreddit_type='public', content_options='any',
                         over_18=False, default_set=True, show_media=False,
                         domain='', wikimode='disabled'):
        """Create a new subreddit."""
        params = {'name': name,
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
        return self.request_json(self.config['site_admin'], params)

    def get_redditor(self, user_name, *args, **kwargs):
        """Return a Redditor instance for the user_name specified."""
        return objects.Redditor(self, user_name, *args, **kwargs)

    @decorators.require_login
    def get_saved_links(self, limit=0):
        """Return a listing of the logged-in user's saved links."""
        return self.get_content(self.config['saved'], limit=limit)

    def login(self, username=None, password=None):
        """
        Login to a reddit site.

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

        params = {'passwd': pswd,
                  'user': user}
        response = self.request_json(self.config['login'], params)
        self.modhash = response['data']['modhash']
        self.user = self.get_redditor(user)
        self.user.__class__ = objects.LoggedInRedditor

    @decorators.require_login
    @decorators.RequireCaptcha
    def send_message(self, recipient, subject, message, captcha=None):
        """
        Send a message to another redditor or a subreddit (mod mail).

        When sending a message to a subreddit the recipient paramater must
        either be a subreddit object or the subreddit name needs to be prefixed
        with either '/r/' or '#'.
        """
        if isinstance(recipient, objects.Subreddit):
            recipient = '/r/%s' % six.text_type(recipient)
        else:
            recipient = six.text_type(recipient)

        params = {'text': message,
                  'subject': subject,
                  'to': recipient}
        if captcha:
            params.update(captcha)
        response = self.request_json(self.config['compose'], params)
        # pylint: disable-msg=E1101,W0212
        helpers._request.evict([self.config['sent']])
        return response


class Reddit(LoggedInExtension,  # pylint: disable-msg=R0904
             SubredditExtension):
    def __init__(self, *args, **kwargs):
        super(Reddit, self).__init__(*args, **kwargs)

    @decorators.RequireCaptcha
    def create_redditor(self, user_name, password, email='', captcha=None):
        """Register a new user."""
        params = {'email': email,
                  'passwd': password,
                  'passwd2': password,
                  'user': user_name}
        if captcha:
            params.update(captcha)
        return self.request_json(self.config['register'], params)

    def get_all_comments(self, *args, **kwargs):
        """Return all comments."""
        return self.get_content(self.config['comments'], *args, **kwargs)

    def get_controversial(self, *args, **kwargs):
        """Return controversial page."""
        return self.get_content(self.config['controversial'], *args, **kwargs)

    def get_front_page(self, *args, **kwargs):
        """
        Return the front page submissions.

        Default front page if not logged in, otherwise get logged in redditor's
        front page.
        """
        return self.get_content(self.config['reddit_url'], *args, **kwargs)

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

    def get_submission(self, url=None, submission_id=None):
        """Return a Submission object for the given url or submission_id."""
        if bool(url) == bool(submission_id):
            raise TypeError('One (and only one) of id or url is required!')
        if submission_id:
            url = urljoin(self.config['comments'], submission_id)
        return objects.Submission.get_info(self, url)

    def get_subreddit(self, subreddit_name, *args, **kwargs):
        """Return a Subreddit object for the subreddit_name specified."""
        return objects.Subreddit(self, subreddit_name, *args, **kwargs)

    def info(self, url=None, thing_id=None, limit=0):
        """
        Given url, queries the API to see if the given URL has been submitted
        already, and if it has, return the submissions.

        Given a thing_id, requests the info for that thing.
        """
        if bool(url) == bool(thing_id):
            raise TypeError('Only one of url or thing_id is required!')
        if url is not None:
            url_data = {'url': url}
            if (url.startswith(self.config['reddit_url']) and
                url != self.config['reddit_url']):
                msg = ('It looks like you may be trying to get the info of a '
                       'self or internal link. This probably will not return '
                       'any useful results!')
                warn_explicit(msg, UserWarning, '', 0)
        else:
            url_data = {'id': thing_id}
        return self.get_content(self.config['info'], url_data=url_data,
                                limit=limit)

    def search(self, query, subreddit=None, sort=None, limit=0, *args,
               **kwargs):
        """Return submissions whose title contains the query phrase."""
        url_data = {'q': query}
        if sort:
            url_data['sort'] = sort
        if subreddit:
            url_data['restrict_sr'] = 'on'
            url = self.config['search'] % subreddit
        else:
            url = self.config['search'] % 'all'
        return self.get_content(url, url_data=url_data, limit=limit, *args,
                                **kwargs)

    def search_reddit_names(self, query):
        """Return subreddits whose display name contains the query."""
        params = {'query': query}
        results = self.request_json(self.config['search_reddit_names'], params)
        return [self.get_subreddit(name) for name in results['names']]

    @decorators.RequireCaptcha
    def send_feedback(self, name, email, message, reason='feedback',
                      captcha=None):
        """
        Send feedback to the admins.

        Please don't abuse this. Read the send feedback page before use.
        """
        params = {'name': name,
                  'email': email,
                  'reason': reason,
                  'text': message}
        if captcha:
            params.update(captcha)
        return self.request_json(self.config['feedback'], params)
