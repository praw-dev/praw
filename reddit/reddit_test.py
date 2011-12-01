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

import itertools, unittest, util, uuid, warnings
import reddit

USER_AGENT = 'reddit_api test suite'

def setUpModule():
    global r, r_auth, submissions

    print 'Initializing setup'
    r = reddit.Reddit(USER_AGENT)
    r_auth = reddit.Reddit(USER_AGENT)
    r_auth.login('PyAPITestUser2', '1111')

    urls = {}
    urls['self'] = 'http://www.reddit.com/r/programming/comments/bn2wi/'
    urls['link'] = 'http://www.reddit.com/r/UCSantaBarbara/comments/m77nc/'

    submissions = dict((x, r.get_submission(urls[x])) for x in urls)
    print 'Done initializing setup'


class RedditTestCase(unittest.TestCase):
    def test_require_user_agent(self):
        self.assertRaises(reddit.APIException, reddit.Reddit, user_agent=None)

    def test_not_logged_in_when_initialized(self):
        self.assertEqual(r.user, None)

    def test_has_set_user_when_logged_in(self):
        self.assertTrue(isinstance(r_auth.user, reddit.Redditor))

    def test_info_by_known_url_returns_known_id_link_post(self):
        found_links = r.info(submissions['link'].url)
        self.assertTrue(submissions['link'] in found_links)

    def test_info_by_self_url_raises_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            r.info(submissions['self'].url)
            self.assertEqual(len(w), 1)
            self.assertEqual(w[-1].category, reddit.APIWarning)
            self.assertTrue('self' in str(w[-1].message))

    def test_info_by_url_also_found_by_id(self):
        found_links = r.info(submissions['link'].url)
        for link in found_links:
            found_by_id = r.info(id=link.name)

            self.assertTrue(found_by_id)
            self.assertTrue(link in found_by_id)

class RedditorTestCase(unittest.TestCase):
    def setUp(self):
        self.user = r_auth.get_redditor('pyapitestuser3')

    def test_get(self):
        self.assertEqual('6c1xj', self.user.id)

    def test_friend(self):
        self.user.friend()

    def test_unfriend(self):
        self.user.unfriend()


class CommunityTestCase(unittest.TestCase):
    def setUp(self):
        self.community = r_auth.get_subreddit('reddit_api_test')

    def test_subscribe(self):
        self.community.subscribe()

    def test_unsubscribe(self):
        self.community.unsubscribe()


class SubComTestCase(unittest.TestCase):
    global comment, created, saved, voted
    comment = created = saved = voted = False

    def setUp(self):
        self.subreddit = 'reddit_api_test'

    def testTryToSubmitWithoutLoggingIn(self):
        self.assertRaises(reddit.APIException, r.submit,
                          self.subreddit, 'TITLE', text='BODY')

    def testCreateLink(self):
        title = 'Test Link: %s' % uuid.uuid4()
        self.assertTrue(r_auth.submit(self.subreddit, title,
                                      url='http://bryceboe.com'))

    def testA_CreateSelf(self):
        global created
        title = 'Test Self: %s' % uuid.uuid4()
        self.assertTrue(r_auth.submit(self.subreddit, title, text='BODY'))
        for item in r_auth.user.get_submitted():
            if title == item.title:
                created = item
        self.assertFalse(not created)

    def testB_AddComment(self):
        global comment
        if not created:
            return
        text = 'Unique comment: %s' % uuid.uuid4()
        self.assertTrue(created.add_comment(text))
        comment = created.comments[0]
        self.assertEqual(text, comment.body)

    def testC_AddReply(self):
        if not comment:
            return
        self.assertTrue(comment.reply('reply text'))

    def testB_Save(self):
        global saved
        if not created:
            return
        self.assertFalse(created in r_auth.get_saved_links())
        created.save()
        self.assertTrue(created in r_auth.get_saved_links())
        saved = True

    def testC_Unsave(self):
        if not saved:
            return
        self.assertTrue(saved)
        created.unsave()
        self.assertFalse(created in r_auth.get_saved_links())

    def testB_SubUpvoteSet(self):
        global voted
        if not created:
            return
        created.upvote()
        assert(False)
        voted = True

    def testB_SubDownvoteSet(self):
        global voted
        if not created:
            return
        created.downvote()
        assert(False)
        voted = True

    def testC_SubClearVote(self):
        if not voted:
            return
        created.clear_vote()

    def testD_DeleteSubmission(self):
        if not created:
            return
        created.delete()
        self.assertFalse(created in r_auth.user.get_submitted())


class CommentTestCase(unittest.TestCase):
    def setUp(self):
        self.comments = submissions['self'].comments

    def test_comments_contains_no_noncomment_objects(self):
        self.assertFalse([item for item in self.comments if not
                         (isinstance(item, reddit.Comment) or
                          isinstance(item, reddit.MoreComments))])


if __name__ == '__main__':
    setUpModule()
    unittest.main()
