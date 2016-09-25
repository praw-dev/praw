"""Test praw.models.subreddit."""
from praw.exceptions import APIException
from praw.models import (Comment, Redditor, Submission, SubredditMessage,
                         WikiPage)
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
                    1410000000, 1420000000,
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


class TestSubredditFlair(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test__iter(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditFlair.test__iter'):
            mapping = list(self.subreddit.flair)
            assert len(mapping) > 0
            assert all(isinstance(x['user'], Redditor) for x in mapping)

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

    def test_ignore_reports(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_ignore_reports'):
            submission = self.reddit.submission('31ybt2')
            self.subreddit.mod.ignore_reports(submission)

    def test_inbox(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditModeration.test_inbox'):
            count = 0
            for item in self.reddit.subreddit('all').mod.inbox():
                assert isinstance(item, SubredditMessage)
                count += 1
            assert count == 100

    def test_remove(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditModeration.test_remove'):
            submission = self.reddit.submission('4b536h')
            self.subreddit.mod.remove(submission, spam=True)

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


class TestSubredditRelationships(IntegrationTest):
    REDDITOR = 'pyapitestuser3'

    @mock.patch('time.sleep', return_value=None)
    def add_remove(self, subreddit, user, relationship, _):
        relationship = getattr(subreddit, relationship)
        relationship.add(user)
        assert user in relationship
        relationship.remove(user)
        assert user not in relationship

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_banned(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditRelationships__banned'):
            self.add_remove(self.subreddit, self.REDDITOR, 'banned')

    def test_contributor(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__contributor'):
            self.add_remove(self.subreddit, self.REDDITOR, 'contributor')

    @mock.patch('time.sleep', return_value=None)
    def test_moderator(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__moderator'):
            # Moderators can only be invited.
            # As of 2016-03-18 there is no API endpoint to get the moderator
            # invite list.
            self.subreddit.moderator.add(self.REDDITOR)
            assert self.REDDITOR not in self.subreddit.moderator

    def test_muted(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette('TestSubredditRelationships__muted'):
            self.add_remove(self.subreddit, self.REDDITOR, 'muted')

    def test_wiki_banned(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__wiki_banned'):
            self.add_remove(self.subreddit.wiki, self.REDDITOR, 'banned')

    def test_wiki_contributors(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
                'TestSubredditRelationships__wiki_contributors'):
            self.add_remove(self.subreddit.wiki, self.REDDITOR, 'contributors')


class TestSubredditStreams(IntegrationTest):
    def test_comments(self):
        with self.recorder.use_cassette('TestSubredditStreams__comments'):
            subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit)
            generator = subreddit.stream.comments()
            for i in range(101):
                assert isinstance(next(generator), Comment)

    def test_submissions(self):
        with self.recorder.use_cassette('TestSubredditStreams__submissions'):
            generator = self.reddit.subreddit('all').stream.submissions()
            for i in range(300):
                assert isinstance(next(generator), Submission)


class TestSubredditWiki(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test__iter(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(
            pytest.placeholders.test_subreddit)
        with self.recorder.use_cassette('TestSubredditWiki__iter'):
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

        with self.recorder.use_cassette('TestSubredditWiki_create'):
            wikipage = subreddit.wiki.create('PRAW New Page',
                                             'This is the new wiki page')
            assert wikipage.name == 'praw_new_page'
            assert wikipage.content_md == 'This is the new wiki page'
