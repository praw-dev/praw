.. begin_changelog_intro

Change Log
==========

Read `/r/changelog <http://www.reddit.com/r/changelog>`_ to be notified of
upstream changes.

.. end_changelog_intro

.. begin_changelog_body

4.0.0a1
-------

**Added**

* Added ``reddit_url`` setting to ``praw.ini``.

**Changed**

* :class:`Redditor` no longer takes a ``handler`` argument.
* :class:`Redditor` no longer has a ``evict`` method.
* Removed instances of ``from __future__ import print_function`` as PRAW should
  not use ``print`` at all.
* Removed instances of ``from __future__ import unicode_literals``.
* ``praw.ini`` settings ``oauth_domain`` and ``oauth_https`` have been combined
  into ``oauth_url``.

**Removed**

* Removed ``api_domain`` setting from ``praw.ini``.
* Removed ``api_request_delay`` setting from ``praw.ini``.
* Removed ``cache_timeout`` setting from ``praw.ini``.
* Removed ``output_chars_limit`` setting from ``praw.ini``.
* Removed :class:`Redditor` ``login`` method. Authentication must be done
  through OAuth.
* Removed all handlers in ``praw.handlers``.
* Removed `praw-multiprocess` as this functionality is no longer needed with
  PRAW4.
* Removed ``restrict_access`` decorator. While attempting to fail early is
  nice, it's not worth the additional code.

For changes prior to version 4.0 please see: `3.4.0 changelog
<http://praw.readthedocs.org/en/v3.4.0/pages/changelog.html>`_

.. end_changelog_body
