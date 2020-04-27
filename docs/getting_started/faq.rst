Frequently Asked Questions
==========================

.. _faq1:

Q: How can I refresh a comment/subreddit/submission?

A: Directly calling the constructors will refresh the value:

.. code-block:: python

   reddit.comment(id=comment.id)
   reddit.subreddit(display_name=subreddit.display_name)
   reddit.submission(id=submission.id)

.. _faq2:

Q: Whenever I try to do anything, I get an ``invalid_grant`` error. What is the
cause?

A: This means that either you provided the wrong password and/or the account
you are trying to sign in with has 2FA enabled, and as such, either needs a 2FA
token or a refresh token to sign in. A refresh token is preferred, because then
you will not need to enter a 2FA token in order to sign in, and the session
will last for longer than an hour. Refer to :ref:`2FA` and :ref:`refresh_token`
in order to use the respective auth methods.

.. _faq3:

Q: Some options (like getting moderator logs from r/mod) keep on timing out.
How can I extend the timeout?

A: Set the timeout config option or initialize :class:`.Reddit` with a timeout
of your choosing.

.. _faq4:

Q: Help, I keep on getting redirected to ``/r/subreddit/login/``!

Q2: I keep on getting this exception!:

.. parsed-literal::

    Traceback (most recent call last):
      File "/usr/local/lib/python3.7/site-packages/praw/models/reddit/subreddit.py", line 1121, in traffic
        API_PATH["about_traffic"].format(subreddit=self)
      File "/usr/local/lib/python3.7/site-packages/praw/reddit.py", line 490, in get
        return self._objectify_request(method="GET", params=params, path=path)
      File "/usr/local/lib/python3.7/site-packages/praw/reddit.py", line 574, in _objectify_request
        data=data, files=files, method=method, params=params, path=path
      File "/usr/local/lib/python3.7/site-packages/praw/reddit.py", line 732, in request
        timeout=self.config.timeout,
      File "/usr/local/lib/python3.7/site-packages/prawcore/sessions.py", line 336, in request
        url=url,
      File "/usr/local/lib/python3.7/site-packages/prawcore/sessions.py", line 265, in _request_with_retries
        raise self.STATUS_EXCEPTIONS[response.status_code](response)
    prawcore.exceptions.Redirect: Redirect to /r/AskReddit/login/ (You may be trying to perform a non-read-only action via a 
    read-only instance.)

A: PRAW is most likely in read-only mode. This normally occurs when PRAW is
authenticated without a username and password or a refresh token. In order to perform
this action, the Reddit instance needs to be authenticated. See :ref:`oauth_options` to
see the available authentication methods.
