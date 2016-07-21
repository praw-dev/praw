"""Tests for helper functions."""

from __future__ import print_function, unicode_literals
from praw import helpers, objects
from .helper import PRAWTest, betamax


class HelperTest(PRAWTest):
    def setUp(self):
        super(HelperTest, self).setUp()
        self.verbosity = 0

    def test_chunk_sequence(self):
        s = 'abcdefgh'
        self.assertEqual(helpers.chunk_sequence(s, 4, allow_incomplete=True),
                         ['abcd', 'efgh'])
        self.assertEqual(helpers.chunk_sequence(s, 3, allow_incomplete=True),
                         ['abc', 'def', 'gh'])
        self.assertEqual(helpers.chunk_sequence(s, 3, allow_incomplete=False),
                         ['abc', 'def'])
        self.assertEqual(helpers.chunk_sequence(s, 10, allow_incomplete=True),
                         ['abcdefgh'])
        self.assertEqual(helpers.chunk_sequence(s, 10,
                                                allow_incomplete=False),
                         [])

        # Returned sequence is same type as input
        s = ['a', 'b', 'c']
        self.assertEqual(helpers.chunk_sequence(s, 2, allow_incomplete=True),
                         [['a', 'b'], ['c']])
        self.assertEqual(helpers.chunk_sequence(s, 2, allow_incomplete=False),
                         [['a', 'b']])

    @betamax()
    def test_comment_stream(self):
        generator = helpers.comment_stream(self.r, "all",
                                           verbosity=self.verbosity)
        for i in range(10001):
            self.assertIsInstance(next(generator), objects.Comment)
