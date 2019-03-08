"""Provide helper classes used by other models."""
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping
from pprint import PrettyPrinter, pformat
import random
import time


class AttributeDict(MutableMapping):
    """A dict class extended to expose its keys though attributes.

    Inherited dict methods (`.update()`, `.clear()`, etc.) always take
    precedence over arbitrary attribute access. Indexing should instead
    be used to access the values of those names.

    There are no restrictions on the key name. If a key can't be get/set
    as an attribute then indexing should be used.

    The inner dict object can be retrieved using `abs(self)`.
    """

    __slots__ = ("_data0",)

    def __init__(self, data=None, **kwargs):
        """Construct an AttributeDict instance."""
        data = {} if data is None else data
        if kwargs:
            data = dict(data, **kwargs)
        object.__setattr__(self, "_data0", data)

    def __contains__(self, item):
        """Implement `in` membership test."""
        return item in self._data0

    def __iter__(self):
        """Implement iter(self)."""
        return iter(self._data0)

    def __len__(self):
        """Return len(self)."""
        return len(self._data0)

    def __getitem__(self, key):
        """Get self[key]."""
        return self._data0[key]

    def __setitem__(self, key, value):
        """Set self[key] to value."""
        self._data0[key] = value

    def __delitem__(self, key):
        """Delete self[key]."""
        del self._data0[key]

    def __getattr__(self, name):
        """Implement getattr(self, name)."""
        try:
            attr = self._data0[name]
        except KeyError:
            pass
        else:
            if isinstance(attr, dict):
                return type(self)(attr)
            return attr

        raise AttributeError(repr(name))

    def __setattr__(self, name, value):
        """Implement setattr(self, name, value)."""
        self.__setitem__(name, value)

    def __delattr__(self, name):
        """Implement delattr(self, name)."""
        self.__delitem__(name)

    def __str__(self):
        """Return str(self)."""
        return str(self._data0)

    def __repr__(self):
        """Return repr(self)."""
        if self._data0:
            return "%s(%r)" % (self.__class__.__name__, self._data0)
        return self.__class__.__name__ + "()"

    def __abs__(self):
        """Return the inner dict object."""
        return self._data0

    def __dir__(self):
        """Support tab completion."""
        return self._data0.keys()

    def __getstate__(self):
        """Extract state to pickle."""
        return self._data0

    def __setstate__(self, state):
        """Restore from pickled state."""
        object.__setattr__(self, "_data0", state)


class ImmutableContainer(object):
    """A mixin that makes container objects immutable."""

    def _immutable(self, *args, **kwargs):
        raise TypeError("%r is immutable" % self.__class__.__name__)

    __setattr__ = __setitem__ = __delitem__ = _immutable


class AttributeContainer(ImmutableContainer, AttributeDict):
    """An immutable container for holding arbitrary attributes.

    Members can be accessed using dot notation, or by indexing like a dict.
    """

    @staticmethod
    def _pprint_attribute_collection(
        printer, obj, stream, indent, allowance, context, level
    ):  # pragma: no cover
        cls = obj.__class__
        stream.write(cls.__name__ + "(")
        printer._format(
            abs(obj),
            stream,
            indent + len(cls.__name__) + 1,
            allowance + 1,
            context,
            level,
        )
        stream.write(")")

    def __str__(self):
        """Return a pretty-print formatted string of the instance."""
        return pformat(self)


if isinstance(getattr(PrettyPrinter, "_dispatch", None), dict):
    PrettyPrinter._dispatch[
        AttributeContainer.__repr__
    ] = AttributeContainer._pprint_attribute_collection


class RedditAttributes(AttributeContainer):
    """A namespace for fetched reddit attributes.

    Members can be accessed using dot notation, or by indexing like a dict.
    """

    def __init__(self, data, prawobj=None):
        """Initialize a RedditAttributes instance.

        If available, prawobj is used to initiate a fetch the first time an
        attribute cannot be found.
        """
        super(RedditAttributes, self).__init__(data)
        object.__setattr__(self, "_prawobj", prawobj)

    def __getitem__(self, key):
        """Return the value of a reddit attribute via indexing."""
        if self._prawobj is None:
            return self._data0[key]

        assert self._prawobj._data is self._data0

        try:
            return self._data0[key]
        except KeyError:
            pass

        if not (self._prawobj._fetched or key.startswith("_")):
            self._prawobj._fetch()

        return self._data0[key]

    def __getattr__(self, name):
        """Return the value of a reddit attribute via dot notation.

        If the retrieved value is a dict type then it will be wrapped
        in an :class:`.AttributeContainer` before being returned.
        """
        try:
            attr = self.__getitem__(name)
        except KeyError:
            pass
        else:
            if isinstance(attr, dict):
                return self.__class__.__base__(attr)
            return attr

        raise AttributeError(repr(name))


class BoundedSet(object):
    """A set with a maximum size that evicts the oldest items when necessary.

    This class does not implement the complete set interface.
    """

    def __init__(self, max_items):
        """Construct an instance of the BoundedSet."""
        self.max_items = max_items
        self._fifo = []
        self._set = set()

    def __contains__(self, item):
        """Test if the BoundedSet contains item."""
        return item in self._set

    def add(self, item):
        """Add an item to the set discarding the oldest item if necessary."""
        if len(self._set) == self.max_items:
            self._set.remove(self._fifo.pop(0))
        self._fifo.append(item)
        self._set.add(item)


