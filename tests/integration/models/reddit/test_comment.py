from praw.models import Comment
import mock
import pytest

from ... import IntegrationTest


class TestComment(IntegrationTest):
    def test_attributes(self):
        with self.recorder.use_cassette(
                'TestComment.test_attributes'):
            comment = Comment(self.reddit, 'cklhv0f')
            assert comment.author == 'bboe'
            assert comment.body.startswith('Yes it does.')
            assert not comment.is_root
            assert comment.permalink(fast=True) == '/comments/2gmzqe//cklhv0f'
            assert comment.submission == '2gmzqe'

    @mock.patch('time.sleep', return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestComment.test_delete'):
            comment = Comment(self.reddit, 'd1616q2')
            comment.delete()
            assert comment.author is None
            assert comment.body == '[deleted]'

    @mock.patch('time.sleep', return_value=None)
    def test_edit(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestComment.test_edit'):
            comment = Comment(self.reddit, 'd1616q2')
            comment.edit('New text')
            assert comment.body == 'New text'

    def test_permalink(self):
        with self.recorder.use_cassette(
                'TestComment.test_permalink'):
            comment = Comment(self.reddit, 'cklhv0f')
            assert comment.permalink() == ('/r/redditdev/comments/2gmzqe/'
                                           'praw_https_enabled_praw_testing_'
                                           'needed/cklhv0f')

    def test_reply(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestComment.test_reply'):
            parent_comment = Comment(self.reddit, 'd1616q2')
            comment = parent_comment.reply('Comment reply')
            assert comment.author == pytest.placeholders.username
            assert comment.body == 'Comment reply'
            assert not comment.is_root
            assert comment.parent_id == parent_comment.fullname
