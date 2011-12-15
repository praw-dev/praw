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

import cookielib
import os
import warnings
import urllib2
import urlparse
try:
    import json
except ImportError:
    import simplejson as json

import reddit.decorators
import reddit.errors
import reddit.helpers
import reddit.objects

from reddit.settings import CONFIG


class Config(object):  # pylint: disable-msg=R0903
    """A class containing the configuration for a reddit site."""
    API_PATHS = {'banned':              'r/%s/about/banned',
                 'captcha':             'captcha/',
                 'clearflairtemplates': 'api/clearflairtemplates/',
                 'comment':             'api/comment/',
                 'comments':            'comments/',
                 'compose':             'api/compose/',
                 'contributors':        'r/%s/about/contributors',
                 'del':                 'api/del/',
                 'feedback':            'api/feedback/',
                 'flair':               'api/flair/',
                 'flaircsv':            'api/flaircsv/',
                 'flairlist':           'r/%s/api/flairlist/',
                 'flairtemplate':       'api/flairtemplate',
                 'friend':              'api/friend/',
                 'help':                'help/',
                 'inbox':               'message/inbox/',
                 'info':                'button_info/',
                 'login':               'api/login/%s/',
                 'logout':              'logout/',
                 'moderator':           'message/moderator/',
                 'moderators':          'r/%s/about/moderators',
                 'my_mod_reddits':      'reddits/mine/moderator/',
                 'my_reddits':          'reddits/mine/',
                 'new_captcha':         'api/new_captcha/',
                 'read_message':        'api/read_message/',
                 'reddit_url':          '/',
                 'register':            'api/register/',
                 'report':              'api/report/',
                 'reports':             'r/%s/about/reports/',
                 'save':                'api/save/',
                 'saved':               'saved/',
                 'search_reddit_names': 'api/search_reddit_names/',
                 'sent':                'message/sent/',
                 'site_admin':          'api/site_admin/',
                 'submit':              'api/submit/',
                 'subreddit':           'r/%s/',
                 'subreddit_about':     'r/%s/about/',
                 'subscribe':           'api/subscribe/',
                 'unfriend':            'api/unfriend/',
                 'unread':              'message/unread/',
                 'unsave':              'api/unsave/',
                 'user':                'user/%s/',
                 'user_about':          'user/%s/about/',
                 'vote':                'api/vote/'}

    def __init__(self, site_name):
        obj = dict(CONFIG.items(site_name))
        self._site_url = 'http://' + obj['domain']
        self.api_request_delay = float(obj['api_request_delay'])
        self.by_kind = {obj['comment_kind']:    reddit.objects.Comment,
                        obj['message_kind']:    reddit.objects.Message,
                        obj['more_kind']:       reddit.objects.MoreComments,
                        obj['redditor_kind']:   reddit.objects.Redditor,
                        obj['submission_kind']: reddit.objects.Submission,
                        obj['subreddit_kind']:  reddit.objects.Subreddit,
                        obj['userlist_kind']:   reddit.objects.UserList}
        self.by_object = dict((value, key) for (key, value) in
                              self.by_kind.items())
        self.by_object[reddit.objects.LoggedInRedditor] = obj['redditor_kind']
        self.cache_timeout = float(obj['cache_timeout'])
        self.default_content_limit = int(obj['default_content_limit'])
        self.domain = obj['domain']
        try:
            self.user = obj['user']
            self.pswd = obj['pswd']
        except KeyError:
            self.user = self.pswd = None
        self.is_reddit = obj['domain'] == 'www.reddit.com'

    def __getitem__(self, key):
        """Return the URL for key"""
        return urlparse.urljoin(self._site_url, self.API_PATHS[key])


class BaseReddit(object):
    """The base class for a reddit session."""
    DEFAULT_HEADERS = {}

    def __init__(self, user_agent, site_name=None):
        """
        Specify the user agent for the application and optionally a site_name.

        If site_name is None, then the site name will be looked for in the
        environment variable REDDIT_SITE. It if is not found there, the default
        site name `reddit` will be used.
        """

        if not isinstance(user_agent, str):
            raise TypeError('User agent must be a string.')
        self.DEFAULT_HEADERS['User-agent'] = user_agent
        self.config = Config(site_name or os.getenv('REDDIT_SITE') or 'reddit')

        _cookie_jar = cookielib.CookieJar()
        self._opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(_cookie_jar))

        self.modhash = self.user = None

    def __str__(self):
        return 'Open Session (%s)' % (self.user or 'Unauthenticated')

    def _request(self, page_url, params=None, url_data=None):
        """Given a page url and a dict of params, opens and returns the page.

        :param page_url: the url to grab content from.
        :param params: the extra url data to submit
        :param url_data: the GET data to put in the url
        :returns: the open page
        """
        # pylint: disable-msg=W0212
        return reddit.helpers._request(self, page_url, params, url_data)

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
                    warnings.warn('Unknown object type: %s' % json_data)
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
        :param url_data: extra GET data to put in the url
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
        if not page_url.endswith('.json'):
            page_url += '.json'
        response = self._request(page_url, params, url_data)
        if as_objects:
            hook = self._json_reddit_objecter
        else:
            hook = None
        return json.loads(response, object_hook=hook)


