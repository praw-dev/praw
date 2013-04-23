"""Provides classes that handle request dispatching."""
import time
from functools import wraps
from praw.errors import ClientException, InvalidSubreddit
from praw.helpers import normalize_url
from requests import Session
from requests.compat import urljoin


def rate_limit(function):
    """Return a decorator that enforces API request limit guidelines.

    We are allowed to make a API request every api_request_delay seconds as
    specified in praw.ini. This value may differ from reddit to reddit. For
    reddit.com it is 2. Any function decorated with this will be forced to
    delay api_request_delay seconds from the calling of the last function
    decorated with this before executing.

    """
    @wraps(function)
    def wrapped(obj, _rate_domain, _rate_delay, **kwargs):
        last = last_call.get(_rate_domain, 0)
        now = time.time()
        delay = last + _rate_delay - now
        if delay > 0:
            now += delay
            time.sleep(delay)
        last_call[_rate_domain] = now
        return function(obj, **kwargs)
    last_call = {}
    return wrapped


def use_cache(function):
    """Return a decorator that interacts with a handler's cache."""
    @wraps(function)
    def wrapped(obj, _cache_key, _cache_ignore, _cache_timeout, **kwargs):
        if _cache_ignore:
            return function(obj, **kwargs)
        call_time = time.time()
        obj.clear_timeouts(call_time, _cache_timeout)
        obj.timeouts.setdefault(_cache_key, call_time)  # Does not update
        if _cache_key in obj.cache:
            return obj.cache[_cache_key]
        result = function(obj, **kwargs)
        return obj.cache.setdefault(_cache_key, result)
    return wrapped


class DefaultHandler(object):

    """Provides a basic request handler and cache for single-threaded PRAW.

    Rate-limits are enforced on a per-domain basis.

    """

    # The cache is class-level not instance level
    cache = {}
    timeouts = {}
    http = Session()

    @staticmethod
    def _handle_redirect(response):
        """Return the new url or None if there are no redirects.

        Raise exceptions if appropriate.

        """
        if response.status_code != 302:
            return None
        new_url = urljoin(response.url, response.headers['location'])
        if 'reddits/search?q=' in new_url:  # Handle non-existent subreddit
            subreddit = new_url.rsplit('=', 1)[1]
            raise InvalidSubreddit('`{0}` is not a valid subreddit'
                                   .format(subreddit))
        elif 'random' not in response.url:
            raise ClientException('Unexpected redirect from {0} to {1}'
                                  .format(response.url, new_url))
        return new_url

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
                del cls.cache[key]

    @classmethod
    def evict(cls, urls):
        """Remove cached responses by URL."""
        urls = set(normalize_url(url) for url in urls)
        for key in list(cls.cache):
            if key[0] in urls:
                del cls.cache[key]
                del cls.timeouts[key]

    @use_cache
    @rate_limit
    def request(self, request, proxies=None, timeout=45):
        """Make the http request and return the http response."""
        response = None
        while request.url:  # Manually handle 302 redirects
            response = self.http.send(request, proxies=proxies,
                                      timeout=timeout)
            request.url = self._handle_redirect(response)
        return response
