Change Log
==========

4.0.0aX
-------

PRAW 4 introduces significant breaking changes. The numerous changes are not
listed here, only the feature removals. Please read through
:doc:`/pages/getting_started` to help with updating your code to PRAW 4. If you
require additional help please ask on `/r/redditdev
<https://www.reddit.com/r/redditdev>`_ or in the `praw-dev/praw
<https://gitter.im/praw-dev/praw>`_ channel on gitter.

**Removed**

* Removed :class:`.Reddit`'s ``login`` method. Authentication must be done
  through OAuth.
* Removed `praw-multiprocess` as this functionality is no longer needed with
  PRAW 4.

For changes prior to version 4.0 please see: `3.4.0 changelog
<http://praw.readthedocs.io/en/v3.4.0/pages/changelog.html>`_
