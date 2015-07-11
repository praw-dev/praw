from __future__ import print_function, unicode_literals

import unittest
from praw.decorators import restrict_access


class DecoratorTest(unittest.TestCase):
    def test_require_access_failure(self):
        self.assertRaises(TypeError, restrict_access, scope=None,
                          oauth_only=True)
