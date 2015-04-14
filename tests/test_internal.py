from __future__ import print_function, unicode_literals
from praw.internal import _to_reddit_list
from .helper import PRAWTest, betamax


class InternalTest(PRAWTest):
    def test__to_reddit_list(self):
        output = _to_reddit_list('hello')
        self.assertEqual('hello', output)

    def test__to_reddit_list_with_list(self):
        output = _to_reddit_list(['hello'])
        self.assertEqual('hello', output)

    def test__to_reddit_list_with_empty_list(self):
        output = _to_reddit_list([])
        self.assertEqual('', output)

    def test__to_reddit_list_with_big_list(self):
        output = _to_reddit_list(['hello', 'world'])
        self.assertEqual('hello,world', output)

    @betamax
    def test__to_reddit_list_with_object(self):
        output = _to_reddit_list(self.r.get_subreddit(self.sr))
        self.assertEqual(self.sr, output)

    def test__to_reddit_list_with_object_in_list(self):
        obj = self.r.get_subreddit(self.sr)
        output = _to_reddit_list([obj])
        self.assertEqual(self.sr, output)

    def test__to_reddit_list_with_mix(self):
        obj = self.r.get_subreddit(self.sr)
        output = _to_reddit_list([obj, 'hello'])
        self.assertEqual("{0},{1}".format(self.sr, 'hello'), output)
