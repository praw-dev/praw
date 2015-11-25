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
from collections import deque
from functools import partial
from timeit import default_timer as timer
from praw.errors import HTTPException

BACKOFF_START = 4  # Minimum number of seconds to sleep during errors
KEEP_ITEMS = 128  # On each iteration only remember the first # items


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
    :param verbosity: A number that controls the amount of output produced to
        stderr. <= 0: no output; >= 1: output the total number of comments
        processed and provide the short-term number of comments processed per
        second; >= 2: output when additional delays are added in order to avoid
        subsequent unexpected http errors. >= 3: output debugging information
        regarding the comment stream. (Default: 1)

    """
    get_function = partial(reddit_session.get_comments,
                           six.text_type(subreddit))
    return _stream_generator(get_function, limit, verbosity)


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
    :param verbosity: A number that controls the amount of output produced to
        stderr. <= 0: no output; >= 1: output the total number of submissions
        processed and provide the short-term number of submissions processed
        per second; >= 2: output when additional delays are added in order to
        avoid subsequent unexpected http errors. >= 3: output debugging
        information regarding the submission stream. (Default: 1)

    """
    if six.text_type(subreddit).lower() == "all":
        if limit is None:
            limit = 1000
    if not hasattr(subreddit, 'reddit_session'):
        subreddit = reddit_session.get_subreddit(subreddit)
    return _stream_generator(subreddit.get_new, limit, verbosity)


def valid_redditors(redditors, sub):
    """Return a verified list of valid Redditor instances.

    :param redditors: A list comprised of Redditor instances and/or strings
        that are to be verified as actual redditor accounts.
    :param sub: A Subreddit instance that the authenticated account has
        flair changing permission on.

    Note: Flair will be unset for all valid redditors in `redditors` on the
    subreddit `mod_sub`.

    """
    simplified = list(set(six.text_type(x).lower() for x in redditors))
    return [sub.reddit_session.get_redditor(simplified[i], fetch=False)
            for (i, resp) in enumerate(sub.set_flair_csv(
                ({'user': x, 'flair_text': x} for x in simplified)))
            if resp['ok']]


def all_submissions(reddit_session,
                    subreddit,
                    highest_timestamp=None,
                    lowest_timestamp=None,
                    verbosity=1):
    """Yield submissions between two timestamps.

    If both ``highest_timestamp`` and ``lowest_timestamp`` are unspecified,
    yields all submissions in the ``subreddit``.

    Submissions are yielded from newest to oldest(like in the "new" queue).

    :param reddit_session: The reddit_session to make requests from. In all the
        examples this is assigned to the variable ``r``.
    :param subreddit: Either a subreddit object, or the name of a
        subreddit. Use `all` to get the submissions stream for all submissions
        made to reddit.
    :param highest_timestamp: The upper bound for ``created_utc`` attribute
        of submissions. (Default: current unix time)
    :param lowest_timestamp: The lower bound for ``created_utc`` atributed of
        submissions.
        (Default: subreddit's created_utc or 0 when subreddit == "all").
        NOTE: both highest_timestamp and lowest_timestamp are proper
        unix timestamps(just like ``created_utc`` attributes)
    :param verbosity: A number that controls the amount of output produced to
        stderr. <= 0: no output; >= 1: output the total number of submissions
        processed; >= 2: output debugging information regarding
        the search queries. (Default: 1)

    """
    def debug(msg, level):
        if verbosity >= level:
            sys.stderr.write(msg + '\n')

    reddit_timestamp_offset = 28800
    if highest_timestamp is None:
        # convert normal unix timestamps into broken reddit timestamps
        highest_timestamp = int(time.time()) + reddit_timestamp_offset

    if lowest_timestamp is not None:
        lowest_timestamp + reddit_timestamp_offset
    elif not isinstance(subreddit, six.string_types):
        print six.string_types
        print type(subreddit)
        lowest_timestamp = subreddit.created
    elif subreddit != "all":
        lowest_timestamp = reddit_session.get_subreddit(subreddit).created
    else:
        lowest_timestamp = 0

    # Those parameters work ok, but there may be a better set of parameters
    window_size = 60 * 60
    search_limit = 100
    min_search_results_in_window = 30
    backoff = BACKOFF_START

    processed_submissions = 0
    while highest_timestamp >= lowest_timestamp:
        try:
            search_query = 'timestamp:{}..{}'.format(
                max(highest_timestamp - window_size, lowest_timestamp),
                highest_timestamp)
            debug(search_query, 3)
            search_results = list(reddit_session.search(search_query,
                                                        subreddit=subreddit,
                                                        limit=search_limit,
                                                        syntax='cloudsearch',
                                                        sort='new'))

            debug("Received {0} search results for query {1}"
                  .format(len(search_results), search_query), 2)

            backoff = BACKOFF_START
        except HTTPException as exc:
            debug("{0}. Sleeping for {1} seconds".format(exc, backoff), 2)
            time.sleep(backoff)
            backoff *= 2
            continue

        if len(search_results) >= search_limit:
            window_size /= 2
            debug("Reducing window size to {0} seconds".format(window_size), 2)
            continue

        for submission in search_results:
            yield submission

        highest_timestamp -= (window_size + 1)
        processed_submissions += len(search_results)
        debug('Total processed submissions: {}'
              .format(processed_submissions), 1)

        if len(search_results) < min_search_results_in_window:
            debug("Increasing window size to {0} seconds"
                  .format(window_size), 2)
            window_size *= 2


