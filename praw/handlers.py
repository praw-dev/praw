"""Provides classes that handle request dispatching."""

import six
import sys
import time
from functools import wraps
from requests.compat import urljoin
from praw.errors import (ClientException, InvalidSubreddit, OAuthException,
                         OAuthInsufficientScope, OAuthInvalidToken)


def rate_limit(function):
    """Return a decorator that enforces API request limit guidelines.

    We are allowed to make a API request every api_request_delay seconds as
    specified in praw.ini. This value may differ from reddit to reddit. For
    reddit.com it is 2. Any function decorated with this will be forced to
    delay api_request_delay seconds from the calling of the last function
    decorated with this before executing.

    """
    @wraps(function)
    def wrapped(obj, reddit_session, *args, **kwargs):
        config = reddit_session.config
        last = last_call.get(config.domain, 0)
        now = time.time()
        delay = last + int(config.api_request_delay) - now
        if delay > 0:
            now += delay
            time.sleep(delay)
        last_call[config.domain] = now
        return function(obj, reddit_session, *args, **kwargs)
    last_call = {}
    return wrapped


def use_cache(function):
    """Return a decorator that interacts with a handler's cache."""
    @wraps(function)
    def wrapped(obj, reddit_session, url, *args, **kwargs):
        if kwargs.get('files'):  # Ignore file uploads
            return function(obj, reddit_session, url, *args, **kwargs)
        normalized_url = obj.normalize_url(url)
        key = (reddit_session, normalized_url, repr(args),
               frozenset(six.iteritems(kwargs)))
        call_time = time.time()
        obj.clear_timeouts(call_time, reddit_session.config.cache_timeout)
        obj.timeouts.setdefault(key, call_time)
        if key in obj.cache:
            return obj.cache[key]
        result = function(obj, reddit_session, url, *args, **kwargs)
        if kwargs.get('raw_response'):
            return result
        return obj.cache.setdefault(key, result)
    return wrapped


class DefaultHandler(object):

    """Provides a basic request handler and cache for single-threaded PRAW.

    Rate-limits are enforced on a per-domain basis.

    """

    # The cache is class-level not instance level
    cache = {}
    timeouts = {}

    @staticmethod
    def _handle_redirect(url, response):
        """Return the new url or None if there are no redirects.

        Raise exceptions if appropriate.

        """
        if response.status_code != 302:
            return None
        new_url = urljoin(url, response.headers['location'])
        if 'reddits/search?q=' in new_url:  # Handle non-existent subreddit
            subreddit = new_url.rsplit('=', 1)[1]
            raise InvalidSubreddit('`{0}` is not a valid subreddit'
                                   .format(subreddit))
        elif 'random' not in url:
            raise ClientException('Unexpected redirect from {0} to {1}'
                                  .format(url, new_url))
        return new_url

    @staticmethod
    def _log_request(reddit_session, url, params, data, auth):
        """Log the request if logging is enabled."""
        if reddit_session.config.log_requests >= 1:
            sys.stderr.write('retrieving: %s\n' % url)
        if reddit_session.config.log_requests >= 2:
            sys.stderr.write('params: %s\n' % (params or 'None'))
            sys.stderr.write('data: %s\n' % (data or 'None'))
            if auth:
                sys.stderr.write('auth: %s\n' % auth)

    @staticmethod
    def _prepare_oauth(reddit_session, url):
        """Return the headers and url for the request."""
        if not getattr(reddit_session, '_use_oauth', False):
            return {}, url

        headers = {'Authorization': 'bearer %s' % reddit_session.access_token}
        # Requests using OAuth for authorization must switch to using the oauth
        # domain.
        # pylint: disable-msg=W0212
        for prefix in (reddit_session.config._site_url,
                       reddit_session.config._ssl_url):
            if url.startswith(prefix):
                if reddit_session.config.log_requests >= 1:
                    sys.stderr.write(
                        'substituting %s for %s in url\n'
                        % (reddit_session.config._oauth_url, prefix))
                url = (reddit_session.config._oauth_url + url[len(prefix):])
                break
        # pylint: enable-msg=W0212
        return headers, url

    @staticmethod
    def _prepare_request(reddit_session, data, auth, files):
        """Return the request function and data dictionary."""
        if not data and not files:
            return reddit_session.http.get, data

        if data is True:
            data = {}
        if not auth:
            data.setdefault('api_type', 'json')
            if reddit_session.modhash:
                data.setdefault('uh', reddit_session.modhash)
        return reddit_session.http.post, data

    @staticmethod
    def _raise_exceptions(url, response):
        """Raise specific errors on some status codes."""
        if response.status_code != 200 and \
                'www-authenticate' in response.headers:
            msg = response.headers['www-authenticate']
            if 'insufficient_scope' in msg:
                raise OAuthInsufficientScope('insufficient_scope', url)
            elif 'invalid_token' in msg:
                raise OAuthInvalidToken('invalid_token', url)
            else:
                raise OAuthException(msg, url)
        response.raise_for_status()

    @staticmethod
    def normalize_url(url):
        """Return url after stripping trailing .json and trailing slashes."""
        if url.endswith('.json'):
            url = url[:-5]
        if url.endswith('/'):
            url = url[:-1]
        return url

    @classmethod
    def clear_cache(cls):
        """Clear the entire cache."""
        cls.cache = {}
        cls.timeouts = {}

    @classmethod
    def clear_timeouts(cls, call_time, cache_timeout):
        """Clear the cache of timed out results."""
        for key in list(cls.timeouts):
            if call_time - cls.timeouts[key] > cache_timeout:
                del cls.timeouts[key]
                if key in cls.cache:
                    del cls.cache[key]

    @classmethod
    def evict(cls, urls):
        """Remove cached RedditContentObject by URL."""
        urls = [cls.normalize_url(url) for url in urls]
        relevant_caches = [key for key in cls.cache if key[1] in urls]
        for key in relevant_caches:
            del cls.cache[key]
            del cls.timeouts[key]

    @use_cache
    @rate_limit
    def request(self, reddit_session, url, params=None, data=None, timeout=45,
                raw_response=False, auth=None, files=None):
        """Make the http request and return the http response body."""
        headers, url = self._prepare_oauth(reddit_session, url)
        self._log_request(reddit_session, url, params, data, auth)
        method, data = self._prepare_request(reddit_session, data, auth, files)
        response = None
        request_url = url
        while request_url:  # Manually handle 302 redirects
            response = method(request_url, params=params, data=data,
                              files=files, headers=headers, timeout=timeout,
                              allow_redirects=False, auth=auth)
            url = request_url
            request_url = self._handle_redirect(request_url, response)
        self._raise_exceptions(url, response)
        if raw_response:
            return response
        return response.text
