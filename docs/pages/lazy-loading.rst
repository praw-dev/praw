.. _lazy_objects:

Lazy Objects
============

Each API request to Reddit must be separated by a 2 second delay, as per the
API rules. So to get the highest performance, the number of API calls must be
kept as low as possible. PRAW uses lazy objects to only make API calls when/if
the information is needed.

For instance, if you're doing the following::

    >>> import praw
    >>> r = praw.Reddit(user_agent=UNIQUE_AND_DESCRIPTIVE_USERAGENT)
    >>> subreddit = r.get_subreddit('askhistorians')

Then :meth:`.get_subreddit` didn't send a request to Reddit. Instead it created
a lazy :class:`.Subreddit` object, that will be filled out with data when/if
necessary::

    >>> for post in subreddit.get_hot():
    ...     pass

Information about the subreddit, like number of subscribers or its
description, is not needed to get the hot listing. So PRAW doesn't request
it and avoids an unnecessary API call, making the code above run about 2
seconds faster due to lazy objects.

When do the lazy loaded objects become non-lazy?
------------------------------------------------

When the information is needed. It's really that simple. Continuing the code
from above::

    >>> subreddit.has_fetched
    False # Data has not been fetched from reddit. It's a lazily loaded object.
    >>> subreddit.public_description
    u'Questions about the past: answered!'
    >>> subreddit.has_fetched
    True # No longer lazily loaded.

Where are the lazy objects?
---------------------------

PRAW uses lazy objects whenever possible. Objects created with
:meth:`.get_subreddit` or :meth:`.get_redditor` are lazy, unless you call the
methods with ``fetch=True``. In this case all data about the object will be
fetched at creation::

    >>> non_lazy_subreddit = r.get_subreddit('askhistorians', fetch=True)
    >>> non_lazy_subreddit.has_fetched
    True

When one object references another, the referenced object starts as a lazy
object::

    >> submission = r.get_submission(submission_id="16m0uu")
    >> submission.author # Reference to a lazy created Redditor object.

Whenever a method returns a generator, such as when you call
:meth:`.get_front_page` then that's also a lazy object. They don't send API
requests to reddit for information until you actually need it by iterating
through the generator.

Lazy objects and errors
-----------------------

The downside of using lazy objects is that any error will not happen when the
lazy object is created, but instead when the API call is actually made.
