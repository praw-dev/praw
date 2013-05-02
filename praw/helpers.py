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

import six
import sys
import time
from requests.exceptions import HTTPError

BACKOFF_START = 4  # Minimum number of seconds to sleep during errors
KEEP_ITEMS = 32  # On each iteration only remember the first # items


def comment_stream(reddit_session, subreddit, verbosity=1):
    """Indefinitely yield new comments from the provided subreddit.

    :param reddit_session: The reddit_session to make requests from. In all the
        examples this is assigned to the varaible ``r``.
    :param subreddit: Either a subreddit object, or the name of a
        subreddit. Use `all` to get the comment stream for all comments made to
        reddit.
    :param verbosity: A number representing the level of output to receive. 0,
        no output; 1, provide a count of the number of items processed; 2,
        output when handled exceptions occur; 3, output some system
        state. (Default: 1)

    """
    def debug(msg, level):
        if verbosity >= level:
            sys.stderr.write(msg + '\n')

    seen = BoundedSet(KEEP_ITEMS * 4)
    before = None
    processed = 0
    backoff = BACKOFF_START
    while True:
        try:
            i = None
            for i, comment in enumerate(reddit_session.get_comments(
                    six.text_type(subreddit), limit=None,
                    params={'before': before})):
                if comment.fullname in seen:
                    if i == 0:
                        assert before is None
                        # Wait until the request is no longer cached
                        debug('Nothing new -- Sleeping for {0} seconds'
                              .format(reddit_session.config.cache_timeout), 3)
                        time.sleep(reddit_session.config.cache_timeout)
                    break
                if i == 0:  # Always the first item in the generator
                    before = comment.fullname
                yield comment
                processed += 1
                if verbosity >= 1 and processed % 100 == 0:
                    sys.stderr.write(' Processed {0}\r'.format(processed))
                    sys.stderr.flush()
                if i < KEEP_ITEMS:
                    seen.add(comment.fullname)
            else:  # Generator exhausted
                if i is None:  # Generator yielded no items
                    assert before is not None
                    # Try again without before as the before item may be too
                    # old or no longer exist.
                    before = None
            backoff = BACKOFF_START
        except HTTPError as exc:
            debug('{0} -- sleeping for {1} seconds'.format(exc, backoff), 2)
            time.sleep(backoff)
            backoff *= 2


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
        if len(self._set) == self.max_items:
            self._set.remove(self._fifo.pop(0))
        self._fifo.append(item)
        self._set.add(item)
