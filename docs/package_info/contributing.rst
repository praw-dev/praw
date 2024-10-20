Contributing to PRAW
====================

PRAW gladly welcomes new contributions. As with most larger projects, we have an
established consistent way of doing things. A consistent style increases readability,
decreases bug-potential and makes it faster to understand how everything works together.

Setting Up Your Development Environment
---------------------------------------

This section will cover the recommended steps to get you started with contributing to
PRAW.

Create a Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is strongly recommended to use a virtual environment to isolate your development
environment. This is a good idea because it will make managing the needed dependencies
and their versions much easier. For more information, see the `venv documentation`_.
Assuming you have the minimum Python version required for PRAW, you can create a virtual
environment with the following commands from the root of the cloned project directory:

.. code-block:: bash

    python3 -m venv .venv

Next you need to activate the virtual environment. This is done by running the
following:

**MacOS/Linux**:

.. code-block:: bash

    source .venv/bin/activate

**Windows Command Prompt**

.. code-block:: bat

    .venv\Scripts\activate.bat

.. _install_dev_deps:

Install Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, you will need to install the dependencies development dependencies. This is done
by running the following:

.. code-block:: bash

    pip install -e .[dev]

.. important::

    If you are using ``zsh`` for your shell, you will need to double-quote ``.[dev]``
    like so:

    .. code-block:: zsh

        pip install -e ".[dev]"

.. note::

    The ``-e`` tells pip to install PRAW in an editable state. This will allow for
    easier testing and debugging. The ``[dev]`` extra will install all development
    dependencies. This includes the dependencies for both linting and testing.

Code Style
----------

Linting
~~~~~~~

PRAW follows :PEP:`8` and :PEP:`257` and some :ref:`praw_specific_guidelines`.
pre-commit_ is used to manage a suite of pre-commit hooks that enforce conformance with
these PEPs along with several other checks. Additionally, the ``pre_push.py`` script can
be used to run the full pre-commit suite and the docs build prior to submitting a pull
request.

.. note::

    In order to use the pre-commit hooks and the ``pre_push.py`` dependencies, you must
    either install the development dependencies as outlined in the
    :ref:`install_dev_deps` section above or you must install the ``[lint]`` extra
    manually:

    .. code-block:: bash

        pip install -e .[lint]

To install the pre-commit hooks to automatically run when you commit, run the following:

.. code-block:: bash

    pre-commit install

To run all the needed checks and to ensure the docs build correctly, run the following:

.. code-block:: bash

    ./pre_push.py

.. _praw_specific_guidelines:

PRAW Specific Style Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following are PRAW-specific guidelines in addition to the PEPs specified in
Linting_:

- Within a single file classes are sorted alphabetically where inheritance permits.
- Within a class, methods are sorted alphabetically within their respective groups with
  the following as the grouping order:

  - Static methods
  - Class methods
  - Cached properties
  - Properties
  - Instance Methods

- Use descriptive names for the catch-all keyword argument, e.g., ``**other_options``
  rather than ``**kwargs``.
- Methods with more than one argument should have all its arguments sorted
  alphabetically and marked as keyword only with the ``*`` argument. For example:

  .. code-block:: python

      class ExampleClass:
          def example_method(
              self,
              *,
              arg1,
              arg2,
              optional_arg1=None,
          ): ...

  There is some exceptions to this:

  - If it’s clear without reading documentation what the mandatory positional arguments
    would be and their order, then they can be positional arguments. For example:

    .. code-block:: python

        class ExampleClass:
            def pair(self, left, right): ...

  - If there is one or two mandatory arguments and some optional arguments, then the
    mandatory arguments may be positional (as long as it adheres to the previous point),
    however, the optional arguments must be made keyword only and sorted alphabetically.
    For example:

    .. code-block:: python

        class Subreddit:
            def submit(
                self,
                title,
                *,
                collection_id=None,
                discussion_type=None,
                draft_id=None,
                flair_id=None,
                flair_text=None,
                inline_media=None,
                nsfw=False,
                resubmit=True,
                selftext=None,
                send_replies=True,
                spoiler=False,
                url=None,
            ): ...

Testing
-------

Contributions to PRAW requires 100% test coverage as reported by Coveralls_. If you know
how to add a feature, but aren't sure how to write the necessary tests, please open a
pull request anyway so we can work with you to write the necessary tests.

Running the Test Suite
~~~~~~~~~~~~~~~~~~~~~~

`GitHub Actions`_ automatically runs all updates to known branches and pull requests.
However, it's useful to be able to run the tests locally. The simplest way is via:

