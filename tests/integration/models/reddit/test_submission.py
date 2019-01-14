from praw.models import Comment, Submission
from prawcore import BadRequest
import mock
import pytest

from ... import IntegrationTest


class TestSubmission(IntegrationTest):
    def test_comments(self):
        with self.recorder.use_cassette(
                'TestSubmission.test_comments'):
            submission = Submission(self.reddit, '2gmzqe')
            assert len(submission.comments) == 1
            assert isinstance(submission.comments[0], Comment)
            assert isinstance(submission.comments[0].replies[0], Comment)

    def test_clear_vote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_clear_vote'):
            Submission(self.reddit, '4b536p').clear_vote()

    @mock.patch('time.sleep', return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_delete'):
            submission = Submission(self.reddit, '4b1tfm')
            submission.delete()
            assert submission.author is None
            assert submission.selftext == '[deleted]'

    def test_disable_inbox_replies(self):
        self.reddit.read_only = False
        submission = Submission(self.reddit, '6ckfdz')
        with self.recorder.use_cassette(
                'TestSubmission.test_disable_inbox_replies'):
            submission.disable_inbox_replies()

    def test_downvote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_downvote'):
            Submission(self.reddit, '4b536p').downvote()

    def test_duplicates(self):
        with self.recorder.use_cassette(
                'TestSubmission.test_duplicates'):
            submission = Submission(self.reddit, 'avj2v')
            assert len(list(submission.duplicates())) > 0

    @mock.patch('time.sleep', return_value=None)
    def test_edit(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_edit'):
            submission = Submission(self.reddit, '4b1tfm')
            submission.edit('New text')
            assert submission.selftext == 'New text'

    def test_enable_inbox_replies(self):
        self.reddit.read_only = False
        submission = Submission(self.reddit, '6ckfdz')
        with self.recorder.use_cassette(
                'TestSubmission.test_enable_inbox_replies'):
            submission.enable_inbox_replies()

    def test_gild__no_creddits(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_gild__no_creddits'):
            with pytest.raises(BadRequest) as excinfo:
                Submission(self.reddit, '4b1tfm').gild()
            reason = excinfo.value.response.json()['reason']
            assert 'INSUFFICIENT_CREDDITS' == reason

    def test_gilded(self):
        with self.recorder.use_cassette('TestSubmission.test_gilded'):
            assert 1 == Submission(self.reddit, '2gmzqe').gilded

    def test_hide(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_hide'):
            Submission(self.reddit, '4b1tfm').hide()

    def test_hide_multiple(self):
        self.reddit.read_only = False
        submissions = [Submission(self.reddit, 'fewoh'),
                       Submission(self.reddit, 'c625v')]
        with self.recorder.use_cassette(
                'TestSubmission.test_hide__multiple'):
            Submission(self.reddit, '1eipl7').hide(submissions)

    @mock.patch('time.sleep', return_value=None)
    def test_hide_multiple_in_batches(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_hide__multiple_in_batches'):
            submissions = list(self.reddit.subreddit('popular').hot(limit=100))
            assert len(submissions) == 100
            submissions[0].hide(submissions[1:])

    def test_invalid_attribute(self):
        with self.recorder.use_cassette(
                'TestSubmission.test_invalid_attribute'):
            submission = Submission(self.reddit, '2gmzqe')
            with pytest.raises(AttributeError) as excinfo:
                submission.invalid_attribute
        assert excinfo.value.args[0] == ("'Submission' object has no attribute"
                                         " 'invalid_attribute'")

    def test_reply(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_reply'):
            submission = Submission(self.reddit, '4b1tfm')
            comment = submission.reply('Test reply')
            assert comment.author == self.reddit.config.username
            assert comment.body == 'Test reply'
            assert comment.parent_id == submission.fullname

    def test_report(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_report'):
            Submission(self.reddit, '4b536h').report('praw')

    def test_save(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_save'):
            Submission(self.reddit, '4b536p').save()

    def test_mark_visited(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_mark_visited'):
            Submission(self.reddit, '8s529q').mark_visited()

    def test_unhide(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_unhide'):
            Submission(self.reddit, '4b1tfm').unhide()

    def test_unhide_multiple(self):
        self.reddit.read_only = False
        submissions = [Submission(self.reddit, 'fewoh'),
                       Submission(self.reddit, 'c625v')]
        with self.recorder.use_cassette(
                'TestSubmission.test_unhide__multiple'):
            Submission(self.reddit, '1eipl7').unhide(submissions)

    @mock.patch('time.sleep', return_value=None)
    def test_unhide_multiple_in_batches(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_unhide__multiple_in_batches'):
            submissions = list(self.reddit.subreddit('popular').hot(limit=100))
            assert len(submissions) == 100
            submissions[0].unhide(submissions[1:])

    def test_unsave(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_unsave'):
            Submission(self.reddit, '4b536p').unsave()

    def test_upvote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_upvote'):
            Submission(self.reddit, '4b536p').upvote()

    @mock.patch('time.sleep', return_value=None)
    def test_crosspost(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubmission.test_crosspost'):
            subreddit = pytest.placeholders.test_subreddit
            crosspost_parent = self.reddit.submission(id='6vx01b')

            submission = crosspost_parent.crosspost(subreddit)
            assert submission.author == self.reddit.config.username
            assert submission.title == 'Test Title'
            assert submission.crosspost_parent == 't3_6vx01b'

    @mock.patch('time.sleep', return_value=None)
    def test_crosspost__subreddit_object(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_crosspost__subreddit_object'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            crosspost_parent = self.reddit.submission(id='6vx01b')

            submission = crosspost_parent.crosspost(subreddit)
            assert submission.author == self.reddit.config.username
            assert submission.title == 'Test Title'
            assert submission.crosspost_parent == 't3_6vx01b'

    @mock.patch('time.sleep', return_value=None)
    def test_crosspost__custom_title(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmission.test_crosspost__custom_title'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            crosspost_parent = self.reddit.submission(id='6vx01b')

            submission = crosspost_parent.crosspost(subreddit, 'my title')
            assert submission.author == self.reddit.config.username
            assert submission.title == 'my title'
            assert submission.crosspost_parent == 't3_6vx01b'


class TestSubmissionFlair(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_choices(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubmissionFlair.test_choices'):
            submission = Submission(self.reddit, '4t4t2h')
            expected = [
                {'flair_text': 'SATISFIED',
                 'flair_template_id': '680f43b8-1fec-11e3-80d1-12313b0b80bc',
                 'flair_text_editable': False, 'flair_position': 'left',
                 'flair_css_class': ''},
                {'flair_text': 'STATS',
                 'flair_template_id': '16cabd0a-a68d-11e5-8349-0e8ff96e6679',
                 'flair_text_editable': False, 'flair_position': 'left',
                 'flair_css_class': ''}]
            assert expected == submission.flair.choices()

    @mock.patch('time.sleep', return_value=None)
    def test_select(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubmissionFlair.test_select'):
            submission = Submission(self.reddit, '4t4t2h')
            submission.flair.select('16cabd0a-a68d-11e5-8349-0e8ff96e6679')


class TestSubmissionModeration(IntegrationTest):
    def test_approve(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_approve'):
            self.reddit.submission('4b536h').mod.approve()

    def test_contest_mode(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_contest_mode'):
            submission = Submission(self.reddit, '4s2idz')
            submission.mod.contest_mode()

    def test_contest_mode__disable(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_contest_mode__disable'):
            submission = Submission(self.reddit, '4s2idz')
            submission.mod.contest_mode(state=False)

    @mock.patch('time.sleep', return_value=None)
    def test_flair(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubmissionModeration.test_flair'):
            self.reddit.submission('4b536p').mod.flair('submission flair')

    def test_distinguish(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_distinguish'):
            self.reddit.submission('4b536h').mod.distinguish()

    def test_ignore_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_ignore_reports'):
            self.reddit.submission('31ybt2').mod.ignore_reports()

    def test_nsfw(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_nsfw'):
            Submission(self.reddit, '4s2idz').mod.nsfw()

    def test_lock(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_lock'):
            Submission(self.reddit, '4s2idz').mod.lock()

    def test_remove(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_remove'):
            self.reddit.submission('4b536h').mod.remove(spam=True)

    @mock.patch('time.sleep', return_value=None)
    def test_send_removal_message(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_send_removal_message'):
            submission = self.reddit.submission('aezo6s')
            mod = submission.mod
            mod.remove()
            message = 'message'
            res = [mod.send_removal_message(type, 'title', message)
                   for type in ('public', 'private', 'private_exposed')]
            assert isinstance(res[0], Comment)
            assert res[0].parent_id == 't3_' + submission.id
            assert res[0].stickied
            assert res[0].body == message
            assert res[1] is None
            assert res[2] is None

    def test_sfw(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_sfw'):
            Submission(self.reddit, '4s2idz').mod.sfw()

    def test_spoiler(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_spoiler'):
            Submission(self.reddit, '5ouli3').mod.spoiler()

    def test_sticky(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_sticky'):
            Submission(self.reddit, '4s2idz').mod.sticky()

    def test_sticky__remove(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_sticky__remove'):
            Submission(self.reddit, '4s2idz').mod.sticky(state=False)

    def test_sticky__top(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_sticky__top'):
            Submission(self.reddit, '4s2idz').mod.sticky(bottom=False)

    def test_suggested_sort(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_suggested_sort'):
            Submission(self.reddit, '4s2idz').mod.suggested_sort(sort='random')

    def test_suggested_sort__clear(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_suggested_sort__clear'):
            Submission(self.reddit, '4s2idz').mod.suggested_sort(sort='blank')

    def test_undistinguish(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_undistinguish'):
            self.reddit.submission('4b536h').mod.undistinguish()

    def test_unignore_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_unignore_reports'):
            self.reddit.submission('31ybt2').mod.unignore_reports()

    def test_unlock(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_unlock'):
            Submission(self.reddit, '4s2idz').mod.unlock()

    def test_unspoiler(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubmissionModeration.test_unspoiler'):
            Submission(self.reddit, '5ouli3').mod.unspoiler()
