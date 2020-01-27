Interpting Subreddit Traffic
============================

PRAW is able to get subreddit traffic stats for a subreddit that is moderated
by the authenticated user, or get traffic stats for a subreddit that has made
their traffic stats public. However, the data is returned in a dict which
contains a list of lists of values, which is hard to interpt. Here, a program
is made that takes the data from a subreddit's traffic, and then prints the
data in an ASCII table.

.. literalinclude:: ../examples/display_traffic_stats.py
   :language: python