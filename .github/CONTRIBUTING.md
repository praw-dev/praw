# Guidelines for Contributing

## Code of Conduct

This project is released with a
[Contributor Code of Conduct](https://github.com/praw-dev/praw/blob/master/CODE_OF_CONDUCT.md). By
participating in this project you agree to abide by its terms.

## Creating an Issue

0. Please do not create issues for questions you have. The appropriate location
   for such questions is [/r/redditdev](https://www.reddit.com/r/redditdev/) or
   in the [praw-dev/praw](https://gitter.im/praw-dev/praw) channel on gitter.

0. Please check the
   [Unreleased](https://github.com/praw-dev/praw/blob/master/CHANGES.rst#unreleased)
   section of the latest changelog before filing an issue as it is possible the
   issue has already been resolved.

0. Please use GitHub's issue search feature to look for already reported issues
   before reporting your own.

## Responding to Issues

One of the simplest ways to help with PRAW is by answering others'
questions. When responding, always be positive. While something may be obvious
to you, it likely is not to the person asking the question.

## Pull Request Creation

0. If you are fixing an already filed issue, please indicate your intentions by
   commenting on the issue. This act will hopefully minimize any duplicate
   work.

0. Prior to creating a pull request run the `pre_push.sh` script. This script
   depends on the tools `black` `flake8`, `pylint`, and `pydocstyle`. They can
   be installed via `pip install black flake8 pydocstyle pylint`.

0. Add yourself as a contributor to the ``AUTHORS.rst``.

0. Once pushed, ensure that your TravisCI build succeeds. Travis will error
   before running any tests if there are _any_ `flake8` or `pydocstyle`
   issues. Resolve any issues by updating your pull request.

0. Ensure that your change has complete test coverage. Tests on methods that do
   not require fetching data from Reddit, e.g., method argument validation,
   should be saved as a unit test. Tests that hit Reddit's servers should be an
   integration test and all network activity should be recorded via Betamax.

0. Feel free to check on the status of your pull request periodically by adding
   a comment.

## Becoming a Team Member

The PRAW team is always interested in expanding PRAW's active team member base
with proven contributors. If you are interested please let us know, In general,
we would like to see you push a number of contributions before we add you on.


## Style Recommendations

To keep PRAW's source consistent, all contribution code must pass the
`pre_push.sh` script. Travis CI will enforce the passing of the automated
tests, as well as style checking done via the `pre_push.sh` script. While this
script helps ensure consistency with much of PEP8 and PEP257 there are a few
things that it does not enforce. Please look over the following list:

### Import Statement Order

From PEP8: https://www.python.org/dev/peps/pep-0008/#imports

List only a single import per line, and group imports by standard library
imports, third party imports and application imports.

__Additions__:

* List `from package ... import ...` imports prior to entire package `import
  ...` type statements.

* Lexicographically sort imports. This process has the intended side effect
  that top-level relative packages will be imported prior to lower-level
  packages.

Example:

```python
from os.path import abspath, join
import sys
import traceback

from prawcore import NotFound
import requests

from ...const import API_PATH
from ..listing.mixins import SubmissionListingMixin
from .base import RedditBase
from .mixins import UserContentMixin
```

### Method Order within a Class

* Group method names by type and order the groups like so:

    * Static methods

    * Class methods

    * Properties

    * Instance methods

* Within each grouping method names should be sorted lexicographically.

Example:

```python
class Example(object):

    @staticmethod
    def a_static_method(): pass

    @staticmethod
    def another_static_method(): pass

    @classmethod
    def some_class_method(cls): pass

    @property
    def name(self): pass

    def __init__(self): pass

    def instance_method(self): pass
```

### See Also

https://praw.readthedocs.io/en/latest/package_info/contributing.html
