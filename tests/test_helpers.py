"""Tests for helper functions."""

from __future__ import print_function, unicode_literals
from praw import helpers, objects
from .helper import PRAWTest, betamax


class HelperTest(PRAWTest):
    def setUp(self):
        super(HelperTest, self).setUp()
        self.verbosity = 0

    def test_bounded_set_fifo_unique(self):
        bounded_set = helpers.BoundedSet(20)
        for i in range(10):
            bounded_set.add(i)
        old_fifo = bounded_set._fifo[:]
        for n in range(10):
            bounded_set.add(n)
        self.assertEqual(old_fifo, bounded_set._fifo)

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

    def test_id_to_id36(self):
        alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
        alphabet_len = len(alphabet)
        for i in range(alphabet_len):
            self.assertEqual(alphabet.index(
                             helpers.convert_numeric_id_to_id36(i)), i)

    @betamax()
    def test_comment_stream(self):
        generator = helpers.comment_stream(self.r, "all",
                                           verbosity=self.verbosity)
        for i in range(10001):
            self.assertIsInstance(next(generator), objects.Comment)
