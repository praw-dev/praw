.. _contributor_guidelines:

Contributor Guidelines
======================

PRAW gladly welcomes new contributions. As with most longer projects, we have
an established way of doing things around here. And we'd like it to keep it
that way because having a consistent style increases readability, decreases
bug-potential and makes it faster to understand how everything works together.

The more you follow these guidelines, the quicker your pull requests will go
through and the easier our jobs becomes. But don't be afraid to send in a
request that doesn't match everything.

Code
----

* Unless otherwise stated, PRAW will follow the :PEP:`257`
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

* Unless otherwise stated, PRAW will follow the :PEP:`257`
* All publicly available functions, classes and modules should have a
  docstring.
* Use the imperative form. Eg "Get the subreddit." not "Gets the subreddit."
   or "PRAW will get the subreddit."
* For one-liner docstrings, the entire string including opening and closing
  """" will be on the same line.
* For multi-line comments the one-liner summary will be on the line after the
  opening """ and the closing """ will be on the line after the last line of
  the docstring. Example


   """  
   Summary line. Sum its up.

   Longer explanation.  
   """  

* Use correct terminology. A subreddits name is something like ' t3_xyfc7'.
  The correct term for a subreddits "name" like
  `python <http://www.reddit.com/r/python>`_ is it's display name.
* When referring to any reddit. Refer to it as 'reddit'. When you are speaking
  of the specific reddit instance with the website reddit.com, refer to it as
  'reddit.com'. This helps prevent any confusion between what is universally
  true between all reddits and what specifically applies to the most known
  instance.
