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


def comment_stream(reddit_session, subreddit, limit=None, verbosity=1):
    """Indefinitely yield new comments from the provided subreddit.

    Comments are yielded from oldest to newest.

    :param reddit_session: The reddit_session to make requests from. In all the
        examples this is assigned to the varaible ``r``.
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
    def debug(msg, level):
        if verbosity >= level:
            sys.stderr.write(msg + '\n')

    seen = BoundedSet(KEEP_ITEMS * 4)
    before = None
    processed = 0
    backoff = BACKOFF_START
    while True:
        comments = []
        sleep = None
        start = time.time()
        try:
            i = None
            for i, comment in enumerate(reddit_session.get_comments(
                    six.text_type(subreddit), limit=limit,
                    params={'before': before})):
                if comment.fullname in seen:
                    if i == 0:
                        if before is not None:
                            # Either we have a logic problem, or reddit sent us
                            # out of order data -- log it
                            debug('(INFO) {0} already seen with before of {1}'
                                  .format(comment.fullname, before), 2)
                        # Wait until the request is no longer cached
                        sleep = (reddit_session.config.cache_timeout,
                                 'Nothing new. Sleeping for {0} seconds.', 3)
                    break
                if i == 0:  # Always the first item in the generator
                    before = comment.fullname
                comments.append(comment)
                processed += 1
                if verbosity >= 1 and processed % 100 == 0:
                    sys.stderr.write(' Comments: {0}          \r'
                                     .format(processed))
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
            sleep = (backoff, '{0}. Sleeping for {{0}} seconds.'.format(exc),
                     2)
            backoff *= 2
        # Provide rate limit
        if verbosity >= 1:
            rate = len(comments) / (time.time() - start)
            sys.stderr.write(' Comments: {0} ({1:.2f} cps)    \r'
                             .format(processed, rate))
            sys.stderr.flush()
        # Yield comments from oldest to newest
        for comment in comments[::-1]:
            yield comment
        # Sleep if necessary
        if sleep:
            sleep_time, msg, msg_level = sleep
            debug(msg.format(sleep_time), msg_level)
            time.sleep(sleep_time)


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
