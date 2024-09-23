Logging in PRAW
===============

It is occasionally useful to observe the HTTP requests that PRAW is issuing. To do so
you have to configure and enable logging.

Add the following to your code to log everything available:

.. code-block:: python

    import logging

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    for logger_name in ("praw", "prawcore"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

Or you can use the following to write the logs to a file for longer running bots or
scripts when you need to look back at what the bot did hours ago.

.. code-block:: python

    import logging

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    file_handler = logging.handlers.RotatingFileHandler(
        "praw_log.txt", maxBytes=1024 * 1024 * 16, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    for logger_name in ("praw", "prawcore"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

When properly configured, HTTP requests that are issued should produce output similar to
the following:

.. code-block:: text

    Fetching: GET https://oauth.reddit.com/api/v1/me at 1691743155.4952002
    Data: None
    Params: {'raw_json': 1}
    Response: 200 (876 bytes) (rst-45:rem-892:used-104 ratelimit) at 1691743156.3847592

Furthermore, any API ratelimits from POST actions that are handled will produce a log
entry with a message similar to the following message:

.. code-block:: text

    Rate limit hit, sleeping for 5.5 seconds

For more information on logging, see :py:class:`logging.Logger`.
