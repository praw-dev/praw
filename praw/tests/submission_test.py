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

import pytest
from six import next as six_next

from helper import configure, disable_cache, first, R, SR, USER_AGENT
from praw import errors, Reddit


def setup_function(function):
    configure()


def test_clear_vote():
    submission = first(R.user.get_submitted(),
                       lambda submission: submission.likes is False)
    assert submission is not None
    submission.clear_vote()
    # reload the submission
    submission = R.get_submission(submission_id=submission.id)
    assert submission.likes is None


def test_delete():
    submission = list(R.user.get_submitted())[-1]
    submission.delete()
    # reload the submission
    submission = R.get_submission(submission_id=submission.id)
    assert None == submission.author


def test_downvote():
    submission = first(R.user.get_submitted(),
                       lambda submission: submission.likes is True)
    assert submission is not None
    submission.downvote()
    # reload the submission
    submission = R.get_submission(submission_id=submission.id)
    assert not submission.likes


def test_hide():
    disable_cache()
    found = first(R.user.get_submitted(), lambda item: not item.hidden)
    assert found is not None
    found.hide()
    found.refresh()
    assert found.hidden


def test_report():
    # login as new user to report submission
    oth = Reddit(USER_AGENT, disable_update_check=True)
    oth.login('PyAPITestUser3', '1111')
    subreddit = oth.get_subreddit(SR)
    submission = first(subreddit.get_new(),
                       lambda submission: not submission.hidden)
    assert submission is not None
    submission.report()
    # check if submission was reported
    found_report = first(R.get_subreddit(SR).get_reports(),
                         lambda report: report.id == submission.id)
    assert found_report is not None


def test_save():
    submission = first(R.user.get_submitted(),
                       lambda submission: not submission.saved)
    assert submission is not None
    submission.save()
    # reload the submission
    submission = R.get_submission(submission_id=submission.id)
    assert submission.saved
    # verify in saved_links
    saved = first(R.user.get_saved(), lambda item: item == submission)
    assert saved is not None


def test_short_link():
    submission = six_next(R.get_new())
    if R.config.is_reddit:
        assert submission.id in submission.short_link
    else:
        with pytest.raises(errors.ClientException):
            getattr(submission, 'short_link')


def test_unhide():
    disable_cache()
    found = first(R.user.get_submitted(), lambda item: item.hidden)
    assert found is not None
    found.unhide()
    found.refresh()
    assert not found.hidden


def test_unsave():
    submission = first(R.user.get_submitted(),
                       lambda submission: submission.saved)
    assert submission is not None
    submission.unsave()
    # reload the submission
    submission = R.get_submission(submission_id=submission.id)
    assert not submission.saved


def test_upvote():
    submission = first(R.user.get_submitted(),
                       lambda submission: submission.likes is None)
    assert submission is not None
    submission.upvote()
    # reload the submission
    submission = R.get_submission(submission_id=submission.id)
    assert submission.likes
