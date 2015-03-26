# Guidelines for Contributing

## Issue Filing

0. Please do not create issues for questions you have. The appropriate location
   for such questions is [/r/redditdev](https://www.reddit.com/r/redditdev/).

0. Please check the
   [Unreleased](https://github.com/praw-dev/praw/blob/master/CHANGES.rst#unreleased)
   section of the latest changelog before filing an issue as it's possible the
   issue has already been resolved.

0. Please use GitHub's search feature to look for already reported issues
   before reporting your own.

## Pull Request Creation

0. If you are fixing an already filed issue, please indicate your intentions by
   commenting on the issue. This act will hopefully minimize any duplicate
   work.

0. Prior to creating a pull request run the `lint.sh` script. This script
   depends on the tools `flake8`, `pylint`, and `pep257`. They can be installed
   via `pip install flake8 pylint pep257.

0. Once pushed, ensure that your TravisCI build succeeds. Travis will error
   before running any tests if there are _any_ `flake8` or `pep257`
   errors. Resolve any issues by updating your pull request. _Note_: Some tests
   are simply flakey and may not pass for you. If you suspect that is the case
   please add a comment to the pull request indicating your suspicion.

0. Feel free to check on the status of your pull request periodically by adding
   a comment.

## Becoming a Maintainer

PRAW is looking for one or two people to regularly handle issues, and integrate
others' pull requests. Interested parties should make their intentions known by
resolving a few issues via pull requests.

---

Some contents of this file were adapted from github3.py
[CONTRIBUTING.rst](https://github.com/sigmavirus24/github3.py/blob/master/CONTRIBUTING.rst).