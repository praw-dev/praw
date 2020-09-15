Contributing to PRAW
====================

PRAW gladly welcomes new contributions. As with most larger projects, we have
an established consistent way of doing things. A consistent style increases
readability, decreases bug-potential and makes it faster to understand how
everything works together.

PRAW follows :PEP:`8` and :PEP:`257`. The ``pre_push.py`` script can be used to
test for compliance with these PEPs in addition to providing a few other
checks. The following are PRAW-specific guidelines in addition to those PEP's.

.. note::

    Python 3.6+ is needed to run the script.

.. note::

    In order to install the dependencies needed to run the script, you can
    install the ``[dev]`` package of praw, like so:

   .. code-block:: bash

       pip install praw[dev]

Code
----

* Within a single file classes are sorted alphabetically where inheritance permits.
* Within a class, methods are sorted alphabetically within their respective groups with
  the following as the grouping order:

  * Static methods
  * Class methods
  * Properties
  * Instance Methods

* Use descriptive names for the catch-all keyword argument. E.g., ``**other_options``
  rather than ``**kwargs``.

Testing
-------

Contributions to PRAW requires 100% test coverage as reported by `Coveralls
<https://coveralls.io/github/praw-dev/praw>`_. If you know how to add a feature, but
aren't sure how to write the necessary tests, please open a PR anyway so we can work
with you to write the necessary tests.

Running the Test Suite
~~~~~~~~~~~~~~~~~~~~~~

`Github Actions <https://github.com/praw-dev/praw/actions>`_ automatically runs all
updates to known branches and pull requests. However, it's useful to be able to run the
tests locally. The simplest way is via:

.. code-block:: bash

    pytest

Without any configuration or modification, all the tests should pass.

Adding and Updating Integration Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PRAW's integration tests utilize `Betamax <https://betamax.readthedocs.io/en/latest/>`_
to record an interaction with Reddit. The recorded interaction is then replayed for
subsequent test runs.

To safely record a cassette without leaking your account credentials, PRAW utilizes a
number of environment variables which are replaced with placeholders in the cassettes.
The environment variables are (listed in bash export format):

.. code-block:: bash

    export prawtest_client_id=myclientid
    export prawtest_client_secret=myclientsecret
    export prawtest_password=mypassword
    export prawtest_test_subreddit=reddit_api_test
    export prawtest_username=myusername
    export prawtest_user_agent=praw_pytest

By setting these environment variables prior to running ``python setup.py test``, when
adding or updating cassettes, instances of ``mypassword`` will be replaced by the
placeholder text ``<PASSWORD>`` and similar for the other environment variables.

To use tokens instead of username/password set ``prawtest_refresh_token`` instead of
``prawtest_password`` and ``prawtest_username``.

When adding or updating a cassette, you will likely want to force requests to occur
again rather than using an existing cassette. The simplest way to rebuild a cassette is
to first delete it, and then rerun the test suite.

Please always verify that only the requests you expect to be made are contained within
your cassette.

Documentation
-------------

* All publicly available functions, classes and modules should have a docstring.
* Use correct terminology. A subreddit's fullname is something like ``t5_xyfc7``. The
  correct term for a subreddit's "name" like `python <https://www.reddit.com/r/python>`_
  is its display name.

Static Checker
~~~~~~~~~~~~~~

PRAW's test suite comes with a checker tool that can warn you of using incorrect
documentation styles (using ``.. code-block::`` instead of ``.. code::``, using ``/r/``
instead of ``r/``, etc.).

.. autoclass:: tools.static_word_checks.StaticChecker
   :inherited-members:

Files to Update
---------------

AUTHORS.rst
~~~~~~~~~~~

For your first contribution, please add yourself to the end of the respective list in
the ``AUTHORS.rst`` file.

CHANGES.rst
~~~~~~~~~~~

For feature additions, bugfixes, or code removal please add an appropriate entry to
``CHANGES.rst``. If the ``Unreleased`` section does not exist at the top of
``CHANGES.rst`` please add it. See `commit 280525c16ba28cdd69cdbb272a0e2764b1c7e6a0
<https://github.com/praw-dev/praw/commit/280525c16ba28cdd69cdbb272a0e2764b1c7e6a0>`_ for
an example.

See Also
--------

Please also read through:
https://github.com/praw-dev/praw/blob/master/.github/CONTRIBUTING.md
