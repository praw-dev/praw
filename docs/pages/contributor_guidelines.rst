.. _contributor_guidelines:

Contributor Guidelines
======================

PRAW gladly welcomes new contributions. As with most larger projects, we have
an established consistent way of doing things. A consistent style increases
readability, decreases bug-potential and makes it faster to understand how
everything works together.

PRAW follows :PEP:`8` and :PEP:`257`. You can use ``lint.sh`` to test for
compliance with these PEP's. The following are PRAW-specific guidelines in to
those PEP's.

Code
----

* Objects are sorted alphabetically.
* Things should maintain the same name throughout the code. \*\*kwargs should
  never be \*\*kw.
* Things should be stored in the same data structure throughout the code.

Testing
-------

* If you're adding functionality, either add tests or suggest how it might be
  tested.
* In assertEquals, the first value should be the value you're testing and the
  second the known value.

Documentation
-------------

* All publicly available functions, classes and modules should have a
  docstring.
* Use correct terminology. A subreddits name is something like ' t5_xyfc7'.
  The correct term for a subreddits "name" like
  `python <http://www.reddit.com/r/python>`_ is its display name.
* When referring to any reddit. Refer to it as 'reddit'. When you are speaking
  of the specific reddit instance with the website reddit.com, refer to it as
  'reddit.com'. This helps prevent any confusion between what is universally
  true between all reddits and what specifically applies to the most known
  instance.
