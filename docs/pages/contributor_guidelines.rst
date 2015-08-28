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
* Use correct terminology. A subreddits name is something like ' t3_xyfc7'.
  The correct term for a subreddits "name" like
  `python <http://www.reddit.com/r/python>`_ is its display name.
* When referring to any reddit. Refer to it as 'reddit'. When you are speaking
  of the specific reddit instance with the website reddit.com, refer to it as
  'reddit.com'. This helps prevent any confusion between what is universally
  true between all reddits and what specifically applies to the most known
  instance.

EOL Issues
----------

Depending on the OS you are editing the source on, you may run into one of two
strange errors. Firstly, PRAW was written on a Unix-based OS. This means, that
the source's `EOLs` (End Of Lines) are the Unix `LF` character, a.k.a "\n"
a.k.a hex `0x0A`.

On Windows, `EOLs` are `CRLF`, which is `0x0D0A` ("\r\n") or if you are on a
Mac with OS-9 and earlier `EOLs` are `0x0D` ("\r"). More info on `EOLs` can be
found [here](http://bit.ly/1Ug8Xyo).

This can potentially pose one of two problems.

1. Your `EOLs` may not be automatically converted and your code will break PRAW.

2. Your editor automatically converts `EOLs`, at the cost that three invisible
    hexadecimal values are added at the beginning of a line, which also breaks
    PRAW. This can be determined to be the case if in the commit history on Github,
    the a line of a file is removed and re-added with no visible change.

The solutions to each are as follows:

1. You will have to find a editor that does converts `EOLs`, edit online, convert
    them manually with a hex editor.
2. Open the file in a hex editor such as [HxD](http://mh-nexus.de/en/hxd/), and
    you will see some characters at the beginning of the "corrupt" line that you would
    not see otherwise. Delete them, and re-commit to Github.
