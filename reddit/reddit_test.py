#!/usr/bin/env python

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
    global r, submissions

    print 'Initializing setup'
    r = reddit.Reddit('reddit_api')
    r.login("PyAPITestUser2", '1111')

    urls = {}
    urls['self'] = 'http://www.reddit.com/r/programming/comments/bn2wi/'
    urls['link'] = 'http://www.reddit.com/r/UCSantaBarbara/comments/m77nc/'

    submissions = dict((x, r.get_submission(urls[x])) for x in urls)
    print 'Done initializing setup'


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
        self.assertRaises(reddit.APIException, reddit.Reddit, user_agent=None)

#    def test_not_logged_in_when_initialized(self):
#        self.assertEqual(r.user, None)

    def test_has_set_user_when_logged_in(self):
        self.assertTrue(isinstance(r.user, reddit.Redditor))

    def test_info_by_known_url_returns_known_id_link_post(self):
        found_links = r.info(submissions['link'].url)
        self.assertTrue(submissions['link'] in found_links)

    def test_info_by_self_url_raises_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            r.info(submissions['self'].url)
            self.assertEqual(len(w), 1)
            self.assertEqual(w[-1].category, reddit.APIWarning)
            self.assertTrue("self" in str(w[-1].message))

    def test_info_by_url_also_found_by_id(self):
        found_links = r.info(submissions['link'].url)
        for link in found_links:
            found_by_id = r.info(id=link.name)

            self.assertTrue(found_by_id)
            self.assertTrue(link in found_by_id)


class SaveableTestCase(unittest.TestCase):
    def setUp(self):
        self.sample_submission = submissions['link']

    def tearDown(self):
        self.sample_submission.unsave()

    def test_save_adds_to_my_saved_links(self):
        self.sample_submission.save()
        self.assertTrue(self.sample_submission in r.get_saved_links())

    def test_unsave_not_in_saved_links(self):
        self.sample_submission.unsave()
        self.assertFalse(self.sample_submission in r.get_saved_links())


class CommentTestCase(unittest.TestCase):
    def setUp(self):
        self.comments = submissions['self'].comments

    def test_comments_contains_no_noncomment_objects(self):
        self.assertFalse([item for item in self.comments if not
                         (isinstance(item, reddit.Comment) or
                          isinstance(item, reddit.MoreComments))])


if __name__ == "__main__":
    setUpModule()
    unittest.main()
