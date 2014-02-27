# This file is part of PRAW.
#
# PRAW is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PRAW is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PRAW.  If not, see <http://www.gnu.org/licenses/>.

"""
Helper functions.

The functions here provide functionality that is often needed by programs using
PRAW, but which isn't part of reddit's API.
"""

from __future__ import unicode_literals

import six
import sys
import time
from functools import partial
from requests.exceptions import HTTPError

BACKOFF_START = 4  # Minimum number of seconds to sleep during errors
KEEP_ITEMS = 32  # On each iteration only remember the first # items


def comment_stream(reddit_session, subreddit, limit=None, verbosity=1):
    """Indefinitely yield new comments from the provided subreddit.

    Comments are yielded from oldest to newest.

    :param reddit_session: The reddit_session to make requests from. In all the
        examples this is assigned to the variable ``r``.
    :param subreddit: Either a subreddit object, or the name of a
        subreddit. Use `all` to get the comment stream for all comments made to
        reddit.
    :param limit: The maximum number of comments to fetch in a single
        iteration. When None, fetch all available comments (reddit limits this
        to 1000 (or multiple of 1000 for multi-subreddits). If this number is
        too small, comments may be missed.
    :param verbosity: A number representing the level of output to receive. 0,
        no output; 1, provide a count of the number of items processed; 2,
        output when handled exceptions occur; 3, output some system
        state. (Default: 1)

    """
    get_function = partial(reddit_session.get_comments,
                           six.text_type(subreddit))
    return _stream_generator(get_function, reddit_session, limit, verbosity)


def submission_stream(reddit_session, subreddit, limit=None, verbosity=1):
    """Indefinitely yield new submissions from the provided subreddit.

    Submissions are yielded from oldest to newest.

    :param reddit_session: The reddit_session to make requests from. In all the
        examples this is assigned to the variable ``r``.
    :param subreddit: Either a subreddit object, or the name of a
        subreddit. Use `all` to get the submissions stream for all submissions
        made to reddit.
    :param limit: The maximum number of submissions to fetch in a single
        iteration. When None, fetch all available submissions (reddit limits
        this to 1000 (or multiple of 1000 for multi-subreddits). If this number
        is too small, submissions may be missed. Since there isn't a limit to
        the number of submissions that can be retrieved from r/all, the limit
        will be set to 1000 when limit is None.
    :param verbosity: A number representing the level of output to receive. 0,
        no output; 1, provide a count of the number of items processed; 2,
        output when handled exceptions occur; 3, output some system
        state. (Default: 1)

    """
    if six.text_type(subreddit).lower() == "all":
        if limit is None:
            limit = 1000
    if not hasattr(subreddit, 'reddit_session'):
        subreddit = reddit_session.get_subreddit(subreddit)
    return _stream_generator(subreddit.get_new, reddit_session, limit,
                             verbosity)


