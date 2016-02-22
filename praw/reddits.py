"""Provide Reddit classes."""

import json
import os
import re
import sys
from warnings import warn_explicit


import six
from requests import Request, Session
from six.moves import html_entities
from six.moves.urllib.parse import parse_qs, urljoin, urlparse, urlunparse
from update_checker import update_check


from . import decorators, errors, objects
from .config import Config
from .const import __version__
from .internal import (_prepare_request, _raise_redirect_exceptions,
                       _raise_response_exceptions, _to_reddit_list)


class BaseReddit(object):
    """A base class that allows access to reddit's API.

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    RETRY_CODES = [502, 503, 504]
    update_checked = False

    def __init__(self, user_agent, site_name=None, disable_update_check=False,
                 **kwargs):
        """Initialize our connection with a reddit server.

        The user_agent is how your application identifies itself. Read the
        official API guidelines for user_agents
        https://github.com/reddit/reddit/wiki/API. Applications using default
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
        occurring in spite of the check_for_updates setting in praw.ini.

        All additional parameters specified via kwargs will be used to
        initialize the Config object. This can be used to specify configuration
        settings during instantiation of the Reddit instance. See
        https://praw.readthedocs.org/en/latest/pages/configuration_files.html
        for more details.

        """
        if not user_agent or not isinstance(user_agent, six.string_types):
            raise TypeError('user_agent must be a non-empty string.')
        if 'bot' in user_agent.lower():
            warn_explicit(
                'The keyword `bot` in your user_agent may be problematic.',
                UserWarning, '', 0)

        self.config = Config(site_name or os.getenv('REDDIT_SITE') or 'reddit',
                             **kwargs)
        self.http = Session()
        self.http.headers['User-Agent'] = self.config.ua_string(user_agent)
        self.http.validate_certs = self.config.validate_certs

        if self.config.http_proxy or self.config.https_proxy:
            self.http.proxies = {}
            if self.config.http_proxy:
                self.http.proxies['http'] = self.config.http_proxy
            if self.config.https_proxy:
                self.http.proxies['https'] = self.config.https_proxy
        self.modhash = None

        # Check for updates if permitted and this is the first Reddit instance
        if not disable_update_check and not self.update_checked \
                and self.config.check_for_updates:
            update_check(__name__, __version__)
            self.update_checked = True

    def _request(self, url, params=None, data=None, files=None, auth=None,
                 timeout=None, raw_response=False, retry_on_error=True,
                 method=None):
        """Given a page url and a dict of params, open and return the page.

        :param url: the url to grab content from.
        :param params: a dictionary containing the GET data to put in the url
        :param data: a dictionary containing the extra data to submit
        :param files: a dictionary specifying the files to upload
        :param auth: Add the HTTP authentication headers (see requests)
        :param timeout: Specifies the maximum time that the actual HTTP request
            can take.
        :param raw_response: return the response object rather than the
            response body
        :param retry_on_error: if True retry the request, if it fails, for up
            to 3 attempts
        :returns: either the response body or the response object

        """
        def decode(match):
            return six.unichr(html_entities.name2codepoint[match.group(1)])

        def handle_redirect():
            response = None
            url = request.url
            while url:  # Manually handle 302 redirects
                request.url = url
                response = self.http.send(request.prepare(),
                                          proxies=self.http.proxies,
                                          timeout=timeout,
                                          allow_redirects=False,
                                          verify=self.http.validate_certs)
                if self.config.log_requests >= 2:
                    msg = 'status: {0}\n'.format(response.status_code)
                    sys.stderr.write(msg)
                url = _raise_redirect_exceptions(response)
                assert url != request.url
            return response

        timeout = self.config.timeout if timeout is None else timeout
        request = _prepare_request(self, url, params, data, auth, files,
                                   method)

        remaining_attempts = 3 if retry_on_error else 1
        attempt_oauth_refresh = bool(self.refresh_token)
        while True:
            try:
                response = handle_redirect()
                _raise_response_exceptions(response)
                self.http.cookies.update(response.cookies)
                if raw_response:
                    return response
                else:
                    return re.sub('&([^;]+);', decode, response.text)
            except errors.OAuthInvalidToken as error:
                if not attempt_oauth_refresh:
                    raise
                attempt_oauth_refresh = False
                self.refresh_access_information()
                request = _prepare_request(self, url, params, data, auth,
                                           files, method)
            except errors.HTTPException as error:
                remaining_attempts -= 1
                # pylint: disable=W0212
                if error._raw.status_code not in self.RETRY_CODES or \
                        remaining_attempts == 0:
                    raise

    def _json_reddit_objecter(self, json_data):
        """Return an appropriate RedditObject from json_data when possible."""
        try:
            object_class = self.config.by_kind[json_data['kind']]
        except KeyError:
            if 'json' in json_data:
                if len(json_data) != 1:
                    msg = 'Unknown object type: {0}'.format(json_data)
                    warn_explicit(msg, UserWarning, '', 0)
                return json_data['json']
        else:
            return object_class.from_api_response(self, json_data['data'])
        return json_data

    def get_content(self, url, params=None, limit=0, place_holder=None,
                    root_field='data', thing_field='children',
                    after_field='after', object_filter=None, **kwargs):
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
            `place_holder`. The place_holder item is the last item to be
            yielded from this generator. Note that the use of `place_holder` is
            not 100% reliable as the place holder item may no longer exist due
            to being removed or deleted.
        :param root_field: indicates the field in the json response that holds
            the data. Most objects use 'data', however some (flairlist) don't
            have the 'data' object. Use None for the root object.
        :param thing_field: indicates the field under the root_field which
            contains the list of things. Most objects use 'children'.
        :param after_field: indicates the field which holds the after item
            element
        :param object_filter: if set to an integer value, fetch content from
            the corresponding list index in the JSON response. For example
            the JSON response for submission duplicates is a list of objects,
            and the object we want to fetch from is at index 1. So we set
            object_filter=1 to filter out the other useless list elements.
        :type place_holder: a string corresponding to a reddit base36 id
            without prefix, e.g. 'asdfasdf'
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

        if hasattr(self, '_url_update'):
            url = self._url_update(url)  # pylint: disable=E1101

        # While we still need to fetch more content to reach our limit, do so.
        while fetch_once or fetch_all or objects_found < limit:
            page_data = self.request_json(url, params=params)
            if object_filter:
                page_data = page_data[object_filter]
            fetch_once = False
            root = page_data.get(root_field, page_data)
            for thing in root[thing_field]:
                yield thing
                objects_found += 1
                # Terminate when we've reached the limit, or place holder
                if objects_found == limit or (place_holder and
                                              thing.id == place_holder):
                    return
            # Set/update the 'after' parameter for the next iteration
            if root.get(after_field):
                # We use `root.get` to also test if the value evaluates to True
                params['after'] = root[after_field]
            else:
                return

    @decorators.raise_api_exceptions
    def request(self, url, params=None, data=None, retry_on_error=True,
                method=None):
        """Make a HTTP request and return the response.

        :param url: the url to grab content from.
        :param params: a dictionary containing the GET data to put in the url
        :param data: a dictionary containing the extra data to submit
        :param retry_on_error: if True retry the request, if it fails, for up
            to 3 attempts
        :param method: The HTTP method to use in the request.
        :returns: The HTTP response.
        """
        return self._request(url, params, data, raw_response=True,
                             retry_on_error=retry_on_error, method=method)

    @decorators.raise_api_exceptions
    def request_json(self, url, params=None, data=None, as_objects=True,
                     retry_on_error=True, method=None):
        """Get the JSON processed from a page.

        :param url: the url to grab content from.
        :param params: a dictionary containing the GET data to put in the url
        :param data: a dictionary containing the extra data to submit
        :param as_objects: if True return reddit objects else raw json dict.
        :param retry_on_error: if True retry the request, if it fails, for up
            to 3 attempts
        :returns: JSON processed page

        """
        if not url.endswith('.json'):
            url += '.json'
        response = self._request(url, params, data, method=method,
                                 retry_on_error=retry_on_error)
        hook = self._json_reddit_objecter if as_objects else None
        # Request url just needs to be available for the objecter to use
        self._request_url = url  # pylint: disable=W0201

        if response == '':
            # Some of the v1 urls don't return anything, even when they're
            # successful.
            return response

        data = json.loads(response, object_hook=hook)
        delattr(self, '_request_url')
        # Update the modhash
        if isinstance(data, dict) and 'data' in data \
                and 'modhash' in data['data']:
            self.modhash = data['data']['modhash']
        return data


class OAuth2Reddit(BaseReddit):
    """Provides functionality for obtaining reddit OAuth2 access tokens.

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def __init__(self, *args, **kwargs):
        """Initialize an OAuth2Reddit instance."""
        super(OAuth2Reddit, self).__init__(*args, **kwargs)
        self.client_id = self.config.client_id
        self.client_secret = self.config.client_secret
        self.redirect_uri = self.config.redirect_uri

    def _handle_oauth_request(self, data):
        auth = (self.client_id, self.client_secret)
        url = self.config['access_token_url']
        response = self._request(url, auth=auth, data=data, raw_response=True)
        if not response.ok:
            msg = 'Unexpected OAuthReturn: {0}'.format(response.status_code)
            raise errors.OAuthException(msg, url)
        retval = response.json()
        if 'error' in retval:
            error = retval['error']
            if error == 'invalid_grant':
                raise errors.OAuthInvalidGrant(error, url)
            raise errors.OAuthException(retval['error'], url)
        return retval

    def get_access_information(self, code):
        """Return the access information for an OAuth2 authorization grant.

        :param code: the code received in the request from the OAuth2 server
        :returns: A dictionary with the key/value pairs for ``access_token``,
            ``refresh_token`` and ``scope``. The ``refresh_token`` value will
            be None when the OAuth2 grant is not refreshable. The ``scope``
            value will be a set containing the scopes the tokens are valid for.

        """
        data = {'code': code, 'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri}
        retval = self._handle_oauth_request(data)
        return {'access_token': retval['access_token'],
                'refresh_token': retval.get('refresh_token'),
                'scope': set(retval['scope'].split(' '))}

    def get_authorize_url(self, state, scope='identity', refreshable=False):
        """Return the URL to send the user to for OAuth2 authorization.

        :param state: a unique string of your choice that represents this
            individual client
        :param scope: the reddit scope to ask permissions for. Multiple scopes
            can be enabled by passing in a container of strings.
        :param refreshable: when True, a permanent "refreshable" token is
            issued

        """
        params = {'client_id': self.client_id, 'response_type': 'code',
                  'redirect_uri': self.redirect_uri, 'state': state,
                  'scope': _to_reddit_list(scope)}
        params['duration'] = 'permanent' if refreshable else 'temporary'
        request = Request('GET', self.config['authorize'], params=params)
        return request.prepare().url

    @property
    def has_oauth_app_info(self):
        """Return True when OAuth credentials are associated with the instance.

        The necessary credentials are: ``client_id``, ``client_secret`` and
        ``redirect_uri``.

        """
        return all((self.client_id is not None,
                    self.client_secret is not None,
                    self.redirect_uri is not None))

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
                'scope': set(retval['scope'].split(' '))}

    def set_oauth_app_info(self, client_id, client_secret, redirect_uri):
        """Set the app information to use with OAuth2.

        This function need only be called if your praw.ini site configuration
        does not already contain the necessary information.

        Go to https://www.reddit.com/prefs/apps/ to discover the appropriate
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

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def __init__(self, *args, **kwargs):
        """Initialize an UnauthenticatedReddit instance."""
        super(UnauthenticatedReddit, self).__init__(*args, **kwargs)
        # initialize to 1 instead of 0, because 0 does not reliably make
        # new requests.
        self._unique_count = 1

    def create_redditor(self, user_name, password, email=''):
        """Register a new user.

        :returns: The json response from the server.

        """
        data = {'email': email,
                'passwd': password,
                'passwd2': password,
                'user': user_name}
        return self.request_json(self.config['register'], data=data)

    def default_subreddits(self, *args, **kwargs):
        """Return a get_content generator for the default subreddits.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['default_subreddits']
        return self.get_content(url, *args, **kwargs)

    def get_comments(self, subreddit, gilded_only=False, *args, **kwargs):
        """Return a get_content generator for comments in the given subreddit.

        :param gilded_only: If True only return gilded comments.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        key = 'sub_comments_gilded' if gilded_only else 'subreddit_comments'
        url = self.config[key].format(subreddit=six.text_type(subreddit))
        return self.get_content(url, *args, **kwargs)

    def get_controversial(self, *args, **kwargs):
        """Return a get_content generator for controversial submissions.

        Corresponds to submissions provided by
        ``https://www.reddit.com/controversial/`` for the session.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['controversial'], *args, **kwargs)

    def get_domain_listing(self, domain, sort='hot', period=None, *args,
                           **kwargs):
        """Return a get_content generator for submissions by domain.

        Corresponds to the submissions provided by
        ``https://www.reddit.com/domain/{domain}``.

        :param domain: The domain to generate a submission listing for.
        :param sort: When provided must be one of 'hot', 'new', 'rising',
            'controversial, or 'top'. Defaults to 'hot'.
        :param period: When sort is either 'controversial', or 'top' the period
            can be either None (for account default), 'all', 'year', 'month',
            'week', 'day', or 'hour'.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        # Verify arguments
        if sort not in ('controversial', 'hot', 'new', 'rising', 'top'):
            raise TypeError('Invalid sort parameter.')
        if period not in (None, 'all', 'day', 'hour', 'month', 'week', 'year'):
            raise TypeError('Invalid period parameter.')
        if sort not in ('controversial', 'top') and period:
            raise TypeError('Period cannot be set for that sort argument.')

        url = self.config['domain'].format(domain=domain)
        if sort != 'hot':
            url += sort
        if period:  # Set or overwrite params 't' parameter
            kwargs.setdefault('params', {})['t'] = period
        return self.get_content(url, *args, **kwargs)

    def get_flair(self, subreddit, redditor, **params):
        """Return the flair for a user on the given subreddit.

        :param subreddit: Can be either a Subreddit object or the name of a
            subreddit.
        :param redditor: Can be either a Redditor object or the name of a
            redditor.
        :returns: None if the user doesn't exist, otherwise a dictionary
            containing the keys `flair_css_class`, `flair_text`, and `user`.

        """
        name = six.text_type(redditor)
        params.update(name=name)
        url = self.config['flairlist'].format(
            subreddit=six.text_type(subreddit))
        data = self.request_json(url, params=params)
        if not data['users'] or \
                data['users'][0]['user'].lower() != name.lower():
            return None
        return data['users'][0]

    def get_front_page(self, *args, **kwargs):
        """Return a get_content generator for the front page submissions.

        Corresponds to the submissions provided by ``https://www.reddit.com/``
        for the session.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['reddit_url'], *args, **kwargs)

    def get_info(self, url=None, thing_id=None, limit=None):
        """Look up existing items by thing_id (fullname) or url.

        :param url: The url to lookup.
        :param thing_id: A single thing_id, or a list of thing_ids. A thing_id
            can be any one of Comment (``t1_``), Link (``t3_``), or Subreddit
            (``t5_``) to lookup by fullname.
        :param limit: The maximum number of Submissions to return when looking
            up by url. When None, uses account default settings.
        :returns: When a single ``thing_id`` is provided, return the
            corresponding thing object, or ``None`` if not found. When a list
            of ``thing_id``s or a ``url`` is provided return a list of thing
            objects (up to ``limit``). ``None`` is returned if any one of the
            thing_ids or the URL is invalid.

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
            if not isinstance(thing_id, six.string_types):
                thing_id = ','.join(thing_id)
                url = True  # Enable returning a list
            params = {'id': thing_id}
        items = self.request_json(self.config['info'],
                                  params=params)['data']['children']
        if url:
            return items if items else None
        elif items:
            return items[0]
        else:
            return None

    def get_moderators(self, subreddit, **kwargs):
        """Return the list of moderators for the given subreddit."""
        url = self.config['moderators'].format(
            subreddit=six.text_type(subreddit))
        return self.request_json(url, **kwargs)

    def get_new(self, *args, **kwargs):
        """Return a get_content generator for new submissions.

        Corresponds to the submissions provided by
        ``https://www.reddit.com/new/`` for the session.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['new'], *args, **kwargs)

    def get_new_subreddits(self, *args, **kwargs):
        """Return a get_content generator for the newest subreddits.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['new_subreddits']
        return self.get_content(url, *args, **kwargs)

    def get_popular_subreddits(self, *args, **kwargs):
        """Return a get_content generator for the most active subreddits.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        url = self.config['popular_subreddits']
        return self.get_content(url, *args, **kwargs)

    def get_random_subreddit(self, nsfw=False):
        """Return a random Subreddit object.

        :param nsfw: When true, return a random NSFW Subreddit object. Calling
            in this manner will set the 'over18' cookie for the duration of the
            PRAW session.

        """
        path = 'random'
        if nsfw:
            self.http.cookies.set('over18', '1')
            path = 'randnsfw'
        url = self.config['subreddit'].format(subreddit=path)
        response = self._request(url, params={'unique': self._unique_count},
                                 raw_response=True)
        self._unique_count += 1
        return self.get_subreddit(response.url.rsplit('/', 2)[-2])

    def get_random_submission(self, subreddit='all'):
        """Return a random Submission object.

        :param subreddit: Limit the submission to the specified
            subreddit(s). Default: all

        """
        url = self.config['subreddit_random'].format(
            subreddit=six.text_type(subreddit))
        try:
            item = self.request_json(url,
                                     params={'unique': self._unique_count})
            self._unique_count += 1  # Avoid network-level caching
            return objects.Submission.from_json(item)
        except errors.RedirectException as exc:
            self._unique_count += 1
            return self.get_submission(exc.response_url)
        raise errors.ClientException('Expected exception not raised.')

    def get_redditor(self, user_name, *args, **kwargs):
        """Return a Redditor instance for the user_name specified.

        The additional parameters are passed directly into the
        :class:`.Redditor` constructor.

        """
        return objects.Redditor(self, user_name, *args, **kwargs)

    def get_rising(self, *args, **kwargs):
        """Return a get_content generator for rising submissions.

        Corresponds to the submissions provided by
        ``https://www.reddit.com/rising/`` for the session.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['rising'], *args, **kwargs)

    def get_sticky(self, subreddit, bottom=False):
        """Return a Submission object for the sticky of the subreddit.

        :param bottom: Get the top or bottom sticky. If the subreddit has only
            a single sticky, it is considered the top one.

        """
        url = self.config['sticky'].format(subreddit=six.text_type(subreddit))
        param = {'num': 2} if bottom else None
        return objects.Submission.from_json(self.request_json(url,
                                                              params=param))

    def get_submission(self, url=None, submission_id=None, comment_limit=0,
                       comment_sort=None, params=None):
        """Return a Submission object for the given url or submission_id.

        :param comment_limit: The desired number of comments to fetch. If <= 0
            fetch the default number for the session's user. If None, fetch the
            maximum possible.
        :param comment_sort: The sort order for retrieved comments. When None
            use the default for the session's user.
        :param params: Dictionary containing extra GET data to put in the url.

        """
        if bool(url) == bool(submission_id):
            raise TypeError('One (and only one) of id or url is required!')
        if submission_id:
            url = urljoin(self.config['comments'], submission_id)
        return objects.Submission.from_url(self, url,
                                           comment_limit=comment_limit,
                                           comment_sort=comment_sort,
                                           params=params)

    def get_submissions(self, fullnames, *args, **kwargs):
        """Generate Submission objects for each item provided in `fullnames`.

        A submission fullname looks like `t3_<base36_id>`. Submissions are
        yielded in the same order they appear in `fullnames`.

        Up to 100 items are batched at a time -- this happens transparently.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` and `limit` parameters cannot be
        altered.

        """
        fullnames = fullnames[:]
        while fullnames:
            cur = fullnames[:100]
            fullnames[:100] = []
            url = self.config['by_id'] + ','.join(cur)
            for item in self.get_content(url, limit=len(cur), *args, **kwargs):
                yield item

    def get_subreddit(self, subreddit_name, *args, **kwargs):
        """Return a Subreddit object for the subreddit_name specified.

        The additional parameters are passed directly into the
        :class:`.Subreddit` constructor.

        """
        sr_name_lower = subreddit_name.lower()
        if sr_name_lower == 'random':
            return self.get_random_subreddit()
        elif sr_name_lower == 'randnsfw':
            return self.get_random_subreddit(nsfw=True)
        return objects.Subreddit(self, subreddit_name, *args, **kwargs)

    def get_subreddit_recommendations(self, subreddits, omit=None):
        """Return a list of recommended subreddits as Subreddit objects.

        Subreddits with activity less than a certain threshold, will not have
        any recommendations due to lack of data.

        :param subreddits: A list of subreddits (either names or Subreddit
            objects) to base the recommendations on.
        :param omit: A list of subreddits (either names or Subreddit
            objects) that will be filtered out of the result.

        """
        params = {'omit': _to_reddit_list(omit or [])}
        url = self.config['sub_recommendations'].format(
            subreddits=_to_reddit_list(subreddits))
        result = self.request_json(url, params=params)
        return [objects.Subreddit(self, sub['sr_name']) for sub in result]

    def get_top(self, *args, **kwargs):
        """Return a get_content generator for top submissions.

        Corresponds to the submissions provided by
        ``https://www.reddit.com/top/`` for the session.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        """
        return self.get_content(self.config['top'], *args, **kwargs)

    def get_traffic(self, subreddit):
        """Return the json dictionary containing traffic stats for a subreddit.

        :param subreddit: The subreddit whose /about/traffic page we will
            collect.

        """
        url = self.config['subreddit_traffic'].format(
            subreddit=six.text_type(subreddit))
        return self.request_json(url)

    def get_wiki_page(self, subreddit, page):
        """Return a WikiPage object for the subreddit and page provided."""
        return objects.WikiPage(self, six.text_type(subreddit), page.lower())

    def get_wiki_pages(self, subreddit):
        """Return a list of WikiPage objects for the subreddit."""
        url = self.config['wiki_pages'].format(
            subreddit=six.text_type(subreddit))
        return self.request_json(url)

    def is_username_available(self, username):
        """Return True if username is valid and available, otherwise False."""
        params = {'user': username}
        try:
            result = self.request_json(self.config['username_available'],
                                       params=params)
        except errors.BadUsername:
            return False
        return result

    def search(self, query, subreddit=None, sort=None, syntax=None,
               period=None, *args, **kwargs):
        """Return a generator for submissions that match the search query.

        :param query: The query string to search for. If query is a URL only
            submissions which link to that URL will be returned.
        :param subreddit: Limit search results to the subreddit if provided.
        :param sort: The sort order of the results.
        :param syntax: The syntax of the search query.
        :param period: The time period of the results.

        The additional parameters are passed directly into
        :meth:`.get_content`. Note: the `url` parameter cannot be altered.

        See https://www.reddit.com/wiki/search for more information on how to
        build a search query.

        """
        params = {'q': query}
        if 'params' in kwargs:
            params.update(kwargs['params'])
            kwargs.pop('params')
        if sort:
            params['sort'] = sort
        if syntax:
            params['syntax'] = syntax
        if period:
            params['t'] = period
        if subreddit:
            params['restrict_sr'] = 'on'
            subreddit = six.text_type(subreddit)
        else:
            subreddit = 'all'
        url = self.config['search'].format(subreddit=subreddit)

        depth = 2
        while depth > 0:
            depth -= 1
            try:
                for item in self.get_content(url, params=params, *args,
                                             **kwargs):
                    yield item
                break
            except errors.RedirectException as exc:
                parsed = urlparse(exc.response_url)
                params = dict((k, ",".join(v)) for k, v in
                              parse_qs(parsed.query).items())
                url = urlunparse(parsed[:3] + ("", "", ""))
                # Handle redirects from URL searches
                if 'already_submitted' in params:
                    yield self.get_submission(url)
                    break

    def search_reddit_names(self, query):
        """Return subreddits whose display name contains the query."""
        data = {'query': query}
        results = self.request_json(self.config['search_reddit_names'],
                                    data=data)
        return [self.get_subreddit(name) for name in results['names']]


class AuthenticatedReddit(OAuth2Reddit, UnauthenticatedReddit):
    """This class adds the methods necessary for authenticating with reddit.

    Authentication can either be login based
    (through :meth:`~praw.__init__.AuthenticatedReddit.login`), or OAuth2 based
    (via :meth:`~praw.__init__.AuthenticatedReddit.set_access_credentials`).

    You should **not** directly instantiate instances of this class. Use
    :class:`.Reddit` instead.

    """

    def __init__(self, *args, **kwargs):
        """Initialize an AuthenticatedReddit instance."""
        super(AuthenticatedReddit, self).__init__(*args, **kwargs)
        # Add variable to distinguish between authentication type
        #  * None means unauthenticated
        #  * True mean login authenticated
        #  * set(...) means OAuth authenticated with the scopes in the set
        self._authentication = None
        self.access_token = None
        self.refresh_token = self.config.refresh_token or None

    def __str__(self):
        """Return a string representation of the AuthenticatedReddit."""
        if isinstance(self._authentication, set):
            return 'OAuth2 reddit session (scopes: {0})'.format(
                ', '.join(self._authentication))
        elif self._authentication:
            return 'LoggedIn reddit session (user: {0})'.format(self.user)
        else:
            return 'Unauthenticated reddit session'

    def _url_update(self, url):
        # When getting posts from a multireddit owned by the authenticated
        # Redditor, we are redirected to me/m/multi/. Handle that now
        # instead of catching later.
        if re.search('user/.*/m/.*', url):
            redditor = url.split('/')[-4]
            if self.user and self.user.name.lower() == redditor.lower():
                url = url.replace("user/"+redditor, 'me')
        return url

    def accept_moderator_invite(self, subreddit):
        """Accept a moderator invite to the given subreddit.

        Callable upon an instance of Subreddit with no arguments.

        :returns: The json response from the server.

        """
        data = {'r': six.text_type(subreddit)}
        # Clear moderated subreddits and cache
        self.user._mod_subs = None  # pylint: disable=W0212
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

    def delete(self, password, message=""):
        """Delete the currently authenticated redditor.

        WARNING!

        This action is IRREVERSIBLE. Use only if you're okay with NEVER
        accessing this reddit account again.

        :param password: password for currently authenticated account
        :param message: optional 'reason for deletion' message.
        :returns: json response from the server.

        """
        data = {'user': self.user.name,
                'passwd': password,
                'delete_message': message,
                'confirm': True}
        return self.request_json(self.config['delete_redditor'], data=data)

    def edit_wiki_page(self, subreddit, page, content, reason=''):
        """Create or edit a wiki page with title `page` for `subreddit`.

        :returns: The json response from the server.

        """
        data = {'content': content,
                'page': page,
                'r': six.text_type(subreddit),
                'reason': reason}
        return self.request_json(self.config['wiki_edit'], data=data)

    def get_access_information(self, code,  # pylint: disable=W0221
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

    def get_flair_choices(self, subreddit, link=None):
        """Return available flair choices and current flair.

        :param link: If link is given, return the flair options for this
            submission. Not normally given directly, but instead set by calling
            the flair_choices method for Submission objects.
            Use the default for the session's user.

        :returns: A dictionary with 2 keys. 'current' containing current flair
            settings for the authenticated user and 'choices' containing a list
            of possible flair choices.

        """
        data = {'r':  six.text_type(subreddit), 'link': link}
        return self.request_json(self.config['flairselector'], data=data)

    def get_friends(self, **params):
        """Return a UserList of Redditors with whom the user is friends."""
        url = self.config['friends']
        return self.request_json(url, params=params)[0]

    def get_me(self):
        """Return a LoggedInRedditor object.

        Note: This function is only intended to be used with an 'identity'
        providing OAuth2 grant.
        """
        response = self.request_json(self.config['me'])
        user = objects.Redditor(self, response['name'], response)
        user.__class__ = objects.LoggedInRedditor
        return user

    def has_scope(self, scope):
        """Return True if OAuth2 authorized for the passed in scope(s)."""
        if '*' in self._authentication:
            return True
        if isinstance(scope, six.string_types):
            scope = [scope]
        return all(s in self._authentication for s in scope)

    def is_logged_in(self):
        """Return True when the session is authenticated via username/password.

        Username and passwords are provided via
        :meth:`~praw.__init__.AuthenticatedReddit.login`.

        """
        return self._authentication is True

    def refresh_access_information(self,  # pylint: disable=W0221
                                   refresh_token=None,
                                   update_session=True):
        """Return updated access information for an OAuth2 authorization grant.

        :param refresh_token: The refresh token used to obtain the updated
            information. When not provided, use the stored refresh_token.
        :param update_session: Update the session with the returned data.
        :returns: A dictionary with the key/value pairs for ``access_token``,
            ``refresh_token`` and ``scope``. The ``refresh_token`` value will
            be None when the OAuth2 grant is not refreshable. The ``scope``
            value will be a set containing the scopes the tokens are valid for.

        """
        response = super(AuthenticatedReddit, self).refresh_access_information(
            refresh_token=refresh_token or self.refresh_token)
        if update_session:
            self.set_access_credentials(**response)
        return response

    def select_flair(self, item, flair_template_id='', flair_text=''):
        """Select user flair or link flair on subreddits.

        This can only be used for assigning your own name flair or link flair
        on your own submissions. For assigning other's flairs using moderator
        access, see :meth:`~praw.__init__.ModFlairMixin.set_flair`.

        :param item: A string, Subreddit object (for user flair), or
            Submission object (for link flair). If ``item`` is a string it
            will be treated as the name of a Subreddit.
        :param flair_template_id: The id for the desired flair template. Use
            the :meth:`~praw.objects.Subreddit.get_flair_choices` and
            :meth:`~praw.objects.Submission.get_flair_choices` methods to find
            the ids for the available user and link flair choices.
        :param flair_text: A string containing the custom flair text.
            Used on subreddits that allow it.

        :returns: The json response from the server.

        """
        data = {'flair_template_id': flair_template_id or '',
                'text':              flair_text or ''}
        if isinstance(item, objects.Submission):  # Link flair
            data['link'] = item.fullname
        else:  # User flair

            data['name'] = self.user.name
            data['r'] = six.text_type(item)
        response = self.request_json(self.config['select_flair'], data=data)
        return response

    def set_access_credentials(self, scope, access_token, refresh_token=None,
                               update_user=True):
        """Set the credentials used for OAuth2 authentication.

        Calling this function will overwrite any currently existing access
        credentials.

        :param scope: A set of reddit scopes the tokens provide access to
        :param access_token: the access token of the authentication
        :param refresh_token: the refresh token of the authentication
        :param update_user: Whether or not to set the user attribute for
            identity scopes

        """
        if isinstance(scope, (list, tuple)):
            scope = set(scope)
        elif isinstance(scope, six.string_types):
            scope = set(scope.split())
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
