"""Provide helper classes used by other models."""
import collections
import random
import time


class BoundedSet:
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


class ExponentialCounter:
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
        function,
        pause_after=None,
        skip_existing=False,
        attribute_name="fullname",
        **function_kwargs
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

    Additional keyword arguments will be passed to ``function``.

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
                list(
                    function(
                        limit=limit,
                        params={"before": before_attribute},
                        **function_kwargs
                    )
                )
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


def validate_types(variable,
                   expected_types,
                   ignore_none=True,
                   _internal_call=False,
                   variable_name=None,
                   expected_type_names=None,
                   error_message=None,
                   error_class=TypeError):
    """A function to make sure the values that are entered in a function are the correct types that should be entered
    in order to not cause any weird behavior with mismatched types.

    If the given variable does not match the expected types, then an error, default TypeError, is thrown.

    .. note:: By default, it does not throw an error if the variable is the value `None`, however this can be changed
       by setting the parameter ignore_none to False.

    :param variable: The variable that should be type-checked

    :param expected_types: A type or tuple of types that should be matched to the variable. These are the type(s) that
        the variable should be.

    :param variable_name: The name of the variable that shows up in the error. This does not need to be included if the
        parameter error_message is not None. If error_message is None, then not including this argument will raise a
        ValueError

    :param ignore_none: A boolean stating whether or not to not throw an error if the variable is None. Default true.

    :param _internal_call: A boolean stating if the function is calling itself internally. Default false.

        .. warning:: This function should never be called from outside of this function.

    :param expected_type_names: A list of strings that correspond to the type(s) that are expected. If not given,
        they will be automatically calculated from the name of the given type(s). This does not need to be included
        if the parameter error_message is not None.

    :param error_message: A message to override the default message that is dynamically calculated.

    :param error_class: The error class to raise, default TypeError.

    If a variable does match, nothing is returned.

    .. code:: python

        url = "12"
        validate_types(url, str, variable_name = "url")
        # passes, returns None

    However, if a variable does not match, a TypeError is raised.

    .. code:: python

        id = 12
        validate_types(id, str, variable_name = "id")
        # raises TypeError("The variable id must be type `str` (was type `int`).")

    Multiple types must be specified in a collection such as a list, tuple, or set.

    .. code:: python
        id_list = {"id1": "1", "id2": "2"}
        validate_types(id_list, (list, tuple, set), variable_name = "id")
        # raises TypeError("The variable id_list must be types `list`, `tuple`, or `set` (was type `dict`).)
    """
    if error_message is None and variable_name is None:
        raise ValueError("variable_name needs to be specified if error_message is not given")
    fail = False
    if not _internal_call:
        validate_types(variable_name, str, variable_name="variable_name", _internal_call=True)
        validate_types(expected_types, (type, list, tuple, set), variable_name="expected_types", _internal_call=True)
        validate_types(ignore_none, (int, bool), variable_name="ignore_none", _internal_call=True)
        validate_types(error_message, str, variable_name="error_message", _internal_call=True)
        validate_types(error_class, type, variable_name="error_class", _internal_call=True)
    if expected_type_names is not None:
        validate_types(expected_type_names, (str, list, tuple, set), variable_name="expected_type_names")
    if not ignore_none and variable is None:
        fail = True
    if ignore_none:
        if not isinstance(variable, expected_types) and variable is not None:
            fail = True
    if fail:
        if error_message is None:
            vlist = []
            if not isinstance(expected_types, type):
                msg = "The variable '%s' must be types %s (was type %s)."
            else:
                msg = "The variable '%s' must be type %s (was type %s)."
            if isinstance(expected_type_names, str):
                expected_type_names = (expected_type_names,)
            if expected_type_names is not None:
                for vtype in expected_type_names:
                    vlist.append(vtype)
            else:
                if isinstance(expected_types, type):
                    expected_types = (expected_types,)
                for type_ in expected_types:
                    vlist.append(type_.__name__)
            if len(vlist) > 1:
                prelim_vals = vlist[:-1]
                varmsg = ""
                for val in prelim_vals:
                    varmsg += "`%s`, " % val
                varmsg = varmsg.rstrip(", ")+" "
                varmsg += "or `%s`" % vlist[-1]
            else:
                varmsg = "`%s`" % vlist[-1]
            raise error_class(msg % (variable_name, varmsg, "`%s`" % variable.__class__.__name__))
        else:
            raise error_class(error_message)
