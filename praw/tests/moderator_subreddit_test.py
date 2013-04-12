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

from helper import configure, OTHER_USER_NAME, R, SR, SUBREDDIT


def setup_function(function):
    configure()


def test_get_mod_log():
    assert list(SUBREDDIT.get_mod_log())


def test_get_mod_log_with_mod_by_name():
    other = R.get_redditor(OTHER_USER_NAME)
    actions = list(SUBREDDIT.get_mod_log(mod=other.name))
    assert actions
    #.assertTrue(all(x.mod_id36 == other.id for x in actions))
    assert all(x.mod.lower() == other.name.lower() for x in actions)


def test_get_mod_log_with_mod_by_redditor_object():
    other = R.get_redditor(OTHER_USER_NAME)
    actions = list(SUBREDDIT.get_mod_log(mod=other))
    assert actions
    #.assertTrue(all(x.mod_id36 == other.id for x in actions))
    assert all(x.mod.lower() == other.name.lower() for x in actions)


def test_get_mod_log_with_action_filter():
    actions = list(SUBREDDIT.get_mod_log(action='removelink'))
    assert actions
    assert all(x.action == 'removelink' for x in actions)


def test_get_mod_queue():
    mod_submissions = list(R.get_subreddit('mod').get_mod_queue())
    assert len(mod_submissions) > 0


def test_get_mod_queue_multi():
    multi = '{0}+{1}'.format(SR, 'reddit_api_test2')
    mod_submissions = list(R.get_subreddit(multi).get_mod_queue())
    assert len(mod_submissions) > 0


def test_get_unmoderated():
    submissions = list(SUBREDDIT.get_unmoderated())
    assert len(submissions) > 0
