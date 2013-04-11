#!/usr/bin/env python

# This file is part of PRAW.
#
# PRAW is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PRAW is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PRAW.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable-msg=C0103, C0302, R0903, R0904, W0201

import unittest

from requests.exceptions import Timeout
from six import next as six_next

from helper import BasicHelper, reddit_only
from praw import helpers, Reddit
from praw.objects import Comment, MoreComments, Submission


class BasicTest(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()

    def test_comments_contains_no_noncomment_objects(self):
        comments = self.r.get_submission(url=self.comment_url).comments
        self.assertFalse([item for item in comments if not
                          (isinstance(item, Comment) or
                           isinstance(item, MoreComments))])

    def test_decode_entities(self):
        text = self.r.get_submission(url=self.comment_url).selftext_html
        self.assertTrue(text.startswith('&lt;'))
        self.assertTrue(text.endswith('&gt;'))
        self.r.config.decode_html_entities = True
        text = self.r.get_submission(url=self.comment_url).selftext_html
        self.assertTrue(text.startswith('<'))
        self.assertTrue(text.endswith('>'))

    def test_equality(self):
        subreddit = self.r.get_subreddit(self.sr)
        same_subreddit = self.r.get_subreddit(self.sr)
        submission = six_next(subreddit.get_hot())
        self.assertTrue(subreddit == same_subreddit)
        self.assertFalse(subreddit != same_subreddit)
        self.assertFalse(subreddit == submission)

    def test_get_all_comments(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_all_comments(limit=num))))

    def test_get_all_comments_gilded(self):
        gilded_comments = self.r.get_all_comments(gilded_only=True)
        self.assertTrue(all(comment.gilded > 0 for comment in gilded_comments))

    def test_get_comments(self):
        num = 50
        result = self.r.get_comments(self.sr, limit=num)
        self.assertEqual(num, len(list(result)))

    @reddit_only
    def test_get_controversial(self):
        num = 50
        result = self.r.get_controversial(limit=num, params={'t': 'all'})
        self.assertEqual(num, len(list(result)))

    def test_get_flair_list(self):
        sub = self.r.get_subreddit('python')
        self.assertTrue(six_next(sub.get_flair_list()))

    def test_get_front_page(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_front_page(limit=num))))

    def test_get_new(self):
        num = 50
        result = self.r.get_new(limit=num, params={'sort': 'new'})
        self.assertEqual(num, len(list(result)))

    @reddit_only
    def test_get_popular_reddits(self):
        num = 50
        self.assertEqual(num, len(list(self.r.get_popular_reddits(limit=num))))

    def test_get_random_subreddit(self):
        subs = set()
        for _ in range(3):
            subs.add(self.r.get_subreddit('RANDOM').display_name)
        self.assertTrue(len(subs) > 1)

    def test_get_submissions(self):
        kind = self.r.config.by_object[Submission]

        def fullname(url):
            return '{0}_{1}'.format(kind, url.rsplit('/', 2)[1])
        fullnames = [fullname(self.comment_url), fullname(self.link_url)] * 100
        retreived = [x.fullname for x in self.r.get_submissions(fullnames)]
        self.assertEqual(fullnames, retreived)

    @reddit_only
    def test_get_top(self):
        num = 50
        result = self.r.get_top(limit=num, params={'t': 'all'})
        self.assertEqual(num, len(list(result)))

    def test_info_by_invalid_id(self):
        self.assertEqual(None, self.r.get_info(thing_id='INVALID'))

    def test_info_by_known_url_returns_known_id_link_post(self):
        found_links = self.r.get_info(self.link_url_link)
        tmp = self.r.get_submission(url=self.link_url)
        self.assertTrue(tmp in found_links)

    def test_info_by_url_also_found_by_id(self):
        found_by_url = self.r.get_info(self.link_url_link)[0]
        found_by_id = self.r.get_info(thing_id=found_by_url.fullname)
        self.assertEqual(found_by_id, found_by_url)

    @reddit_only
    def test_info_by_url_maximum_listing(self):
        self.assertEqual(100, len(self.r.get_info('http://www.reddit.com',
                                                  limit=101)))

    def test_is_username_available(self):
        self.assertFalse(self.r.is_username_available(self.un))
        self.assertTrue(self.r.is_username_available(self.invalid_user_name))
        self.assertFalse(self.r.is_username_available(''))

    def test_not_logged_in_when_initialized(self):
        self.assertEqual(self.r.user, None)

    def test_require_user_agent(self):
        self.assertRaises(TypeError, Reddit, user_agent=None)
        self.assertRaises(TypeError, Reddit, user_agent='')
        self.assertRaises(TypeError, Reddit, user_agent=1)

    @reddit_only
    def test_search(self):
        self.assertTrue(len(list(self.r.search('test'))) > 0)

    def test_search_reddit_names(self):
        self.assertTrue(len(self.r.search_reddit_names('reddit')) > 0)

    def test_timeout(self):
        # pylint: disable-msg=W0212
        self.assertRaises(Timeout, helpers._request, self.r,
                          self.r.config['comments'], timeout=0.001)
