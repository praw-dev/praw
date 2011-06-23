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

import time
import urlparse
from settings import CACHE_TIMEOUT

from functools import wraps

class memoize(object):
    """
    Simple memoize decorator with timeout, providing a way to prune out cached
    results based on the first parameter to the memoized function.

    For RedditContentObject methods, this means removal by URL, provided by the
    is_stale method.
    """
    TIMEOUT = CACHE_TIMEOUT

    def __init__(self, func):
        wraps(func)(self)
        self.func = func

        self._cache = {}
        self._timeouts = {}

    def __call__(self, *args, **kwargs):
        key = (args[0], args[1], repr(args[2:]), frozenset(kwargs.items()))
        call_time = time.time()
        self.clear_timeouts(call_time)

        self._timeouts.setdefault(key, call_time)
        if key in self._cache:
            return self._cache[key]
        return self._cache.setdefault(key, self.func(*args, **kwargs))

    def clear_timeouts(self, call_time):
        """
        Clears the _caches of results which have timed out.
        """
        need_clearing = (k for k, v in self._timeouts.items()
                                    if call_time - v > self.TIMEOUT)
        for k in need_clearing:
            try:
                del self._cache[k]
            except KeyError:
                pass
            del self._timeouts[k]

    def is_stale(self, urls):
        relevant_caches = [k for k in self._cache if k[1] in urls or
                                        k[1].rstrip(".json") in urls]
        for k in relevant_caches:
            del self._cache[k]
            del self._timeouts[k]

def limit_chars(num_chars=80):
    """
    A decorator to limit the number of chars in a function that outputs a
    string.
    """
    def func_limiter(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            if len(value) > num_chars:
                value = value[:num_chars] + "..."
            return value
        return func_wrapper
    return func_limiter

def urljoin(base, subpath, *args, **kwargs):
    """
    Does a urljoin with a base url, always considering the base url to end
    with a directory, and never truncating the base url.
    """
    subpath = subpath.lstrip("/")

    if not subpath:
        return base
    if not base.endswith("/"):
        return urlparse.urljoin(base + "/", subpath, *args, **kwargs)
    return urlparse.urljoin(base, subpath, *args, **kwargs)
