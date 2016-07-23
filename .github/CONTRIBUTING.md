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
   [Unreleased](https://github.com/praw-dev/praw/blob/praw4/CHANGES.rst#unreleased)
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
   depends on the tools `flake8`, `pylint`, and `pydocstyle`. They can be
   installed via `pip install flake8 pydocstyle pylint`.

0. Once pushed, ensure that your TravisCI build succeeds. Travis will error
   before running any tests if there are _any_ `flake8` or `pydocstyle`
   issues. Resolve any issues by updating your pull request.

0. Ensure that your change has complete test coverage. Tests on methods that do
   not require fetching data from Reddit, e.g., method argument validation,
   should be saved as a unit test. Tests that hit Reddit's servers should be an
   integration test and all network activity should be recorded via Betamax.

0. Feel free to check on the status of your pull request periodically by adding
   a comment.

## Becoming a Maintainer

PRAW's maintainers are always iterested in expanding PRAW's active maintainer
base with proven contributors. If you are interested please let us know, In
general, we would like to see you push forward a number of contributions before
we add you on.
