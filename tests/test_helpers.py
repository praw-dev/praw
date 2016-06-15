"""Tests for helper functions."""

from __future__ import print_function, unicode_literals
from praw.helpers import chunk_sequence
from .helper import PRAWTest


class HeleperTest(PRAWTest):
    def test_chunk_sequence(self):
        s = 'abcdefgh'
        self.assertEqual(chunk_sequence(s, 4, allow_incomplete=True),
                         ['abcd', 'efgh'])
        self.assertEqual(chunk_sequence(s, 3, allow_incomplete=True),
                         ['abc', 'def', 'gh'])
        self.assertEqual(chunk_sequence(s, 3, allow_incomplete=False),
                         ['abc', 'def'])
        self.assertEqual(chunk_sequence(s, 10, allow_incomplete=True),
                         ['abcdefgh'])
        self.assertEqual(chunk_sequence(s, 10, allow_incomplete=False),
                         [])

        # Returned sequence is same type as input
        s = ['a', 'b', 'c']
        self.assertEqual(chunk_sequence(s, 2, allow_incomplete=True),
                         [['a', 'b'], ['c']])
        self.assertEqual(chunk_sequence(s, 2, allow_incomplete=False),
                         [['a', 'b']])
