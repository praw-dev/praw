"""Test praw.models.subreddit."""
from os.path import abspath, dirname, join
import sys

from praw.exceptions import APIException
from praw.models import (Comment, ModAction, Redditor, Submission, Subreddit,
                         SubredditMessage, Stylesheet, WikiPage)
from prawcore import Forbidden, NotFound
import mock
import pytest

from ... import IntegrationTest


class TestSubreddit(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_create(self, _):
        self.reddit.read_only = False
        new_name = 'PRAW_rrldkyrfln'
        with self.recorder.use_cassette('TestSubreddit.test_create'):
            subreddit = self.reddit.subreddit.create(name=new_name,
                                                     title='Sub',
                                                     link_type='any',
                                                     subreddit_type='public',
                                                     wikimode='disabled')
            assert subreddit.display_name == new_name
            assert subreddit.submission_type == 'any'

    def test_create__exists(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubreddit.test_create__exists'):
            with pytest.raises(APIException) as excinfo:
                self.reddit.subreddit.create('redditdev', title='redditdev',
                                             link_type='any',
                                             subreddit_type='public',
                                             wikimode='disabled')
            assert excinfo.value.error_type == 'SUBREDDIT_EXISTS'

    def test_create__invalid_parameter(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubreddit.test_create__invalid_parameter'):
            with pytest.raises(APIException) as excinfo:
                # Supplying invalid setting for link_type
                self.reddit.subreddit.create(name='PRAW_iavynavffv',
                                             title='sub', link_type='abcd',
                                             subreddit_type='public',
                                             wikimode='disabled')
            assert excinfo.value.error_type == 'INVALID_OPTION'

    def test_create__missing_parameter(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubreddit.test_create__missing_parameter'):
            with pytest.raises(APIException) as excinfo:
                # Not supplying required field title.
                self.reddit.subreddit.create(name='PRAW_iavynavffv',
                                             title=None, link_type='any',
                                             subreddit_type='public',
                                             wikimode='disabled')
            assert excinfo.value.error_type == 'NO_TEXT'

    @mock.patch('time.sleep', return_value=None)
    def test_message(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubreddit.test_message'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            subreddit.message('Test from PRAW', message='Test content')

    def test_random(self):
        with self.recorder.use_cassette('TestSubreddit.test_random'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            submissions = [subreddit.random(), subreddit.random(),
                           subreddit.random(), subreddit.random()]
            assert len(submissions) == len(set(submissions))

    def test_sticky(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubreddit.test_sticky'):
            submission = subreddit.sticky()
            assert isinstance(submission, Submission)

    def test_sticky__not_set(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubreddit.test_sticky__not_set'):
            with pytest.raises(NotFound):
                subreddit.sticky(2)

    def test_search(self):
        with self.recorder.use_cassette('TestSubreddit.test_search'):
            subreddit = self.reddit.subreddit('all')
            for item in subreddit.search('praw oauth search', limit=None):
                assert isinstance(item, Submission)

    @mock.patch('time.sleep', return_value=None)
    @mock.patch('time.time', return_value=1474803456.4)
    def test_submissions__with_default_arguments(self, _, __):
        with self.recorder.use_cassette(
                'TestSubreddit.test_submissions__with_default_arguments'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            count = 0
            for submission in subreddit.submissions():
                count += 1
        assert count > 1000

    @mock.patch('time.sleep', return_value=None)
    def test_submissions__with_provided_arguments(self, _):
        with self.recorder.use_cassette(
                'TestSubreddit.test_submissions__with_provided_arguments'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            count = 0
            for submission in subreddit.submissions(
                    1410000000.1, 1420000000.9,
                    "(not author:'{}')".format(self.reddit.config.username)):
                count += 1
                assert submission.author != self.reddit.config.username
        assert count > 0

    @mock.patch('time.sleep', return_value=None)
    def test_submit__selftext(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubreddit.test_submit__selftext'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            submission = subreddit.submit('Test Title', selftext='Test text.')
            assert submission.author == self.reddit.config.username
            assert submission.selftext == 'Test text.'
            assert submission.title == 'Test Title'

    @mock.patch('time.sleep', return_value=None)
    def test_submit__url(self, _):
        url = 'https://praw.readthedocs.org/en/stable/'
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubreddit.test_submit__url'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            submission = subreddit.submit('Test Title', url=url)
            assert submission.author == self.reddit.config.username
            assert submission.url == url
            assert submission.title == 'Test Title'

    def test_subscribe(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubreddit.test_subscribe'):
            subreddit.subscribe()

    def test_subscribe__multiple(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette(
                'TestSubreddit.test_subscribe__multiple'):
            subreddit.subscribe(['redditdev', self.reddit.subreddit('iama')])

    def test_traffic(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubreddit.test_traffic'):
            traffic = subreddit.traffic()
            assert isinstance(traffic, dict)

    def test_traffic__not_public(self):
        subreddit = self.reddit.subreddit('announcements')
        with self.recorder.use_cassette(
                'TestSubreddit.test_traffic__not_public'):
            with pytest.raises(NotFound):
                subreddit.traffic()

    def test_unsubscribe(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubreddit.test_unsubscribe'):
            subreddit.unsubscribe()

    def test_unsubscribe__multiple(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette(
                'TestSubreddit.test_unsubscribe__multiple'):
            subreddit.unsubscribe(['redditdev', self.reddit.subreddit('iama')])


class TestSubredditFilters(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test__iter__all(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFilters.test__iter__all'):
            filters = list(self.reddit.subreddit('all').filters)
        assert len(filters) > 0
        assert all(isinstance(x, Subreddit) for x in filters)

    @mock.patch('time.sleep', return_value=None)
    def test__iter__mod(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFilters.test__iter__mod'):
            filters = list(self.reddit.subreddit('mod').filters)
        assert len(filters) > 0
        assert all(isinstance(x, Subreddit) for x in filters)

    @mock.patch('time.sleep', return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFilters.test_add'):
            self.reddit.subreddit('all').filters.add('redditdev')

    @mock.patch('time.sleep', return_value=None)
    def test_add__non_special(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFilters.test_add__non_special'):
            with pytest.raises(NotFound):
                self.reddit.subreddit('redditdev').filters.add('redditdev')

    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFilters.test_remove'):
            self.reddit.subreddit('mod').filters.remove('redditdev')

    @mock.patch('time.sleep', return_value=None)
    def test_remove__non_special(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFilters.test_remove__non_special'):
            with pytest.raises(NotFound):
                self.reddit.subreddit('redditdev').filters.remove('redditdev')


class TestSubredditFlair(IntegrationTest):
    REDDITOR = pytest.placeholders.username

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test__call(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFlair.test__call'):
            mapping = self.subreddit.flair()
            assert len(list(mapping)) > 0

    def test__call__user_filter(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test__call_user_filter'):
            mapping = self.subreddit.flair(redditor=self.REDDITOR)
            assert len(list(mapping)) == 1

    def test__iter(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFlair.test__iter'):
            mapping = list(self.subreddit.flair)
            assert len(mapping) > 0
            assert all(isinstance(x['user'], Redditor) for x in mapping)

    def test_configure(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_configure'):
            self.subreddit.flair.configure(position=None, self_assign=True,
                                           link_position=None,
                                           link_self_assign=True)

    def test_configure__defaults(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_configure__defaults'):
            self.subreddit.flair.configure()

    def test_delete(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFlair.test_delete'):
            self.subreddit.flair.delete(self.reddit.config.username)

    @mock.patch('time.sleep', return_value=None)
    def test_delete_all(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFlair.test_delete_all'):
            response = self.subreddit.flair.delete_all()
            assert len(response) > 100
            assert all('removed' in x['status'] for x in response)

    def test_set__redditor(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_set__redditor'):
            redditor = self.subreddit._reddit.redditor(
                self.reddit.config.username)
            self.subreddit.flair.set(redditor, 'redditor flair')

    def test_set__redditor_string(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_set__redditor_string'):
            self.subreddit.flair.set(self.reddit.config.username, 'new flair',
                                     'some class')

    def test_set__submission(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_set__submission'):
            submission = self.subreddit._reddit.submission('4b536p')
            self.subreddit.flair.set(submission, 'submission flair')

    def test_set__submission__by_thing(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_set__submission__by_thing'):
            submission = self.subreddit._reddit.submission('4b536p')
            self.subreddit.flair.set(thing=submission, text='submission flair')

    def test_update(self):
        self.reddit.read_only = False
        redditor = self.subreddit._reddit.redditor(self.reddit.config.username)
        flair_list = [redditor, 'spez', {'user': 'bsimpson'},
                      {'user': 'spladug', 'flair_text': '',
                       'flair_css_class': ''}]
        with self.recorder.use_cassette('TestSubredditFlair.test_update'):
            response = self.subreddit.flair.update(flair_list,
                                                   css_class='default')
        assert all(x['ok'] for x in response)
        assert not any(x['errors'] for x in response)
        assert not any(x['warnings'] for x in response)
        assert len([x for x in response if 'added' in x['status']]) == 3
        assert len([x for x in response if 'removed' in x['status']]) == 1
        for i, name in enumerate([str(redditor), 'spez', 'bsimpson',
                                  'spladug']):
            assert name in response[i]['status']

    def test_update__comma_in_text(self):
        self.reddit.read_only = False
        flair_list = [{'user': 'bsimpson'},
                      {'user': 'spladug', 'flair_text': 'a,b'}]
        with self.recorder.use_cassette(
                'TestSubredditFlair.test_update__comma_in_text'):
            response = self.subreddit.flair.update(flair_list,
                                                   css_class='default')
        assert all(x['ok'] for x in response)


class TestSubredditFlairTemplates(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test__iter(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlairTemplates.test__iter'):
            templates = list(self.subreddit.flair.templates)
        assert len(templates) > 100

    @mock.patch('time.sleep', return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlairTemplates.test_add'):
            for i in range(101):
                self.subreddit.flair.templates.add('PRAW{}'.format(i))

    def test_clear(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlairTemplates.test_clear'):
            self.subreddit.flair.templates.clear()

    @mock.patch('time.sleep', return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlairTemplates.test_delete'):
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.delete(
                template['flair_template_id'])

    @mock.patch('time.sleep', return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditFlairTemplates.test_update'):
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.update(
                template['flair_template_id'], 'PRAW updated')


class TestSubredditListings(IntegrationTest):
    def test_comments(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_comments'):
            subreddit = self.reddit.subreddit('askreddit')
            comments = list(subreddit.comments())
        assert len(comments) == 100

    def test_comments_gilded(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_comments_gilded'):
            subreddit = self.reddit.subreddit('askreddit')
            comments = list(subreddit.comments.gilded())
        assert len(comments) == 100

    def test_controversial(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_controversial'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.controversial())
        assert len(submissions) == 100

    def test_gilded(self):
        with self.recorder.use_cassette('TestSubredditListings.test_gilded'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.gilded())
        assert len(submissions) >= 50

    def test_hot(self):
        with self.recorder.use_cassette('TestSubredditListings.test_hot'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.hot())
        assert len(submissions) == 100

    def test_new(self):
        with self.recorder.use_cassette('TestSubredditListings.test_new'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.new())
        assert len(submissions) == 100

    def test_random_rising(self):
        with self.recorder.use_cassette(
                'TestSubredditListings.test_random_rising'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.random_rising())
        assert len(submissions) == 100

    def test_rising(self):
        with self.recorder.use_cassette('TestSubredditListings.test_rising'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.rising())
        assert len(submissions) == 100

    def test_top(self):
        with self.recorder.use_cassette('TestSubredditListings.test_top'):
            subreddit = self.reddit.subreddit('askreddit')
            submissions = list(subreddit.top())
        assert len(submissions) == 100


class TestSubredditModeration(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_accept_invite__no_invite(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_accept_invite__no_invite'):
            with pytest.raises(APIException) as excinfo:
                self.subreddit.mod.accept_invite()
            assert excinfo.value.error_type == 'NO_INVITE_FOUND'

    def test_approve(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_approve'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.approve(submission)

    def test_distinguish(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_distinguish'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.distinguish(submission)

    @mock.patch('time.sleep', return_value=None)
    def test_distinguish__sticky(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_distinguish__sticky'):
            comment = Comment(self.reddit, 'dba9bzn')
            self.subreddit.mod.distinguish(comment, sticky=True)

    def test_edited(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditModeration.test_edited'):
            count = 0
            for item in self.subreddit.mod.edited():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count == 100

    def test_edited__only_comments(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_edited__only_comments'):
            count = 0
            for item in self.subreddit.mod.edited(only='comments'):
                assert isinstance(item, Comment)
                count += 1
            assert count == 100

    def test_edited__only_submissions(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_edited__only_submissions'):
            count = 0
            for item in self.subreddit.mod.edited(only='submissions'):
                assert isinstance(item, Submission)
                count += 1
            assert count > 0

    def test_ignore_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_ignore_reports'):
            submission = self.reddit.submission('31ybt2')
            self.subreddit.mod.ignore_reports(submission)

    def test_inbox(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditModeration.test_inbox'):
            count = 0
            for item in self.reddit.subreddit('all').mod.inbox():
                assert isinstance(item, SubredditMessage)
                count += 1
            assert count == 100

    def test_log(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditModeration.test_log'):
            count = 0
            for item in self.reddit.subreddit('mod').mod.log():
                assert isinstance(item, ModAction)
                count += 1
            assert count == 100

    def test_log__filters(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_log__filters'):
            count = 0
            for item in self.reddit.subreddit('mod').mod.log(
                    action='invitemoderator',
                    mod=self.reddit.redditor('bboe_dev')):
                assert isinstance(item, ModAction)
                assert item.action == 'invitemoderator'
                assert isinstance(item.mod, Redditor)
                assert item.mod == 'bboe_dev'
                count += 1
            assert count > 0

    def test_modqueue(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_modqueue'):
            count = 0
            for item in self.subreddit.mod.modqueue():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count > 0

    def test_modqueue__only_comments(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_modqueue__only_comments'):
            count = 0
            for item in self.subreddit.mod.modqueue(only='comments'):
                assert isinstance(item, Comment)
                count += 1
            assert count > 0

    def test_modqueue__only_submissions(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_modqueue__only_submissions'):
            count = 0
            for item in self.subreddit.mod.modqueue(only='submissions'):
                assert isinstance(item, Submission)
                count += 1
            assert count > 0

    def test_remove(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditModeration.test_remove'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.remove(submission, spam=True)

    def test_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_reports'):
            count = 0
            for item in self.subreddit.mod.reports():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count == 100

    def test_reports__only_comments(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_reports__only_comments'):
            count = 0
            for item in self.subreddit.mod.reports(only='comments'):
                assert isinstance(item, Comment)
                count += 1
            assert count > 0

    def test_reports__only_submissions(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_reports__only_submissions'):
            count = 0
            for item in self.subreddit.mod.reports(only='submissions'):
                assert isinstance(item, Submission)
                count += 1
            assert count == 100

    def test_spam(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditModeration.test_spam'):
            count = 0
            for item in self.subreddit.mod.spam():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count > 0

    def test_spam__only_comments(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_spam__only_comments'):
            count = 0
            for item in self.subreddit.mod.spam(only='comments'):
                assert isinstance(item, Comment)
                count += 1
            assert count > 0

    def test_spam__only_submissions(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_spam__only_submissions'):
            count = 0
            for item in self.subreddit.mod.spam(only='submissions'):
                assert isinstance(item, Submission)
                count += 1
            assert count > 0

    def test_undistinguish(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_undistinguish'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.undistinguish(submission)

    def test_unignore_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_unignore_reports'):
            submission = self.reddit.submission('31ybt2')
            self.subreddit.mod.unignore_reports(submission)

    def test_unmoderated(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_unmoderated'):
            count = 0
            for item in self.subreddit.mod.unmoderated():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count > 0

    def test_unread(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditModeration.test_unread'):
            count = 0
            for item in self.reddit.subreddit('all').mod.unread():
                assert isinstance(item, SubredditMessage)
                count += 1
            assert count > 0

    @mock.patch('time.sleep', return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditModeration.test_update'):
            before_settings = self.subreddit.mod.settings()
            new_title = before_settings['title'] + 'x'
            if len(new_title) == 20:
                new_title = 'x'
            self.subreddit.mod.update(title=new_title)
            assert self.subreddit.title == new_title
            after_settings = self.subreddit.mod.settings()

            # Ensure that nothing has changed besides what was specified.
            before_settings['title'] = new_title
            assert before_settings == after_settings


class TestSubredditQuarantine(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_opt_in(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit('ferguson')
        with self.recorder.use_cassette('TestSubredditQuarantine.opt_in'):
            with pytest.raises(Forbidden):
                next(subreddit.hot())
            subreddit.quaran.opt_in()
            assert isinstance(next(subreddit.hot()), Submission)

    @mock.patch('time.sleep', return_value=None)
    def test_opt_out(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit('ferguson')
        with self.recorder.use_cassette('TestSubredditQuarantine.opt_out'):
            subreddit.quaran.opt_out()
            with pytest.raises(Forbidden):
                next(subreddit.hot())


class TestSubredditRelationships(IntegrationTest):
    REDDITOR = 'pyapitestuser3'

    @mock.patch('time.sleep', return_value=None)
    def add_remove(self, base, user, relationship, _):
        relationship = getattr(base, relationship)
        relationship.add(user)
        relationships = list(relationship)
        assert user in relationships
        redditor = relationships[relationships.index(user)]
        assert isinstance(redditor, Redditor)
        assert hasattr(redditor, 'date')
        relationship.remove(user)
        assert user not in relationship

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_banned(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditRelationships.banned'):
            self.add_remove(self.subreddit, self.REDDITOR, 'banned')

    def test_banned__callable(self):
        self.reddit.read_only = False
        banned = self.subreddit.banned()
        with self.recorder.use_cassette(
                'TestSubredditRelationships.banned__callable'):
            assert len(list(banned)) > 0

    def test_banned__callable__user_filter(self):
        self.reddit.read_only = False
        banned = self.subreddit.banned(redditor='pyapitestuser3')
        with self.recorder.use_cassette(
                'TestSubredditRelationships.banned__callable_user_filter'):
            assert len(list(banned)) == 1

    def test_contributor(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.contributor'):
            self.add_remove(self.subreddit, self.REDDITOR, 'contributor')

    @mock.patch('time.sleep', return_value=None)
    def test_contributor_leave(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_contributor_leave'):
            self.subreddit.contributor.leave()

    @mock.patch('time.sleep', return_value=None)
    def test_moderator(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.moderator'):
            # Moderators can only be invited.
            # As of 2016-03-18 there is no API endpoint to get the moderator
            # invite list.
            self.subreddit.moderator.add(self.REDDITOR)
            assert self.REDDITOR not in self.subreddit.moderator

    @mock.patch('time.sleep', return_value=None)
    def test_moderator__limited_permissions(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.moderator__limited_permissions'):
            # Moderators can only be invited.
            # As of 2016-03-18 there is no API endpoint to get the moderator
            # invite list.
            self.subreddit.moderator.add(self.REDDITOR,
                                         permissions=['access', 'wiki'])
            assert self.REDDITOR not in self.subreddit.moderator

    def test_moderator_invite__invalid_perm(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.moderator_invite__invalid_perm'):
            with pytest.raises(APIException) as excinfo:
                self.subreddit.moderator.invite(
                    self.REDDITOR, permissions=['a'])
            assert excinfo.value.error_type == 'INVALID_PERMISSIONS'

    @mock.patch('time.sleep', return_value=None)
    def test_moderator_invite__no_perms(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.moderator_invite__no_perms'):
            # Moderators can only be invited.
            # As of 2016-03-18 there is no API endpoint to get the moderator
            # invite list.
            self.subreddit.moderator.invite(self.REDDITOR, permissions=[])
            assert self.REDDITOR not in self.subreddit.moderator

    @mock.patch('time.sleep', return_value=None)
    def test_modeator_leave(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.moderator_leave'):
            self.subreddit.moderator.leave()

    def test_moderator_update(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.moderator_update'):
            self.subreddit.moderator.update(
                self.REDDITOR, permissions=['config'])

    def test_moderator_update_invite(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.moderator_update_invite'):
            self.subreddit.moderator.update_invite(
                self.REDDITOR, permissions=['mail'])

    def test_muted(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditRelationships.muted'):
            self.add_remove(self.subreddit, self.REDDITOR, 'muted')

    def test_wiki_banned(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.wiki_banned'):
            self.add_remove(self.subreddit.wiki, self.REDDITOR, 'banned')

    def test_wiki_contributors(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships.wiki_contributors'):
            self.add_remove(self.subreddit.wiki, self.REDDITOR, 'contributors')


class TestSubredditStreams(IntegrationTest):
    def test_comments(self):
        with self.recorder.use_cassette('TestSubredditStreams.comments'):
            generator = self.reddit.subreddit('all').stream.comments()
            for i in range(400):
                assert isinstance(next(generator), Comment)

    def test_submissions(self):
        with self.recorder.use_cassette('TestSubredditStreams.submissions'):
            generator = self.reddit.subreddit('all').stream.submissions()
            for i in range(101):
                assert isinstance(next(generator), Submission)


class TestSubredditStylesheet(IntegrationTest):
    @staticmethod
    def image_path(name):
        test_dir = abspath(dirname(sys.modules[__name__].__file__))
        return join(test_dir, '..', '..', 'files', name)

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_call(self):
        with self.recorder.use_cassette('TestSubredditStylesheet.test_call'):
            stylesheet = self.subreddit.stylesheet()
        assert isinstance(stylesheet, Stylesheet)
        assert len(stylesheet.images) > 0
        assert stylesheet.stylesheet != ''

    def test_delete_header(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditStylesheet.test_delete_header'):
            self.subreddit.stylesheet.delete_header()

    def test_delete_image(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditStylesheet.test_delete_image'):
            self.subreddit.stylesheet.delete_image('praw')

    def test_update(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditStylesheet.test_update'):
            self.subreddit.stylesheet.update('p { color: red; }')

    def test_update__with_reason(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditStylesheet.test_update__with_reason'):
            self.subreddit.stylesheet.update(
                'div { color: red; }', reason='use div')

    def test_upload(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditStylesheet.test_upload'):
            response = self.subreddit.stylesheet.upload(
                'praw', self.image_path('white-square.png'))
        assert response['img_src'].endswith('.png')

    def test_upload_header__jpg(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditStylesheet.test_upload_header__jpg'):
            response = self.subreddit.stylesheet.upload_header(
                self.image_path('white-square.jpg'))
        assert response['img_src'].endswith('.jpg')

    def test_upload_header__png(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditStylesheet.test_upload_header__png'):
            response = self.subreddit.stylesheet.upload_header(
                self.image_path('white-square.png'))
        assert response['img_src'].endswith('.png')


class TestSubredditWiki(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test__iter(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditWiki.iter'):
            count = 0
            for wikipage in subreddit.wiki:
                assert isinstance(wikipage, WikiPage)
                count += 1
            assert count > 0

    @mock.patch('time.sleep', return_value=None)
    def test_create(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)

        with self.recorder.use_cassette('TestSubredditWiki.create'):
            wikipage = subreddit.wiki.create('PRAW New Page',
                                             'This is the new wiki page')
            assert wikipage.name == 'praw_new_page'
            assert wikipage.content_md == 'This is the new wiki page'

    @mock.patch('time.sleep', return_value=None)
    def test_revisions(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)

        with self.recorder.use_cassette('TestSubredditWiki.revisions'):
            count = 0
            for revision in subreddit.wiki.revisions(limit=4):
                count += 1
                assert isinstance(revision['author'], Redditor)
                assert isinstance(revision['page'], WikiPage)
            assert count == 4