.. code-block:: bash

    pytest

Without any configuration or modification, all the tests should pass. If they do not,
please file a bug report.

Adding and Updating Integration Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PRAW's integration tests utilize Betamax_ to record an interaction with Reddit. The
recorded interaction is then replayed for subsequent test runs.

To safely record a cassette without leaking your account credentials, PRAW utilizes a
number of environment variables which are replaced with placeholders in the cassettes.
The environment variables are (listed in bash export format):

.. code-block:: bash

    export prawtest_client_id=myclientid
    export prawtest_client_secret=myclientsecret
    export prawtest_password=mypassword
    export prawtest_test_subreddit=test
    export prawtest_username=myusername
    export prawtest_user_agent=praw_pytest

By setting these environment variables prior to running ``pytest``, when adding or
updating cassettes, instances of ``mypassword`` will be replaced by the placeholder text
``<PASSWORD>`` and similar for the other environment variables.

To use a refresh token instead of username/password set ``prawtest_refresh_token``
instead of ``prawtest_password`` and ``prawtest_username``.

When adding or updating a cassette, you will likely want to force requests to occur
again rather than using an existing cassette. The simplest way to rebuild a cassette is
to first delete it, and then rerun the test suite.

Please always verify that only the requests you expect to be made are contained within
your cassette.

There are a few pytest markers that can be used to control how cassettes are recorded or
used.

- ``@pytest.mark.add_placeholder``: Allows you to add custom placeholders to the
  cassette. This can be useful when you want to record dynamic or generated data, but do
  not want it to be saved in the cassette. This marker takes at least one keyword
  argument and can be applied to a test class or individual test methods. It can also be
  applied multiple times.
- ``@pytest.mark.cassette_name``: Allows you to set the cassette name. This can be
  useful when you want to use a cassette that was recorded by another test.
- ``@pytest.mark.recorder_kwargs``: Allows you to pass additional arguments to the
  recorder. This can be useful if you need to specify parameters for the
  ``Betamax.use_cassette`` method. Like the ``add_placeholder`` marker, this marker can
  be applied to a test class or individual test methods and can be applied multiple
  times.

Examples:

.. code-block:: python

    @pytest.mark.recorder_kwargs(allow_playback_repeats=True)
    class TestClass:
        @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
        def test_example(self): ...

        @pytest.mark.cassette_name("TestClass.test_example")
        @pytest.mark.recorder_kwargs(match_requests_on=["uri", "method", "body"])
        def test_example__different_assertion(self): ...

        @pytest.mark.add_placeholder(generated_data_a=generate_data_a())
        @pytest.mark.add_placeholder(generated_data_b=generate_data_b())
        def test_example__with_generated_placeholders(self): ...

Documentation
-------------

- All publicly available functions, classes, and modules should have a docstring.
- All documentation files and docstrings should be linted and formatted by
  ``docstrfmt``.
- Use correct terminology. A subreddit's fullname is something like ``t5_xyfc7``. The
  correct term for a subreddit's "name" like ``python`` for `r/python`_ is its display
  name.

Static Checker
~~~~~~~~~~~~~~

PRAW's test suite comes with a checker tool that can warn you of using incorrect
documentation styles (using ``.. code::`` instead of ``.. code-block::``, using ``/r/``
instead of ``r/``, etc.). This is run automatically by the pre-commit hooks and the
``pre_push.py`` script.

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

For feature additions, bug fixes, or code removal please add an appropriate entry to
``CHANGES.rst``. If the ``Unreleased`` section does not exist at the top of
``CHANGES.rst`` please add it. See `commit 280525c16ba28cdd69cdbb272a0e2764b1c7e6a0`_
for an example.

See Also
--------

Please also read the `Contributing Guidelines`_

.. _betamax: https://betamax.readthedocs.io/en/latest

.. _commit 280525c16ba28cdd69cdbb272a0e2764b1c7e6a0: https://github.com/praw-dev/praw/commit/280525c16ba28cdd69cdbb272a0e2764b1c7e6a0

.. _contributing guidelines: https://github.com/praw-dev/praw/blob/master/.github/CONTRIBUTING.rst

.. _coveralls: https://coveralls.io/github/praw-dev/praw

.. _github actions: https://github.com/praw-dev/praw/actions

.. _pre-commit: https://pre-commit.com

.. _r/python: https://www.reddit.com/r/python

.. _venv documentation: https://docs.python.org/3/library/venv.html
