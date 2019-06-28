"""Caching utilities."""


class cachedproperty(object):
    """A decorator for caching a property's result.

    Similar to `property`, but the wrapped method's result is cached
    on the instance. This is achieved by setting an entry in the object's
    instance dictionary with the same name as the property. When the name
    is later accessed, the value in the instance dictionary takes precedence
    over the (non-data descriptor) property.

    This is useful for implementing lazy-loaded properties.

    The cache can be invalidated via `delattr()`, or by modifying `__dict__`
    directly. It will be repopulated on next access.

    *New in version 6.3.0.*
    """

    def __init__(self, func, doc=None):
        """Initialize the descriptor."""
        self.func = self.__wrapped__ = func

        if doc is None:
            doc = func.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        """Implement descriptor getter.

        Calculate the property's value and then store it in the
        associated object's instance dictionary.
        """
        if obj is None:
            return self

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def __repr__(self):
        """Return repr(self)."""
        return "<%s %s>" % (self.__class__.__name__, self.func)
