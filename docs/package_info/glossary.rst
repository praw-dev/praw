##########
 Glossary
##########

.. _access_token:

- ``Access Token``: A temporary token to allow access to the Reddit API. Lasts for one
  hour.

.. _fullname:

- ``Fullname``: The fullname of an object is the object's type followed by an underscore
  and its base-36 id. An example would be ``t3_1h4f3``, where the ``t3`` signals that it
  is a :class:`.Submission`, and the submission ID is ``1h4f3``.

  Here is a list of the six different types of objects returned from Reddit:


  - ``t1`` These objects represent :class:`.Comment`\ s.


  - ``t2`` These objects represent :class:`.Redditor`\ s.


  - ``t3`` These objects represent :class:`.Submission`\ s.


  - ``t4`` These objects represent :class:`.Message`\ s.


  - ``t5`` These objects represent :class:`.Subreddit`\ s.


  - ``t6`` These objects represent :class:`.Trophy`\ s.

.. _websocket:

- ``Websocket``: A special connection type that supports both a client and a server (the
  running program and Reddit respectively) sending multiple messages to each other.
  Reddit uses websockets to notify clients when an image or video submission is
  completed, as well as certain types of asset uploads, such as subreddit banners.
