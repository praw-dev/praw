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

from praw.tests.helper import configure, first, SUBREDDIT


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def test_approve():
    submission = next(SUBREDDIT.get_spam())
    assert submission
    submission.approve()
    found = first(SUBREDDIT.get_new(),
                  lambda approved: approved.id == submission.id)
    assert found is not None


def test_remove():
    submission = next(SUBREDDIT.get_new())
    assert submission
    submission.remove()
    found = first(SUBREDDIT.get_spam(),
                  lambda removed: removed.id == submission.id)
    assert found is not None
