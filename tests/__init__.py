"""PRAW Test Suite."""

from __future__ import print_function, unicode_literals
import unittest


def travis_suite():
    """Return a TestSuite including tests to run on travis.

    Until all tests are betamax compatible, this subset of tests is necessary.

    """
    import glob
    return unittest.defaultTestLoader.loadTestsFromNames(
        x[:-3].replace('/', '.') for x in glob.glob('tests/test_*.py'))