def _stream_generator(get_function, reddit_session, limit=None, verbosity=1):
    def debug(msg, level):
        if verbosity >= level:
            sys.stderr.write(msg + '\n')

    seen = BoundedSet(KEEP_ITEMS * 4)
    before = None
    processed = 0
    backoff = BACKOFF_START
    while True:
        items = []
        sleep = None
        start = time.time()
        try:
            i = None
            gen = enumerate(get_function(limit=limit,
                                         params={'before': before}))
            for i, item in gen:
                if item.fullname in seen:
                    if i == 0:
                        if before is not None:
                            # Either we have a logic problem, or reddit sent us
                            # out of order data -- log it
                            debug('(INFO) {0} already seen with before of {1}'
                                  .format(item.fullname, before), 2)
                        # Wait until the request is no longer cached
                        sleep = (reddit_session.config.cache_timeout,
                                 'Nothing new. Sleeping for {0} seconds.', 3)
                    break
                if i == 0:  # Always the first item in the generator
                    before = item.fullname
                items.append(item)
                processed += 1
                if verbosity >= 1 and processed % 100 == 0:
                    sys.stderr.write(' Items: {0}          \r'
                                     .format(processed))
                    sys.stderr.flush()
                if i < KEEP_ITEMS:
                    seen.add(item.fullname)
            else:  # Generator exhausted
                if i is None:  # Generator yielded no items
                    assert before is not None
                    # Try again without before as the before item may be too
                    # old or no longer exist.
                    before = None
            backoff = BACKOFF_START
        except HTTPError as exc:
            sleep = (backoff, '{0}. Sleeping for {{0}} seconds.'.format(exc),
                     2)
            backoff *= 2
        # Provide rate limit
        if verbosity >= 1:
            rate = len(items) / (time.time() - start)
            sys.stderr.write(' Items: {0} ({1:.2f} ips)    \r'
                             .format(processed, rate))
            sys.stderr.flush()
        # Yield items from oldest to newest
        for item in items[::-1]:
            yield item
        # Sleep if necessary
        if sleep:
            sleep_time, msg, msg_level = sleep
            debug(msg.format(sleep_time), msg_level)
            time.sleep(sleep_time)


def convert_id36_to_numeric_id(id36):
    """
    Convert base 36 into numeric ID
    """
    if not isinstance(id36, six.string_types) or id36.count("_") > 0:
        raise ValueError("must supply base36 string, not fullname (e.g. use "
                         "xxxxx, not t3_xxxxx)")
    return int(id36, 36)


def convert_numeric_id_to_id36(numeric_id):
    """
    Convert numeric ID into base36, method has been cleaned up slightly
    to improve readability. For more info see;

    https://github.com/reddit/reddit/blob/master/r2/r2/lib/utils/_utils.pyx
    http://www.reddit.com/r/redditdev/comments/n624n/submission_ids_question/
    http://en.wikipedia.org/wiki/Base_36#Python_implementation
    """

    # base36 does allows negative numbers, but reddit does not
    if not isinstance(numeric_id, six.integer_types) or numeric_id < 0:
        raise ValueError("must supply a positive int/long")

    # Alphabet used for base 36 conversion
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    alphabet_len = len(alphabet)

    # Temp assign
    current_number = numeric_id
    base36 = []

    # Current_number must be greater than alphabet length to while/divmod
    if 0 <= current_number < alphabet_len:
        return alphabet[current_number]

    # Break up into chunks
    while current_number != 0:
        current_number, rem = divmod(current_number, alphabet_len)
        base36.append(alphabet[rem])

    # String is built in reverse order
    return ''.join(reversed(base36))


def flatten_tree(tree, nested_attr='replies', depth_first=False):
    """Return a flattened version of the passed in tree.

    :param nested_attr: The attribute name that contains the nested items.
        Defaults to ``replies`` which is suitable for comments.
    :param depth_first: When true, add to the list in a depth-first manner
        rather than the default breadth-first manner.

    """
    stack = tree[:]
    retval = []
    while stack:
        item = stack.pop(0)
        nested = getattr(item, nested_attr, None)
        if nested and depth_first:
            stack.extend(nested)
        elif nested:
            stack[0:0] = nested
        retval.append(item)
    return retval


def normalize_url(url):
    """Return url after stripping trailing .json and trailing slashes."""
    if url.endswith('.json'):
        url = url[:-5]
    if url.endswith('/'):
        url = url[:-1]
    return url


class BoundedSet(object):

    """A set with a maxmimum size that evicts the oldest items when necessary.

    This class does not implement the complete set interface.

    """

    def __init__(self, max_items):
        self.max_items = max_items
        self._fifo = []
        self._set = set()

    def __contains__(self, item):
        return item in self._set

    def add(self, item):
        """Add an item to the set discarding the oldest item if necessary."""
        if item in self._set:
            self._fifo.remove(item)
        elif len(self._set) == self.max_items:
            self._set.remove(self._fifo.pop(0))
        self._fifo.append(item)
        self._set.add(item)
