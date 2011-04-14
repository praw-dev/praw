# This file is part of reddit_api.
# 
# reddit_api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# reddit_api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with reddit_api.  If not, see <http://www.gnu.org/licenses/>.

import itertools
import unittest
import warnings

import reddit
import util

def setUpModule():
    global r, r_auth, front_page, auth_front_page, link_post, self_post

    r = reddit.Reddit()
    r_auth = reddit.Reddit()
    r_auth.login("PyAPITestUser2", 1111)

    front_page = r.get_front_page(limit=25)
    auth_front_page = r_auth.get_front_page(limit=5)

    link_post = itertools.ifilterfalse(lambda s: s.is_self, front_page).next()
    self_post = itertools.ifilter(lambda s: s.is_self, front_page).next()

class MemoizeTestCase(unittest.TestCase):
    def setUp(self):
        from random import randint
        from itertools import count

        self._primary_key = count(1)
        @util.memoize
        def sample_func(*args, **kwargs):
            return sum(args)
        self.func = sample_func

class URLJoinTestCase(unittest.TestCase):
    def test_neither_slashed(self):
        self.assertEqual(util.urljoin("http://www.example.com", "subpath"),
                         "http://www.example.com/subpath")

    def test_base_slashed(self):
        self.assertEqual(util.urljoin("http://www.example.com/", "subpath"),
                         "http://www.example.com/subpath")

    def test_subpath_slashed(self):
        self.assertEqual(util.urljoin("http://www.example.com", "/subpath"),
                         "http://www.example.com/subpath")

    def test_both_slashed(self):
        self.assertEqual(util.urljoin("http://www.example.com/", "/subpath"),
                         "http://www.example.com/subpath")

class RedditTestCase(unittest.TestCase):
    def test_require_user_agent(self):
        if not reddit.DEBUG:
            self.assertRaises(reddit.APIException, reddit.Reddit, user_agent=None)

    def test_not_logged_in_when_initialized(self):
        self.assertEqual(r.user, None)

    def test_has_set_user_when_logged_in(self):
        self.assertIsInstance(r_auth.user, reddit.Redditor)

    def test_info_by_known_url_returns_known_id_link_post(self):
        found_links = r.info(link_post.url)
        self.assertIn(link_post, found_links)

    def test_info_by_self_url_raises_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            r.info(self_post.url)
            self.assertEqual(len(w), 1)
            self.assertEqual(w[-1].category, reddit.APIWarning)
            self.assertIn("self", str(w[-1].message))

    def test_info_by_url_also_found_by_id(self):
        found_links = r.info(link_post.url)
        for link in found_links:
            found_by_id = r.info(id=link.name)

            self.assertTrue(found_by_id)
            self.assertIn(link, found_by_id)

class SaveableTestCase(unittest.TestCase):
    def setUp(self):
        self.sample_submission = auth_front_page[0]

    def tearDown(self):
        self.sample_submission.unsave()

    def test_save_adds_to_my_saved_links(self):
        self.sample_submission.save()
        self.assertIn(self.sample_submission, r_auth.get_saved_links())

    def test_unsave_not_in_saved_links(self):
        self.sample_submission.unsave()
        self.assertNotIn(self.sample_submission, r_auth.get_saved_links())

class CommentTestCase(unittest.TestCase):
    def setUp(self):
        self.comments = front_page[0].comments

    def test_comments_contains_no_noncomment_objects(self):
        self.assertFalse([item for item in self.comments if not
                         isinstance(item, reddit.Comment)])

urljoin_suite = unittest.TestLoader().loadTestsFromTestCase(URLJoinTestCase)
reddit_suite = unittest.TestLoader().loadTestsFromTestCase(RedditTestCase)
saveable_suite = unittest.TestLoader().loadTestsFromTestCase(SaveableTestCase)
comment_suite = unittest.TestLoader().loadTestsFromTestCase(CommentTestCase)

if __name__ == "__main__":
    unittest.main(verbosity=2)
