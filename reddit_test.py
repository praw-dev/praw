import unittest

from reddit import *

class URLJoinTestCase(unittest.TestCase):
    def test_neither_slashed(self):
        self.assertEqual(urljoin("http://www.example.com", "subpath"),
                         "http://www.example.com/subpath")

    def test_base_slashed(self):
        self.assertEqual(urljoin("http://www.example.com/", "subpath"),
                         "http://www.example.com/subpath")

    def test_subpath_slashed(self):
        self.assertEqual(urljoin("http://www.example.com", "/subpath"),
                         "http://www.example.com/subpath")

    def test_both_slashed(self):
        self.assertEqual(urljoin("http://www.example.com/", "/subpath"),
                         "http://www.example.com/subpath")

class RedditTestCase(unittest.TestCase):
    def setUp(self):
        self.r = Reddit()

    def test_require_user_agent(self):
        if not DEBUG:
            self.assertRaises(APIException, Reddit, user_agent=None)

    def test_not_logged_in_when_initialized(self):
        self.assertEqual(self.r.user, None)

urljoin_suite = unittest.TestLoader().loadTestsFromTestCase(URLJoinTestCase)
reddit_suite = unittest.TestLoader().loadTestsFromTestCase(RedditTestCase)

if __name__ == "__main__":
    unittest.main(verbosity=2)
