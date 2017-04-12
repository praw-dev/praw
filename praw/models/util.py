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
       `+all`.
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
    """Forever yield new items from ListingGenerators.

    :param function: A callable that returns a ListingGenerator, e.g.
       ``subreddit.comments`` or ``subreddit.new``.
    :param pause_after: A integer representing the maximum times to fetch
       data if no new items are found. Once this limit is reached, it will
       yield ``None``, signalling to the caller no new data is available.
       If set to ``0``, it will yield ``None`` after each data fetch that
       returns no new items. If not set, the fetching loop will just keep
       running (with sleeps) until a valid item appears. Once ``None`` is
       yielded, the calling code can still consume the generator, which will
       yield new data once available using the same ``pause_after`` value
       (default: None).
    """
    before_fullname = None
    exponential_counter = ExponentialCounter(max_counter=64)
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
        if found:
            exponential_counter.reset()
            responses_without_new = 0
        else:
            responses_without_new += 1
            if valid_pause_after and responses_without_new > pause_after:
                responses_without_new = 0
                yield None
            else:
                time.sleep(exponential_counter.counter())
