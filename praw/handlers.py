"""Provides classes that handle request dispatching."""

import time
from functools import wraps
from praw.helpers import normalize_url
from requests import Session
from six import text_type
from threading import Lock
from timeit import default_timer as timer


class RateLimitHandler(object):
    """The base handler that provides thread-safe rate limiting enforcement.

    While this handler is threadsafe, PRAW is not thread safe when the same
    `Reddit` instance is being utilized from multiple threads.

    """

    last_call = {}  # Stores a two-item list: [lock, previous_call_time]
    rl_lock = Lock()  # lock used for adding items to last_call

    @staticmethod
    def rate_limit(function):
        """Return a decorator that enforces API request limit guidelines.

        We are allowed to make a API request every api_request_delay seconds as
        specified in praw.ini. This value may differ from reddit to reddit. For
        reddit.com it is 2. Any function decorated with this will be forced to
        delay _rate_delay seconds from the calling of the last function
        decorated with this before executing.

        This decorator must be applied to a RateLimitHandler class method or
        instance method as it assumes `rl_lock` and `last_call` are available.

        """
        @wraps(function)
        def wrapped(cls, _rate_domain, _rate_delay, **kwargs):
            cls.rl_lock.acquire()
            lock_last = cls.last_call.setdefault(_rate_domain, [Lock(), 0])
            with lock_last[0]:  # Obtain the domain specific lock
                cls.rl_lock.release()
                # Sleep if necessary, then perform the request
                now = timer()
                delay = lock_last[1] + _rate_delay - now
                if delay > 0:
                    now += delay
                    time.sleep(delay)
                lock_last[1] = now
                return function(cls, **kwargs)
        return wrapped

    @classmethod
    def evict(cls, urls):  # pylint: disable=W0613
        """Method utilized to evict entries for the given urls.

        :param urls: An iterable containing normalized urls.
        :returns: The number of items removed from the cache.

        By default this method returns False as a cache need not be present.

        """
        return 0

    def __del__(self):
        """Cleanup the HTTP session."""
        if self.http:
            try:
                self.http.close()
            except:  # Never fail  pylint: disable=W0702
                pass

    def __init__(self):
        """Establish the HTTP session."""
        self.http = Session()  # Each instance should have its own session

    def request(self, request, proxies, timeout, verify, **_):
        """Responsible for dispatching the request and returning the result.

        Network level exceptions should be raised and only
        ``requests.Response`` should be returned.

        :param request: A ``requests.PreparedRequest`` object containing all
            the data necessary to perform the request.
        :param proxies: A dictionary of proxy settings to be utilized for the
            request.
        :param timeout: Specifies the maximum time that the actual HTTP request
            can take.
        :param verify: Specifies if SSL certificates should be validated.

        ``**_`` should be added to the method call to ignore the extra
        arguments intended for the cache handler.

        """
        return self.http.send(request, proxies=proxies, timeout=timeout,
                              allow_redirects=False, verify=verify)
RateLimitHandler.request = RateLimitHandler.rate_limit(
    RateLimitHandler.request)


class DefaultHandler(RateLimitHandler):
    """Extends the RateLimitHandler to add thread-safe caching support."""

    ca_lock = Lock()
    cache = {}
    cache_hit_callback = None
    timeouts = {}

    @staticmethod
    def with_cache(function):
        """Return a decorator that interacts with a handler's cache.

        This decorator must be applied to a DefaultHandler class method or
        instance method as it assumes `cache`, `ca_lock` and `timeouts` are
        available.

        """
        @wraps(function)
        def wrapped(cls, _cache_key, _cache_ignore, _cache_timeout, **kwargs):
            def clear_timeouts():
                """Clear the cache of timed out results."""
                for key in list(cls.timeouts):
                    if timer() - cls.timeouts[key] > _cache_timeout:
                        del cls.timeouts[key]
                        del cls.cache[key]

            if _cache_ignore:
                return function(cls, **kwargs)
            with cls.ca_lock:
                clear_timeouts()
                if _cache_key in cls.cache:
                    if cls.cache_hit_callback:
                        cls.cache_hit_callback(_cache_key)
                    return cls.cache[_cache_key]
            # Releasing the lock before actually making the request allows for
            # the possibility of more than one thread making the same request
            # to get through. Without having domain-specific caching (under the
            # assumption only one request to a domain can be made at a
            # time), there isn't a better way to handle this.
            result = function(cls, **kwargs)
            # The handlers don't call `raise_for_status` so we need to ignore
            # status codes that will result in an exception that should not be
            # cached.
            if result.status_code not in (200, 302):
                return result
            with cls.ca_lock:
                cls.timeouts[_cache_key] = timer()
                cls.cache[_cache_key] = result
                return result
        return wrapped

    @classmethod
    def clear_cache(cls):
        """Remove all items from the cache."""
        with cls.ca_lock:
            cls.cache = {}
            cls.timeouts = {}

    @classmethod
    def evict(cls, urls):
        """Remove items from cache matching URLs.

        Return the number of items removed.

        """
        if isinstance(urls, text_type):
            urls = [urls]
        urls = set(normalize_url(url) for url in urls)
        retval = 0
        with cls.ca_lock:
            for key in list(cls.cache):
                if key[0] in urls:
                    retval += 1
                    del cls.cache[key]
                    del cls.timeouts[key]
        return retval
DefaultHandler.request = DefaultHandler.with_cache(RateLimitHandler.request)
