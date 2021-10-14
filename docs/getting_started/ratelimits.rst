.. _ratelimits:

Ratelimits
==========

Even though PRAW respects the |ratelimit_header|_ and waits the appropriate time between
requests, there are other unknown ratelimits that Reddit has that might require
additional wait time (anywhere from milliseconds to minutes) for things such as
commenting, editing comments/posts, banning users, adding moderators, etc. PRAW will
sleep and try the request again if the requested wait time (as much as 600s) is less
than or equal to PRAW's |ratelimit_seconds|_, PRAW will wait for the requested time plus
1 second. If the requested wait time exceeds the set value of ``ratelimit_seconds``,
PRAW will raise :class:`.RedditAPIException`.

For example, given the following Reddit instance:

.. code-block:: python

    import praw

    reddit = praw.Reddit(
        client_id="xxx",
        client_secret="xxx",
        username="xxx",
        password="xxx",
        user_agent="Example bot v0.0.1 by u/xxx",
        ratelimit_seconds=300,
    )

Let's say your bot posts a comment to Reddit every 30s and Reddit returns the ratelimit
error: ``"You're doing that too much. Try again in 3 minutes."``. PRAW will wait for 181
seconds since 181 seconds is less than the configured ``ratelimit_seconds`` of 300
seconds. However, if Reddit returns the ratelimit error: ``"You're doing that too much.
Try again in 6 minutes."``, PRAW will raise an exception since 360 seconds is greater
than the configured ``ratelimit_seconds`` of 300 seconds.

.. |ratelimit_header| replace:: ``X-Ratelimit-*`` headers

.. |ratelimit_seconds| replace:: ``ratelimit_seconds`` configuration setting (default:
    5s)

.. _ratelimit_header: https://github.com/reddit-archive/reddit/wiki/API#rules

.. _ratelimit_seconds: https://praw.readthedocs.io/en/stable/getting_started/configuration/options.html#miscellaneous-configuration-options