class SubredditExtension(BaseReddit):
    def __init__(self, *args, **kwargs):
        super(SubredditExtension, self).__init__(*args, **kwargs)

    @reddit.decorators.require_login
    def add_flair_template(self, subreddit, text, css_class, text_editable):
        """Adds a flair template to the subreddit."""
        params = {'r': str(subreddit),
                  'text': text,
                  'css_class': css_class,
                  'text_editable': str(text_editable),
                  'uh': self.user.modhash,
                  'api_type': 'json'}
        return self.request_json(self.config['flairtemplate'], params)

    @reddit.decorators.require_login
    def clear_flair_templates(self, subreddit):
        """Clear flair templates for a subreddit."""
        params = {'r': str(subreddit),
                  'uh': self.user.modhash,
                  'api_type': 'json'}
        return self.request_json(self.config['clearflairtemplates'], params)

    @reddit.decorators.require_login
    def get_banned(self, subreddit):
        """Get the list of banned users for a subreddit."""
        return self.request_json(self.config['banned'] % str(subreddit))

    @reddit.decorators.require_login
    def get_contributors(self, subreddit):
        """Get the list of contributors for a subreddit."""
        return self.request_json(self.config['contributors'] % str(subreddit))

    @reddit.decorators.require_login
    def get_moderators(self, subreddit):
        """Get the list of moderators for a subreddit."""
        return self.request_json(self.config['moderators'] % str(subreddit))
        
    @reddit.decorators.require_login
    def get_reports(self, subreddit, limit=None):
        """Get the list of reported submissions for a subreddit."""
        return self.get_content(self.config['reports'] % str(subreddit),
                                limit=limit, url_data={'uh':self.user.modhash})

    @reddit.decorators.require_login
    def flair_list(self, subreddit, limit=None):
        """Get flair list for a subreddit.

        Returns a tuple containing 'user', 'flair_text', and 'flair_css_class'.
        """
        params = {'uh': self.user.modhash}
        return self.get_content(self.config['flairlist'] % str(subreddit),
                                limit=limit, url_data=params, root_field=None,
                                thing_field='users', after_field='next')

    @reddit.decorators.require_login
    def set_flair(self, subreddit, user, text='', css_class=''):
        """Set flair of user in given subreddit."""
        params = {'r': str(subreddit),
                  'name': str(user),
                  'text': text,
                  'css_class': css_class,
                  'uh': self.user.modhash,
                  'api_type': 'json'}
        response = self.request_json(self.config['flair'], params)
        stale_url = self.config['flairlist'] % str(subreddit)
        # pylint: disable-msg=E1101,W0212
        reddit.helpers._request.is_stale([stale_url])
        return response

    @reddit.decorators.require_login
    def set_flair_csv(self, subreddit, flair_mapping):
        """Set flair for a group of users all at once.

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
        params = {'r': str(subreddit),
                  'flair_csv': '\n'.join(lines),
                  'uh': self.user.modhash,
                  'api_type': 'json'}
        response = self.request_json(self.config['flaircsv'], params)
        stale_url = self.config['flairlist'] % str(subreddit)
        # pylint: disable-msg=E1101,W0212
        reddit.helpers._request.is_stale([stale_url])
        return response

    @reddit.decorators.RequireCaptcha
    @reddit.decorators.require_login
    def submit(self, subreddit, title, text=None, url=None, captcha=None):
        """
        Submit a new link.

        Accepts either a Subreddit object or a str containing the subreddit
        name.
        """
        if bool(text) == bool(url):
            raise TypeError('One (and only one) of text or url is required!')
        params = {'sr': str(subreddit),
                  'title': title,
                  'uh': self.modhash,
                  'api_type': 'json'}
        if text:
            params['kind'] = 'self'
            params['text'] = text
        else:
            params['kind'] = 'link'
            params['url'] = url
        if captcha:
            params.update(captcha)
        return self.request_json(self.config['submit'], params)


class LoggedInExtension(BaseReddit):
    def __init__(self, *args, **kwargs):
        super(LoggedInExtension, self).__init__(*args, **kwargs)

    @reddit.decorators.require_login
    def _add_comment(self, thing_id, text):
        """Comment on the given thing with the given text."""
        params = {'thing_id': thing_id,
                  'text': text,
                  'uh': self.modhash,
                  'api_type': 'json'}
        return self.request_json(self.config['comment'], params)

    @reddit.decorators.require_login
    def _mark_as_read(self, thing_ids):
        """ Marks each of the supplied thing_ids as read """
        params = {'id': ','.join(thing_ids),
                  'uh': self.modhash}
        response = self.request_json(self.config['read_message'], params)
        urls = [self.config[x] for x in ['inbox', 'moderator', 'unread']]
        # pylint: disable-msg=E1101,W0212
        reddit.helpers._request.is_stale(urls)
        return response

    @reddit.decorators.RequireCaptcha
    @reddit.decorators.require_login
    def compose_message(self, recipient, subject, message, captcha=None):
        """Send a message to another redditor."""
        params = {'text': message,
                  'subject': subject,
                  'to': str(recipient),
                  'uh': self.modhash,
                  'user': self.user.name,
                  'api_type': 'json'}
        if captcha:
            params.update(captcha)
        response = self.request_json(self.config['compose'], params)
        # pylint: disable-msg=E1101,W0212
        reddit.helpers._request.is_stale([self.config['sent']])
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
                  'domain': domain,
                  'uh': self.modhash,
                  'id': '#sr-form',
                  'api_type': 'json'}
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

        user = username or self.config.user or raw_input('Username: ')
        if username and username == self.config.user:
            pswd = password or self.config.pswd
        elif not username and self.config.user:
            pswd = self.config.pswd
        else:
            import getpass
            pswd = password or getpass.getpass('Password for %s: ' % user)

        params = {'api_type': 'json',
                  'passwd': pswd,
                  'user': user}
        response = self.request_json(self.config['login'] % user, params)
        self.modhash = response['data']['modhash']
        self.user = self.get_redditor(user)
        self.user.__class__ = reddit.objects.LoggedInRedditor

    @reddit.decorators.require_login
    def logout(self):
        """Logs out of a session."""
        params = {'uh': self.modhash}
        self.modhash = self.user = None
        return self.request_json(self.config['logout'], params)


class Reddit(LoggedInExtension,  # pylint: disable-msg=R0904
             SubredditExtension):
    def __init__(self, *args, **kwargs):
        super(Reddit, self).__init__(*args, **kwargs)

    def get_all_comments(self, limit=0, place_holder=None):
        """Returns a listing from reddit.com/comments (which provides all of
        the most recent comments from all users to all submissions)."""
        return self.get_content(self.config['comments'], limit=limit,
                                place_holder=place_holder)

    def get_front_page(self, limit=0):
        """Return the reddit front page. Login isn't required, but you'll only
        see your own front page if you are logged in."""
        return self.get_content(self.config['reddit_url'], limit=limit)

    def get_subreddit(self, subreddit_name, *args, **kwargs):
        """Returns a Subreddit object for the subreddit_name specified."""
        return reddit.objects.Subreddit(self, subreddit_name, *args, **kwargs)

    def get_submission(self, url=None, submission_id=None):
        """Returns a Submission object for the given url or submission_id."""
        if bool(url) == bool(submission_id):
            raise TypeError('One (and only one) of id or url is required!')
        if submission_id:
            url = urlparse.urljoin(self.config['comments'], submission_id)
        submission_info, comment_info = self.request_json(url)
        submission = submission_info['data']['children'][0]
        submission.comments = comment_info['data']['children']
        return submission

    def info(self, url=None, thing_id=None, limit=0):
        """
        Given url, queries the API to see if the given URL has been submitted
        already, and if it has, return the submissions.

        Given a thing_id, requests the info for that thing.
        """
        if bool(url) == bool(thing_id):
            raise TypeError('Only one of url or thing_id is required!')
        if url is not None:
            params = {'url': url}
            if (url.startswith(self.config['reddit_url']) and
                url != self.config['reddit_url']):
                warnings.warn('It looks like you may be trying to get the info'
                              ' of a self or internal link. This probably '
                              'will not return any useful results!',
                              UserWarning)
        else:
            params = {'id': thing_id}
        return self.get_content(self.config['info'], url_data=params,
                                limit=limit)

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
                  'text': message,
                  'api_type': 'json'}
        if captcha:
            params.update(captcha)
        return self.request_json(self.config['feedback'], params)

    def search_reddit_names(self, query):
        """Search the subreddits for a reddit whose name matches the query."""
        params = {'query': query,
                  'api_type': 'json'}
        results = self.request_json(self.config['search_reddit_names'], params)
        return [self.get_subreddit(name) for name in results['names']]

    @reddit.decorators.RequireCaptcha
    def create_redditor(self, user_name, password, email='', captcha=None):
        """Register a new user."""
        params = {'email': email,
                  'op': 'reg',
                  'passwd': password,
                  'passwd2': password,
                  'user': user_name,
                  'api_type': 'json'}
        if captcha:
            params.update(captcha)
        return self.request_json(self.config['register'], params)
