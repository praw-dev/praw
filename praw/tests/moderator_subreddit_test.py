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

from helper import AuthenticatedHelper


class ModeratorSubredditTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_get_mod_log(self):
        self.assertTrue(list(self.subreddit.get_mod_log()))

    def test_get_mod_log_with_mod_by_name(self):
        other = self.r.get_redditor(self.other_user_name)
        actions = list(self.subreddit.get_mod_log(mod=other.name))
        self.assertTrue(actions)
        #self.assertTrue(all(x.mod_id36 == other.id for x in actions))
        self.assertTrue(all(x.mod.lower() == other.name.lower()
                            for x in actions))

    def test_get_mod_log_with_mod_by_redditor_object(self):
        other = self.r.get_redditor(self.other_user_name)
        actions = list(self.subreddit.get_mod_log(mod=other))
        self.assertTrue(actions)
        #self.assertTrue(all(x.mod_id36 == other.id for x in actions))
        self.assertTrue(all(x.mod.lower() == other.name.lower()
                            for x in actions))

    def test_get_mod_log_with_action_filter(self):
        actions = list(self.subreddit.get_mod_log(action='removelink'))
        self.assertTrue(actions)
        self.assertTrue(all(x.action == 'removelink' for x in actions))

    def test_get_mod_queue(self):
        mod_submissions = list(self.r.get_subreddit('mod').get_mod_queue())
        self.assertTrue(len(mod_submissions) > 0)

    def test_get_mod_queue_multi(self):
        multi = '{0}+{1}'.format(self.sr, 'reddit_api_test2')
        mod_submissions = list(self.r.get_subreddit(multi).get_mod_queue())
        self.assertTrue(len(mod_submissions) > 0)

    def test_get_unmoderated(self):
        submissions = list(self.subreddit.get_unmoderated())
        self.assertTrue(len(submissions) > 0)
