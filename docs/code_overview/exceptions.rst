Exceptions in PRAW
==================

In addition to exceptions under the ``praw.exceptions`` namespace shown below,
exceptions might be raised that inherit from
``prawcore.PrawcoreException``. Please see the following resource for
information on those exceptions:
https://github.com/praw-dev/prawcore/blob/master/prawcore/exceptions.py

Base Exception
--------------

.. autoclass:: praw.exceptions.PRAWException
   :inherited-members:

Server Exceptions
-----------------

.. automodule:: praw.exceptions.api
   :inherited-members:

Client Exceptions
-----------------

.. automodule:: praw.exceptions.client
   :inherited-members: