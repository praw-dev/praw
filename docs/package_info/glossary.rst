Glossary
========

.. _access_token:

* ``Access Token``: A temporary token to allow access to the Reddit API. Lasts for one
  hour.

.. _creddit:

* ``Creddit``: Back when the only award was ``Reddit Gold``, a creddit was equal to one
  month of Reddit Gold. Creddits have been converted to ``Reddit Coins``. See :ref:`this
  <gild>` for more info about the old Reddit Gold system.

.. _fullname:

* ``Fullname``: The fullname of an object is the object's type followed by an underscore
  and its base-36 id. An example would be ``t3_1h4f3``, where the ``t3`` signals that it
  is a :class:`.Submission`, and the submission ID is ``1h4f3``.

  Here is a list of the six different types of objects returned from reddit:

  .. _fullname_t1:

  - ``t1`` These object represent :class:`.Comment`\ s.

  .. _fullname_t2:

  - ``t2`` These object represent :class:`.Redditor`\ s.

  .. _fullname_t3:

  - ``t3`` These object represent :class:`.Submission`\ s.

  .. _fullname_t4:

  - ``t4`` These object represent :class:`.Message`\ s.

  .. _fullname_t5:

  - ``t5`` These object represent :class:`.Subreddit`\ s.

  .. _fullname_t6:

  - ``t6`` These object represent ``Award``\ s, such as ``Reddit Gold`` or
    ``Reddit Silver``.

.. _gild:

* ``Gild``: Back when the only award was ``Reddit Gold``, gilding a post meant awarding
  one month of Reddit Gold. Currently, gilding means awarding one month of ``Reddit
  Platinum``, or giving a ``Platinum`` award.

.. _websocket:

* ``Websocket``: A special connection type that supports both a client and a server (the
  running program and reddit respectively) sending multiple messages to each other.
  Reddit uses websockets to notify clients when an image or video submission is
  completed, as well as certain types of asset uploads, such as subreddit banners. If a
  client does not connect to the websocket in time, the client will not be notified of
  the completion of such uploads.
