"""PRAW Test Suite."""

from __future__ import print_function, unicode_literals
import unittest


def travis_suite():
    """Return a TestSuite including tests to run on travis.

    Until all tests are betamax compatible, this subset of tests is necessary.

    """
    load = unittest.defaultTestLoader.loadTestsFromNames
    tests = load(['tests.test_unauthenticated_reddit',
                  'tests.test_oauth2_reddit',
                  'tests.old.ModeratorSubredditTest.test_mod_mail_send'])
    return tests
