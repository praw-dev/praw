.. _reddit_initialization:

Keyword Arguments to :class:`.Reddit`
=====================================

Most of PRAW's documentation will demonstrate configuring PRAW through the use
of keyword arguments when initializing instances of :class:`.Reddit`. All of
the :ref:`configuration_options` can be specified using a keyword argument of
the same name.

For example, if we wanted to explicitly pass the information for ``bot3``
defined in :ref:`the praw.ini custom site example <custom_site_example>`
without using the ``bot3`` site, we would initialize :class:`.Reddit` as:

.. code-block:: python

   reddit = praw.Reddit(client_id='SI8pN3DSbt0zor',
                        client_secret='xaxkj7HNh8kwg8e5t4m6KvSrbTI',
                        password='1guiwevlfo00esyy',
                        user_agent='testscript by /u/fakebot3',
                        username='fakebot3')
