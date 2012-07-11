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

import reddit.backport  # pylint: disable-msg=W0611
from six.moves import (HTTPCookieProcessor, HTTPError, build_opener,
                       http_cookiejar, http_client, urljoin)

import json
import os
import platform
import six
import sys
import warnings

import reddit.decorators
import reddit.errors
import reddit.helpers
import reddit.objects
from reddit.settings import CONFIG

__version__ = '1.4.0'
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
                 'login':               'api/login/%s/',
                 'moderator':           'message/moderator/',
                 'moderators':          'r/%s/about/moderators/',
                 'modqueue':            'r/%s/about/modqueue/',
                 'morechildren':        'api/morechildren/',
                 'my_mod_reddits':      'reddits/mine/moderator/',
                 'my_reddits':          'reddits/mine/',
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
                 'undistinguish':       'api/distinguish/no/',
                 'unfriend':            'api/unfriend/',
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
        self.api_request_delay = float(obj['api_request_delay'])
        self.by_kind = {obj['comment_kind']:    reddit.objects.Comment,
                        obj['message_kind']:    reddit.objects.Message,
                        obj['redditor_kind']:   reddit.objects.Redditor,
                        obj['submission_kind']: reddit.objects.Submission,
                        obj['subreddit_kind']:  reddit.objects.Subreddit,
                        'more':                 reddit.objects.MoreComments,
                        'UserList':             reddit.objects.UserList}
        self.by_object = dict((value, key) for (key, value) in
                              six.iteritems(self.by_kind))
        self.by_object[reddit.objects.LoggedInRedditor] = obj['redditor_kind']
        self.cache_timeout = float(obj['cache_timeout'])
        self.comment_limit = int(obj['comment_limit'])
        self.comment_sort = obj['comment_sort']
        self.default_content_limit = int(obj['default_content_limit'])
        self.domain = obj['domain']
        self.more_comments_max = int(obj['more_comments_max'])
        if 'short_domain' in obj:
            self._short_domain = 'http://' + obj['short_domain']
        else:
            self._short_domain = None
        self.timeout = float(obj['timeout'])
        try:
            self.user = obj['user']
            self.pswd = obj['pswd']
        except KeyError:
            self.user = self.pswd = None
        self.is_reddit = obj['domain'] == 'www.reddit.com'

    def __getitem__(self, key):
        """Return the URL for key"""
        if self._ssl_url and key in self.SSL_PATHS:
            return urljoin(self._ssl_url, self.API_PATHS[key])
        return urljoin(self._site_url, self.API_PATHS[key])

    @property
    def short_domain(self):
        if self._short_domain:
            return self._short_domain
        else:
            raise reddit.errors.ClientException('No short domain specified.')


class BaseReddit(object):
    """The base class for a reddit session."""
    DEFAULT_HEADERS = {}
    RETRY_CODES = [502, 503, 504]

    def __init__(self, user_agent, site_name=None):
        """
        Specify the user agent for the application and optionally a site_name.

        If site_name is None, then the site name will be looked for in the
        environment variable REDDIT_SITE. It if is not found there, the default
        site name `reddit` will be used.
        """

        if not user_agent or not isinstance(user_agent, six.string_types):
            raise TypeError('User agent must be a non-empty string.')

        self.DEFAULT_HEADERS['User-agent'] = UA_STRING % user_agent
        self.config = Config(site_name or os.getenv('REDDIT_SITE') or 'reddit')

        _cookie_jar = http_cookiejar.CookieJar()
        self._opener = build_opener(HTTPCookieProcessor(_cookie_jar))

        self.modhash = self.user = None

    def __str__(self):
        return 'Open Session (%s)' % (self.user or 'Unauthenticated')

    def _request(self, page_url, params=None, url_data=None, timeout=None):
        """Given a page url and a dict of params, opens and returns the page.

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
                return reddit.helpers._request(self, page_url, params,
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
                    warnings.warn_explicit('Unknown object type: %s' %
                                           json_data, UserWarning, '', 0)
                return json_data['json']
        else:
            return object_class.from_api_response(self, json_data['data'])
        return json_data

    def get_content(self, page_url, limit=0, url_data=None, place_holder=None,
                    root_field='data', thing_field='children',
                    after_field='after'):
        """A generator method to return Reddit content from a URL. Starts at
        the initial page_url, and fetches content using the `after` JSON data
        until `limit` entries have been fetched, or the `place_holder` has been
        reached.

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
        :type place_holder: a string corresponding to a Reddit content id, e.g.
            't3_asdfasdf'
        :returns: a list of Reddit content, of type Subreddit, Comment,
            Submission or user flair.
        """
        content_found = 0

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
        while fetch_all or content_found < limit:
            page_data = self.request_json(page_url, url_data=url_data)
            if root_field:
                root = page_data[root_field]
            else:
                root = page_data
            for thing in root[thing_field]:
                yield thing
                content_found += 1
                # Terminate when we reached the limit, or place holder
                if (content_found == limit or
                    place_holder and thing.id == place_holder):
                    return
            # Set/update the 'after' parameter for the next iteration
            if after_field in root and root[after_field]:
                url_data['after'] = root[after_field]
            else:
                return

    @reddit.decorators.parse_api_json_response
    def request_json(self, page_url, params=None, url_data=None,
                     as_objects=True):
        """Gets the JSON processed from a page. Takes the same parameters as
        the _request method, plus a param to control whether objects are
        returned.

        :param page_url
        :param params
        :param url_data
        :param as_objects: Whether to return constructed Reddit objects or the
        raw json dict.
        :returns: JSON processed page
        """
        page_url += '.json'
        response = self._request(page_url, params, url_data)
        if as_objects:
            hook = self._json_reddit_objecter
        else:
            hook = None
        return json.loads(response.decode('utf-8'), object_hook=hook)


class SubredditExtension(BaseReddit):
    def __init__(self, *args, **kwargs):
        super(SubredditExtension, self).__init__(*args, **kwargs)

    @reddit.decorators.require_login
    def _subscribe(self, sr_id=None, sr_name=None, unsubscribe=False):
        """Perform the (un)subscribe to the given subreddit.

        Provide either the subreddit id (sr_id) name (sr_name)."""

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
        reddit.helpers._request.evict([self.config['my_reddits']])
        return response

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def add_flair_template(self, subreddit, text='', css_class='',
                           text_editable=False, is_link=False):
        """Adds a flair template to the given subreddit."""
        params = {'r': six.text_type(subreddit),
                  'text': text,
                  'css_class': css_class,
                  'text_editable': six.text_type(text_editable),
                  'flair_type': 'LINK_FLAIR' if is_link else 'USER_FLAIR'}
        return self.request_json(self.config['flairtemplate'], params)

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def clear_flair_templates(self, subreddit, is_link=False):
        """Clear flair templates for the given subreddit."""
        params = {'r': six.text_type(subreddit),
                  'flair_type': 'LINK_FLAIR' if is_link else 'USER_FLAIR'}
        return self.request_json(self.config['clearflairtemplates'], params)

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def flair_list(self, subreddit, limit=None):
        """Get flair list for the given subreddit.

        Returns a tuple containing 'user', 'flair_text', and 'flair_css_class'.
        """
        return self.get_content(self.config['flairlist'] %
                                six.text_type(subreddit),
                                limit=limit, root_field=None,
                                thing_field='users', after_field='next')

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def get_banned(self, subreddit):
        """Get the list of banned users for the given subreddit."""
        return self.request_json(self.config['banned'] %
                                 six.text_type(subreddit))

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def get_settings(self, subreddit):
        """Get the settings for the given subreddit."""
        return self.request_json(self.config['subreddit_settings'] %
                                 six.text_type(subreddit))['data']

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def get_contributors(self, subreddit):
        """Get the list of contributors for the given subreddit."""
        return self.request_json(self.config['contributors'] %
                                 six.text_type(subreddit))

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def get_flair(self, subreddit, redditor):
        """Gets the flair for a user on the given subreddit."""
        url_data = {'name': six.text_type(redditor)}
        data = self.request_json(self.config['flairlist'] %
                                 six.text_type(subreddit), url_data=url_data)
        return data['users'][0]

    @reddit.decorators.require_login
    def get_moderators(self, subreddit):
        """Get the list of moderators for the given subreddit."""
        return self.request_json(self.config['moderators'] %
                                 six.text_type(subreddit))

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def get_modqueue(self, subreddit='mod', limit=None):
        """Get the mod-queue for the given subreddit."""
        return self.get_content(self.config['modqueue'] %
                                six.text_type(subreddit),
                                limit=limit)

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def get_reports(self, subreddit='mod', limit=None):
        """Get the list of reported submissions for the given subreddit."""
        return self.get_content(self.config['reports'] %
                                six.text_type(subreddit),
                                limit=limit)

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def get_spam(self, subreddit='mod', limit=None):
        """Get the list of spam-filtered items for the given subreddit."""
        return self.get_content(self.config['spam'] % six.text_type(subreddit),
                                limit=limit)

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def get_stylesheet(self, subreddit):
        """Get the stylesheet and associated images for the given subreddit."""
        return self.request_json(self.config['stylesheet'] %
                                 six.text_type(subreddit))['data']

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def set_flair(self, subreddit, item, flair_text='', flair_css_class=''):
        """Set flair for the user in the given subreddit.

        Item can be a string, Redditor object, or Submission object. If item is
        a string it will be treated as a Redditor.
        """
        params = {'r': six.text_type(subreddit),
                  'text': flair_text or '',
                  'css_class': flair_css_class or ''}
        if isinstance(item, reddit.objects.Submission):
            params['link'] = item.content_id
            evict = item.permalink
        else:
            params['name'] = six.text_type(item)
            evict = self.config['flairlist'] % six.text_type(subreddit)
        response = self.request_json(self.config['flair'], params)
        # pylint: disable-msg=E1101,W0212
        reddit.helpers._request.evict([evict])
        return response

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def set_flair_csv(self, subreddit, flair_mapping):
        """Set flair for a group of users in the given subreddit.

        flair_mapping should be a list of dictionaries with the following keys:
          user: the user name
          flair_text: the flair text for the user (optional)
          flair_css_class: the flair css class for the user (optional)
        """
        if not flair_mapping:
            raise reddit.errors.ClientException('flair_mapping must be set')
        item_order = ['user', 'flair_text', 'flair_css_class']
        lines = []
        for mapping in flair_mapping:
            if 'user' not in mapping:
                raise reddit.errors.ClientException('flair_mapping must '
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
        reddit.helpers._request.evict([stale_url])
        return response

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def set_settings(self, subreddit, title, public_description='',
                     description='', language='en', subreddit_type='public',
                     content_options='any', over_18=False, default_set=True,
                     show_media=False, domain='', domain_css=False,
                     domain_sidebar=False, header_hover_text=''):
        def bool_str(item):
            return 'on' if item else 'off'

        """Set the settings for the given subreddit."""
        params = {'r': six.text_type(subreddit),
                  'sr': subreddit.content_id,
                  'title': title,
                  'public_description': public_description,
                  'description': description,
                  'lang': language,
                  'type': subreddit_type,
                  'link_type': content_options,
                  'over_18': bool_str(over_18),
                  'allow_top': bool_str(default_set),
                  'show_media': bool_str(show_media),
                  'domain': domain or '',
                  'domain_css': bool_str(domain_css),
                  'domain_sidebar': bool_str(domain_sidebar),
                  'header-title': header_hover_text or ''}
        # pylint: disable-msg=E1101,W0212
        reddit.helpers._request.evict([self.config['subreddit_settings'] %
                                       six.text_type(subreddit)])
        return self.request_json(self.config['site_admin'], params)

    @reddit.decorators.require_login
    @reddit.decorators.require_moderator
    def set_stylesheet(self, subreddit, stylesheet):
        """Set stylesheet for the given subreddit."""
        params = {'r': six.text_type(subreddit),
                  'stylesheet_contents': stylesheet,
                  'op': 'save'}  # Options: save / preview
        return self.request_json(self.config['subreddit_css'], params)

    @reddit.decorators.require_login
    @reddit.decorators.RequireCaptcha
    def submit(self, subreddit, title, text=None, url=None, captcha=None):
        """
        Submit a new link to the given subreddit.

        Accepts either a Subreddit object or a str containing the subreddit
        name.
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
        """Subscribe to the given subreddit by name."""
        self._subscribe(sr_name=subreddit)

    def unsubscribe(self, subreddit):
        """Unsubscribe from the given subreddit by name."""
        self._subscribe(sr_name=subreddit, unsubscribe=True)

    def update_settings(self, subreddit, **kwargs):
        """Update only the given settings for the given subreddit.

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

    @reddit.decorators.require_login
    def _add_comment(self, thing_id, text):
        """Comment on the given thing with the given text."""
        params = {'thing_id': thing_id,
                  'text': text}
        data = self.request_json(self.config['comment'], params)
        # REDDIT: Reddit's end should only ever return a single comment
        return data['data']['things'][0]

    @reddit.decorators.require_login
    def _mark_as_read(self, thing_ids, unread=False):
        """ Marks each of the supplied thing_ids as (un)read."""
        params = {'id': ','.join(thing_ids)}
        key = 'unread_message' if unread else 'read_message'
        response = self.request_json(self.config[key], params)
        urls = [self.config[x] for x in ['inbox', 'moderator', 'unread']]
        # pylint: disable-msg=E1101,W0212
        reddit.helpers._request.evict(urls)
        return response

    @reddit.decorators.require_login
    @reddit.decorators.RequireCaptcha
    def compose_message(self, recipient, subject, message, captcha=None):
        """Send a message to another redditor or a subreddit.

        When sending a message to a subreddit the recipient paramater must
        either be a subreddit object or the subreddit name needs to be prefixed
        with either '/r/' or '#'.
        """
        if isinstance(recipient, reddit.objects.Subreddit):
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
        reddit.helpers._request.evict([self.config['sent']])
        return response

    @reddit.decorators.require_login
    def create_subreddit(self, name, title, description='', language='en',
                         subreddit_type='public', content_options='any',
                         over_18=False, default_set=True, show_media=False,
                         domain=''):
        """Create a new subreddit"""
        params = {'name': name,
                  'title': title,
                  'description': description,
                  'lang': language,
                  'type': subreddit_type,
                  'link_type': content_options,
                  'over_18': 'on' if over_18 else 'off',
                  'allow_top': 'on' if default_set else 'off',
                  'show_media': 'on' if show_media else 'off',
                  'domain': domain}
        return self.request_json(self.config['site_admin'], params)

    def get_redditor(self, user_name, *args, **kwargs):
        """Returns a Redditor class for the user_name specified."""
        return reddit.objects.Redditor(self, user_name, *args, **kwargs)

    @reddit.decorators.require_login
    def get_saved_links(self, limit=0):
        """Return a listing of the logged-in user's saved links."""
        return self.get_content(self.config['saved'], limit=limit)

    def login(self, username=None, password=None):
        """Login to Reddit.

        If no user or password is provided, the settings file will be checked,
        and finally the user will be prompted with raw_input and
        getpass.getpass. If username was explicitly provided and password was
        not, then we must ask for the password unless the username matches
        what's provided in the config file."""
        if password and not username:
            raise Exception('Username must be provided when password is.')
        user = username or self.config.user
        if not user:
            sys.stdout.write('Username: ')
            sys.stdout.flush()
            user = sys.stdin.readline().strip()
        if username and username == self.config.user:
            pswd = password or self.config.pswd
        elif not username and self.config.user:
            pswd = self.config.pswd
        else:
            import getpass
            pswd = password or getpass.getpass('Password for %s: ' % user)

        params = {'passwd': pswd,
                  'user': user}
        response = self.request_json(self.config['login'] % user, params)
        self.modhash = response['data']['modhash']
        self.user = self.get_redditor(user)
        self.user.__class__ = reddit.objects.LoggedInRedditor


