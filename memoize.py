# This code is mostly taken from 
#   http://code.activestate.com/recipes/325905-memoize-decorator-with-timeout/
# and I have changed a few lines.
import time
import copy

class Memoize(object):
    """Memoize With Timeout"""
    _caches = {}
    _timeouts = {}
    
    def __init__(self,timeout=2):
        self.timeout = timeout
        
    def collect(self):
        """Clear cache of results which have timed out"""
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (time.time() - self._caches[func][key][1]) < self._timeouts[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache
    
    def __call__(self, f):
        self.cache = self._caches[f] = {}
        self._timeouts[f] = self.timeout
        
        def func(*args, **kwargs):
            kw = kwargs.items()
            kw.sort()
            # make the Reddit user the first part of the key
            key = (args[0].user, args, tuple(kw))
            key = repr(key)

            try:
                v = self.cache[key]
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                v = self.cache[key] = f(*args,**kwargs),time.time()
            # Make a shallow copy to return
            return copy.copy(v[0])
        return func
