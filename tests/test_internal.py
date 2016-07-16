from __future__ import print_function, unicode_literals
from six.moves import reload_module
import sys
from types import ModuleType
from praw.internal import _to_reddit_list
from .helper import PRAWTest, betamax


def patch_openpyssl(version):
    """Wrapper to patch a pyOpenSSL version.

       - Calls the function with praw's internal module as the second argument.
       - version defines the version string to patch in
       - Reverts OpenSSL back to it's normal state after the function call if
         it exists on the system, otherwise, deletes the patched module from
         sys.modules
    """
    def factory(func):
        def wrapped(obj):
            try:
                import OpenSSL as RealOpenSSL
            except ImportError:
                RealOpenSSL = None
            FakeOpenSSL = ModuleType(str('openssl'))
            FakeOpenSSL.__version__ = version
            sys.modules['OpenSSL'] = FakeOpenSSL
            from praw import internal
            reload_module(internal)

            retval = func(obj, internal)
            del sys.modules['OpenSSL']
            if RealOpenSSL is not None:
                sys.modules['OpenSSL'] = RealOpenSSL
            return retval
        return wrapped
    return factory


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

    @betamax()
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

    @patch_openpyssl('0.14')
    def test__warn_pyopenssl_invalid_version(self, internal):
        self.assertWarningsRegexp("0\.14", RuntimeWarning,
                                  internal._warn_pyopenssl)

    @patch_openpyssl('0.15')
    def test__warn_pyopenssl_valid_version(self, internal):
        self.assertNoWarnings(internal._warn_pyopenssl)

    @patch_openpyssl('16.0.1.dev001')
    def test__warn_pyopenssl_valid_version_dev(self, internal):
        self.assertNoWarnings(internal._warn_pyopenssl)
