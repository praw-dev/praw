"""Provide helper classes used by other models."""


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


def stream_generator(function):
    """Forever yield new items from ListingGenerators."""
    before_fullname = None
    seen_fullnames = BoundedSet(301)
    without_before_counter = 0
    while True:
        newest_fullname = None
        limit = 100
        if before_fullname is None:
            limit -= without_before_counter
            without_before_counter = (without_before_counter + 1) % 30
        for item in reversed(list(function(
                limit=limit, params={'before': before_fullname}))):
            if item.fullname in seen_fullnames:
                continue
            seen_fullnames.add(item.fullname)
            newest_fullname = item.fullname
            yield item
        before_fullname = newest_fullname