class Reddit(LoggedInExtension,  # pylint: disable-msg=R0904
             SubredditExtension):
    def __init__(self, *args, **kwargs):
        super(Reddit, self).__init__(*args, **kwargs)

    @reddit.decorators.RequireCaptcha
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
        """Returns a listing from reddit.com/comments (which provides all of
        the most recent comments from all users to all submissions)."""
        return self.get_content(self.config['comments'], *args, **kwargs)

    def get_front_page(self, limit=0):
        """Return the reddit front page. Login isn't required, but you'll only
        see your own front page if you are logged in."""
        return self.get_content(self.config['reddit_url'], limit=limit)

    def get_submission(self, url=None, submission_id=None):
        """Returns a Submission object for the given url or submission_id."""
        if bool(url) == bool(submission_id):
            raise TypeError('One (and only one) of id or url is required!')
        if submission_id:
            url = urljoin(self.config['comments'], submission_id)
        return reddit.objects.Submission.get_info(self, url)

    def get_subreddit(self, subreddit_name, *args, **kwargs):
        """Returns a Subreddit object for the subreddit_name specified."""
        return reddit.objects.Subreddit(self, subreddit_name, *args, **kwargs)

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
                warnings.warn_explicit(msg, UserWarning, '', 0)
        else:
            url_data = {'id': thing_id}
        return self.get_content(self.config['info'], url_data=url_data,
                                limit=limit)

    def search(self, query, subreddit=None, sort=None, limit=0, *args,
               **kwargs):
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
        """Search the subreddits for a reddit whose name matches the query."""
        params = {'query': query}
        results = self.request_json(self.config['search_reddit_names'], params)
        return [self.get_subreddit(name) for name in results['names']]

    @reddit.decorators.RequireCaptcha
    def send_feedback(self, name, email, message, reason='feedback',
                      captcha=None):
        """
        Send feedback to the admins. Please don't abuse this, read what it says
        on the send feedback page!
        """
        params = {'name': name,
                  'email': email,
                  'reason': reason,
                  'text': message}
        if captcha:
            params.update(captcha)
        return self.request_json(self.config['feedback'], params)
