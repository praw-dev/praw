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

class SaveableTestCase(unittest.TestCase):
    def setUp(self):
        self.r = Reddit()
        self.r.login("PyAPITestUser2", 1111)
        self.sub = self.r.get_subreddit("PyAPISandbox")
        self.sample_submission = self.sub.get_hot(limit=1)[0]

    def tearDown(self):
        self.sample_submission.unsave()

    def test_save_adds_to_my_saved_links(self):
        self.sample_submission.save()
        self.assertIn(self.sample_submission, self.r.get_saved_links())

    def test_unsave_not_in_saved_links(self):
        self.sample_submission.unsave()
        self.assertNotIn(self.sample_submission, self.r.get_saved_links())

class CommentTestCase(unittest.TestCase):
    def setUp(self):
        r = Reddit()
        self.comments = r.get_front_page(limit=1)[0].comments

    def test_comments_contains_no_noncomment_objects(self):
        self.assertFalse([item for item in self.comments if not
                         isinstance(item, Comment)])

urljoin_suite = unittest.TestLoader().loadTestsFromTestCase(URLJoinTestCase)
reddit_suite = unittest.TestLoader().loadTestsFromTestCase(RedditTestCase)

if __name__ == "__main__":
    unittest.main(verbosity=2)