def _stream_generator(get_function, limit=None, verbosity=1):
    def debug(msg, level):
        if verbosity >= level:
            sys.stderr.write(msg + '\n')

    def b36_id(item):
        return int(item.id, 36)

    seen = BoundedSet(KEEP_ITEMS * 16)
    before = None
    count = 0  # Count is incremented to bypass the cache
    processed = 0
    backoff = BACKOFF_START
    while True:
        items = []
        sleep = None
        start = timer()
        try:
            i = None
            params = {'uniq': count}
            count = (count + 1) % 100
            if before:
                params['before'] = before
            gen = enumerate(get_function(limit=limit, params=params))
            for i, item in gen:
                if b36_id(item) in seen:
                    if i == 0:
                        if before is not None:
                            # reddit sent us out of order data  -- log it
                            debug('(INFO) {0} already seen with before of {1}'
                                  .format(item.fullname, before), 3)
                            before = None
                    break
                if i == 0:  # Always the first item in the generator
                    before = item.fullname
                if b36_id(item) not in seen:
                    items.append(item)
                    processed += 1
                if verbosity >= 1 and processed % 100 == 0:
                    sys.stderr.write(' Items: {0}            \r'
                                     .format(processed))
                    sys.stderr.flush()
                if i < KEEP_ITEMS:
                    seen.add(b36_id(item))
            else:  # Generator exhausted
                if i is None:  # Generator yielded no items
                    assert before is not None
                    # Try again without before as the before item may be too
                    # old or no longer exist.
                    before = None
            backoff = BACKOFF_START
        except HTTPException as exc:
            sleep = (backoff, '{0}. Sleeping for {{0}} seconds.'.format(exc),
                     2)
            backoff *= 2
        # Provide rate limit
        if verbosity >= 1:
            rate = len(items) / (timer() - start)
            sys.stderr.write(' Items: {0} ({1:.2f} ips)    \r'
                             .format(processed, rate))
            sys.stderr.flush()
        # Yield items from oldest to newest
        for item in items[::-1]:
            yield item
        # Sleep if necessary
        if sleep:
            sleep_time, msg, msg_level = sleep  # pylint: disable=W0633
            debug(msg.format(sleep_time), msg_level)
            time.sleep(sleep_time)


def convert_id36_to_numeric_id(id36):
    """Convert strings representing base36 numbers into an integer."""
    if not isinstance(id36, six.string_types) or id36.count("_") > 0:
        raise ValueError("must supply base36 string, not fullname (e.g. use "
                         "xxxxx, not t3_xxxxx)")
    return int(id36, 36)


def convert_numeric_id_to_id36(numeric_id):
    """Convert an integer into its base36 string representation.

    This method has been cleaned up slightly to improve readability. For more
    info see:

    https://github.com/reddit/reddit/blob/master/r2/r2/lib/utils/_utils.pyx

    https://www.reddit.com/r/redditdev/comments/n624n/submission_ids_question/

    https://en.wikipedia.org/wiki/Base36
    """
    # base36 allows negative numbers, but reddit does not
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
    stack = deque(tree)
    extend = stack.extend if depth_first else stack.extendleft
    retval = []
    while stack:
        item = stack.popleft()
        nested = getattr(item, nested_attr, None)
        if nested:
            extend(nested)
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
        if item in self._set:
            self._fifo.remove(item)
        elif len(self._set) == self.max_items:
            self._set.remove(self._fifo.pop(0))
        self._fifo.append(item)
        self._set.add(item)
