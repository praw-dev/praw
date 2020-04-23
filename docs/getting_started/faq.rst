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
will last for longer than an hour. Refer to :ref:`2FA` and :ref:`code_flow` in
order to use the respective auth methods.

.. _faq3:

Q: Some options (like getting moderator logs from r/mod) keep on timing out.
How can I extend the timeout?

A: Set the timeout config option or initialize :class:`.Reddit` with a timeout
of your choosing.