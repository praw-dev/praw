"""Provide helper classes used by other models."""
import random
import time


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
        max_jitter = self._base / 16.
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
        to_set = ['+all']
    else:
        to_set = ['-all']
        omitted = sorted(known_permissions - set(permissions))
        to_set.extend('-{}'.format(x) for x in omitted)
        to_set.extend('+{}'.format(x) for x in permissions)
    return ','.join(to_set)


def stream_generator(function, pause_after=None):
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

    .. note:: This function internally uses an exponential delay with jitter
       between subsequent responses that contain no new results, up to a
       maximum delay of just over a 16 seconds. In practice that means that the
       time before pause for ``pause_after=N+1`` is approximately twice the
       time before pause for ``pause_after=N``.

    For example to pause a comment stream after six responses with no new
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
    before_fullname = None
    exponential_counter = ExponentialCounter(max_counter=16)
    seen_fullnames = BoundedSet(301)
    without_before_counter = 0
    responses_without_new = 0
    valid_pause_after = pause_after is not None
    while True:
        found = False
        newest_fullname = None
        limit = 100
        if before_fullname is None:
            limit -= without_before_counter
            without_before_counter = (without_before_counter + 1) % 30
        for item in reversed(list(function(
                limit=limit, params={'before': before_fullname}))):
            if item.fullname in seen_fullnames:
                continue
            found = True
            seen_fullnames.add(item.fullname)
            newest_fullname = item.fullname
            yield item
        before_fullname = newest_fullname
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
