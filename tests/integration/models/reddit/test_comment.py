from praw.exceptions import ClientException, PRAWException
from praw.models import Comment
from prawcore import BadRequest
import mock
import pytest

from ... import IntegrationTest


class TestComment(IntegrationTest):
    def test_attributes(self):
        with self.recorder.use_cassette('TestComment.test_attributes'):
            comment = Comment(self.reddit, 'cklhv0f')
            assert comment.author == 'bboe'
            assert comment.body.startswith('Yes it does.')
            assert not comment.is_root
            assert comment.permalink(fast=True) == '/comments/2gmzqe//cklhv0f'
            assert comment.submission == '2gmzqe'

    @mock.patch('time.sleep', return_value=None)
    def test_block(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_block'):
            comment = None
            for item in self.reddit.inbox.submission_replies():
                if item.author and item.author != pytest.placeholders.username:
                    comment = item
                    break
            else:
                assert False, 'no comment found'
            comment.block()

    def test_clear_vote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_clear_vote'):
            Comment(self.reddit, 'd1680wu').clear_vote()

    @mock.patch('time.sleep', return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_delete'):
            comment = Comment(self.reddit, 'd1616q2')
            comment.delete()
            assert comment.author is None
            assert comment.body == '[deleted]'

    def test_downvote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_downvote'):
            Comment(self.reddit, 'd1680wu').downvote()

    @mock.patch('time.sleep', return_value=None)
    def test_edit(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestComment.test_edit'):
            comment = Comment(self.reddit, 'd1616q2')
            comment.edit('New text')
            assert comment.body == 'New text'

    def test_gild__no_creddits(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_gild__no_creddits'):
            with pytest.raises(BadRequest) as excinfo:
                Comment(self.reddit, 'd1616q2').gild()
            reason = excinfo.value.response.json()['reason']
            assert 'INSUFFICIENT_CREDDITS' == reason

    def test_invalid(self):
        with self.recorder.use_cassette('TestComment.test_invalid'):
            with pytest.raises(PRAWException) as excinfo:
                Comment(self.reddit, '0').body
            assert ("No 'Comment' data returned for thing t1_0",)\
                == excinfo.value.args

    @mock.patch('time.sleep', return_value=None)
    def test_mark_read(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_mark_read'):
            comment = next(self.reddit.inbox.unread())
            assert isinstance(comment, Comment)
            comment.mark_read()

    @mock.patch('time.sleep', return_value=None)
    def test_mark_unread(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_mark_unread'):
            comment = next(self.reddit.inbox.comment_replies())
            comment.mark_unread()

    def test_permalink(self):
        with self.recorder.use_cassette('TestComment.test_permalink'):
            comment = Comment(self.reddit, 'cklhv0f')
            assert comment.permalink() == ('/r/redditdev/comments/2gmzqe/'
                                           'praw_https_enabled_praw_testing_'
                                           'needed/cklhv0f')

    def test_refresh(self):
        with self.recorder.use_cassette('TestComment.test_refresh'):
            comment = Comment(self.reddit, 'd81vwef').refresh()
        assert len(comment.replies) > 0

    def test_refresh__deleted_comment(self):
        with self.recorder.use_cassette(
                'TestComment.test_refresh__deleted_comment'):
            with pytest.raises(ClientException) as excinfo:
                Comment(self.reddit, 'd7ltvl0').refresh()
        assert ('Comment has been deleted',) == excinfo.value.args

    def test_reply(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_reply'):
            parent_comment = Comment(self.reddit, 'd1616q2')
            comment = parent_comment.reply('Comment reply')
            assert comment.author == self.reddit.config.username
            assert comment.body == 'Comment reply'
            assert not comment.is_root
            assert comment.parent_id == parent_comment.fullname

    def test_report(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_report'):
            Comment(self.reddit, 'd0335z3').report('custom')

    def test_save(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_save'):
            Comment(self.reddit, 'd1680wu').save('foo')

    def test_unsave(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_unsave'):
            Comment(self.reddit, 'd1680wu').unsave()

    def test_upvote(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestComment.test_upvote'):
            Comment(self.reddit, 'd1680wu').upvote()
