import unittest
from praw.decorator_helpers import _make_func_args


class DecoratorTest(unittest.TestCase):
    def test_make_func_args(self):
        def foo(arg1, arg2, arg3):
            pass

        def bar(arg1, arg2, arg3, *args, **kwargs):
            pass

        arglist = ['arg1', 'arg2', 'arg3']

        self.assertEqual(_make_func_args(foo), arglist)
        self.assertEqual(_make_func_args(bar), arglist)
