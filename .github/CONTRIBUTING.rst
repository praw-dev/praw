Guidelines for Contributing
===========================

Code of Conduct
---------------

This project is released with a `Contributor Code of Conduct`_. By participating in this
project you agree to abide by its terms.

Creating an Issue
-----------------

1. Please do not create issues for questions you have. The appropriate location for such
   questions is `r/redditdev`_ or via Slack_.
2. Please check the Unreleased_ section of the latest changelog before filing an issue
   as it is possible the issue has already been resolved.
3. Please use GitHub's issue search feature to look for already reported issues before
   reporting your own.

Responding to Issues
--------------------

One of the simplest ways to help with PRAW is by answering others questions. When
responding, always be positive. While something may be obvious to you, it likely is not
to the person asking the question.

Creating Pull Requests
----------------------

1. If you are fixing an already filed issue, please indicate your intentions by
   commenting on the issue. This act will hopefully minimize any duplicate work.
2. Before committing, make sure to install pre-commit_ and the pre-commit hooks, which
   ensures any new code conforms to our quality and style guidelines. To do so, install
   the linting dependencies with ``pip install praw[lint]``, then by the hooks with
   ``pre-commit install``. They will now run automatically every time you commit. If one
   of the hooks changes one or more files, the commit will automatically abort, so you
   can double-check the changes. If everything looks good try committing again.
3. Prior to creating a pull request, run the ``pre_push.py`` script. This runs the
   pre-commit suite on all files, as well as builds the docs. You'll need to have
   installed the linting dependencies first (see previous).
4. Add yourself as a contributor to appropriate section in the ``AUTHORS.rst`` file.
5. Once pushed, ensure that your GitHub Actions build succeeds. If this is your first
   time contributing to the repository, you will need to wait for a team member to allow
   GitHub Actions to run. GitHub Actions will error if there are *any* linting or test
   failures. Resolve any issues by updating your pull request.
6. Ensure that your code change has complete test coverage. Tests on methods that do not
   require fetching data from Reddit, e.g., method argument validation, should be saved
   as a unit test. Tests that hit Reddit's servers will be an integration test and all
   network activity will be recorded via Betamax. The required packages can be installed
   with ``pip install praw[test]``.
7. Feel free to check on the status of your pull request periodically by adding a
   comment.

Becoming a Team Member
----------------------

The PRAW team is always interested in expanding PRAW's active team member base with
proven contributors. If you are interested, please let us know. In general, we would
like to see you push a number of contributions before we add you on.

Style Recommendations
---------------------

To keep PRAW's source consistent, all contribution code must pass the ``pre_push.py``
script. GitHub Actions will enforce the passing of the automated tests, as well as style
checking done via the ``pre_push.py`` script. While this script helps ensure consistency
with much of PEP8 and PEP257 there are a few things that it does not enforce. Please
look over the following list:

Method Order within a Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Group method names by type and order the groups like so:

  - Static methods
  - Class methods
  - Properties
  - Instance methods

- Within each grouping method names should be sorted lexicographically.

  Example:

  .. code-block:: python

      class Example(object):
          @staticmethod
          def a_static_method():
              pass

          @staticmethod
          def another_static_method():
              pass

          @classmethod
          def some_class_method(cls):
              pass

          @property
          def name(self):
              pass

          def __init__(self):
              pass

          def instance_method(self):
              pass

See Also
~~~~~~~~

Please also read through:
https://praw.readthedocs.io/en/latest/package_info/contributing.html

.. _contributor code of conduct: https://github.com/praw-dev/.github/blob/main/CODE_OF_CONDUCT.md

.. _pre-commit: https://pre-commit.com

.. _r/redditdev: https://redditdev.reddit.com

.. _slack: https://join.slack.com/t/praw/shared_invite/enQtOTUwMDcxOTQ0NzY5LWVkMGQ3ZDk5YmQ5MDEwYTZmMmJkMTJkNjBkNTY3OTU0Y2E2NGRlY2ZhZTAzMWZmMWRiMTMwYjdjODkxOGYyZjY

.. _unreleased: https://github.com/praw-dev/praw/blob/master/CHANGES.rst#unreleased