class ExponentialCounter(object):
    """A class to provide an exponential counter with jitter."""

    def __init__(self, max_counter):
        """Initialize an instance of ExponentialCounter.

        :param max_counter: The maximum base value. Note that the computed
            value may be 3.125% higher due to jitter.
        """
        self._base = 1
        self._max = max_counter

    def counter(self):
        """Increment the counter and return the current value with jitter."""
        max_jitter = self._base / 16.0
        value = self._base + random.random() * max_jitter - max_jitter / 2
        self._base = min(self._base * 2, self._max)
        return value

    def reset(self):
        """Reset the counter to 1."""
        self._base = 1


def permissions_string(permissions, known_permissions):
    """Return a comma separated string of permission changes.

    :param permissions: A list of strings, or ``None``. These strings can
       exclusively contain ``+`` or ``-`` prefixes, or contain no prefixes at
       all. When prefixed, the resulting string will simply be the joining of
       these inputs. When not prefixed, all permissions are considered to be
       additions, and all permissions in the ``known_permissions`` set that
       aren't provided are considered to be removals. When None, the result is
       ``+all``.
    :param known_permissions: A set of strings representing the available
       permissions.

    """
    to_set = []
    if permissions is None:
        to_set = ["+all"]
    else:
        to_set = ["-all"]
        omitted = sorted(known_permissions - set(permissions))
        to_set.extend("-{}".format(x) for x in omitted)
        to_set.extend("+{}".format(x) for x in permissions)
    return ",".join(to_set)


def stream_generator(
    function, pause_after=None, skip_existing=False, attribute_name="fullname"
):
    """Yield new items from ListingGenerators and ``None`` when paused.

    :param function: A callable that returns a ListingGenerator, e.g.
       ``subreddit.comments`` or ``subreddit.new``.

    :param pause_after: An integer representing the number of requests that
        result in no new items before this function yields ``None``,
        effectively introducing a pause into the stream. A negative value
        yields ``None`` after items from a single response have been yielded,
        regardless of number of new items obtained in that response. A value of
        ``0`` yields ``None`` after every response resulting in no new items,
        and a value of ``None`` never introduces a pause (default: None).

    :param skip_existing: When True does not yield any results from the first
        request thereby skipping any items that existed in the stream prior to
        starting the stream (default: False).

    :param attribute_name: The field to use as an id (default: "fullname").

    .. note:: This function internally uses an exponential delay with jitter
       between subsequent responses that contain no new results, up to a
       maximum delay of just over a 16 seconds. In practice that means that the
       time before pause for ``pause_after=N+1`` is approximately twice the
       time before pause for ``pause_after=N``.

    For example, to create a stream of comment replies, try:

    .. code:: python

       reply_function = reddit.inbox.comment_replies
       for reply in praw.models.util.stream_generator(reply_function):
           print(reply)

    To pause a comment stream after six responses with no new
    comments, try:

    .. code:: python

       subreddit = reddit.subreddit('redditdev')
       for comment in subreddit.stream.comments(pause_after=6):
           if comment is None:
               break
           print(comment)

    To resume fetching comments after a pause, try:

    .. code:: python

       subreddit = reddit.subreddit('help')
       comment_stream = subreddit.stream.comments(pause_after=5)

       for comment in comment_stream:
           if comment is None:
               break
           print(comment)
       # Do any other processing, then try to fetch more data
       for comment in comment_stream:
           if comment is None:
               break
           print(comment)

    To bypass the internal exponential backoff, try the following. This
    approach is useful if you are monitoring a subreddit with infrequent
    activity, and you want the to consistently learn about new items from the
    stream as soon as possible, rather than up to a delay of just over sixteen
    seconds.

    .. code:: python

       subreddit = reddit.subreddit('help')
       for comment in subreddit.stream.comments(pause_after=0):
           if comment is None:
               continue
           print(comment)

    """
    before_attribute = None
    exponential_counter = ExponentialCounter(max_counter=16)
    seen_attributes = BoundedSet(301)
    without_before_counter = 0
    responses_without_new = 0
    valid_pause_after = pause_after is not None
    while True:
        found = False
        newest_attribute = None
        limit = 100
        if before_attribute is None:
            limit -= without_before_counter
            without_before_counter = (without_before_counter + 1) % 30
        for item in reversed(
            list(function(limit=limit, params={"before": before_attribute}))
        ):
            attribute = getattr(item, attribute_name)
            if attribute in seen_attributes:
                continue
            found = True
            seen_attributes.add(attribute)
            newest_attribute = attribute
            if not skip_existing:
                yield item
        before_attribute = newest_attribute
        skip_existing = False
        if valid_pause_after and pause_after < 0:
            yield None
        elif found:
            exponential_counter.reset()
            responses_without_new = 0
        else:
            responses_without_new += 1
            if valid_pause_after and responses_without_new > pause_after:
                exponential_counter.reset()
                responses_without_new = 0
                yield None
            else:
                time.sleep(exponential_counter.counter())
