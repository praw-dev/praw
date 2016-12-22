Contributing to PRAW
====================

PRAW gladly welcomes new contributions. As with most larger projects, we have
an established consistent way of doing things. A consistent style increases
readability, decreases bug-potential and makes it faster to understand how
everything works together.

PRAW follows :PEP:`8` and :PEP:`257`. You can use ``pre_push.py`` to test for
compliance with these PEP's and a few other checks. The following are
PRAW-specific guidelines in addition to those PEP's.

Code
----

* Objects are sorted alphabetically.
* Things should maintain the same name throughout the code.
* Things should be stored in the same data structure throughout the code.
* ``**kwargs`` should be given descriptive names.

Testing
-------

* All additions to the code require 100% test coverage. If you're not sure
  where to begin with testing, ask.

Documentation
-------------

* All publicly available functions, classes and modules should have a
  docstring.
* Use correct terminology. A subreddits name is something like ' t5_xyfc7'.
  The correct term for a subreddit's "name" like
  `python <https://www.reddit.com/r/python>`_ is its display name.
