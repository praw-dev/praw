Logging in PRAW
===============

Occasionally it is useful to observe the HTTP requests that PRAW is issuing. To
do so you have to configure and enable logging.

To log everything available add the following to your code:

.. code-block:: python

   import logging

   handler = logging.StreamHandler()
   handler.setLevel(logging.DEBUG)
   logger = logging.getLogger('prawcore')
   logger.setLevel(logging.DEBUG)
   logger.addHandler(handler)

When properly configured HTTP requests that are issued should produce output
similar to the following:

.. code-block:: text

   Fetching: GET https://oauth.reddit.com/api/v1/me
   Data: None
   Params: {'raw_json': 1}
   Response: 200 (876 bytes)

For more information on logging, see :py:class:`logging.Logger`.
