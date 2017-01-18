"""Test praw.models.LiveThread"""
from praw.const import API_PATH
from praw.exceptions import APIException
from praw.models import LiveThread, LiveUpdate, Redditor, RedditorList
import mock
import pytest

from ... import IntegrationTest


class TestLiveThread(IntegrationTest):
    def test_contributor(self):
        thread = LiveThread(self.reddit, 'ukaeu1ik4sw5')
        with self.recorder.use_cassette('TestLiveThread_test_contributor'):
            contributors = thread.contributor()
        assert isinstance(contributors, RedditorList)
        assert len(contributors) > 0

    @mock.patch('time.sleep', return_value=None)
    def test_contributor__with_manage_permission(self, _):
        # see issue #710 for more info
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        url = API_PATH['live_contributors'].format(id=thread.id)
        with self.recorder.use_cassette(
                'TestLiveThread_test_contributor__with_manage_permission'):
            data = thread._reddit.request('GET', url)
            contributors = thread.contributor()
        assert isinstance(data, list)
        assert isinstance(contributors, RedditorList)
        assert len(contributors) > 0

    def test_init(self):
        thread = LiveThread(self.reddit, 'ukaeu1ik4sw5')
        with self.recorder.use_cassette('TestLiveThread_test_init'):
            assert thread.title == 'reddit updates'

    @mock.patch('time.sleep', return_value=None)
    def test_updates(self, _):
        thread = LiveThread(self.reddit, 'ukaeu1ik4sw5')
        with self.recorder.use_cassette('TestLiveThread_test_updates'):
            for update in thread.updates(limit=None):
                assert update.thread == thread
        assert update.body.startswith('Small change:')


class TestLiveContributorRelationship(IntegrationTest):
    def test_accept_invite(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_test_accept_invite'):
            thread.contributor.accept_invite()

    @mock.patch('time.sleep', return_value=None)
    def test_invite__already_invited(self, _):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_'
                'test_invite__already_invited'):
            thread.contributor.invite('nmtake')
            with pytest.raises(APIException) as excinfo:
                thread.contributor.invite('nmtake')
        assert excinfo.value.error_type == 'LIVEUPDATE_ALREADY_CONTRIBUTOR'

    def test_invite__empty_list(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_test_invite__empty_list'):
            thread.contributor.invite('nmtake', [])

    def test_invite__limited(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_test_invite__limited'):
            thread.contributor.invite('nmtake', ['manage', 'edit'])

    def test_invite__none(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_test_invite__none'):
            thread.contributor.invite('nmtake', None)

    def test_invite__redditor(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        redditor = Redditor(self.reddit,
                            _data={'name': 'nmtake', 'id': 'll32z'})
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_test_invite__redditor'):
            thread.contributor.invite(redditor)

    def test_leave(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_test_leave'):
            thread.contributor.leave()

    def test_remove__fullname(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_test_remove__fullname'):
            thread.contributor.remove('t2_ll32z')

    def test_remove__redditor(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        redditor = Redditor(self.reddit,
                            _data={'name': 'nmtake', 'id': 'll32z'})
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_test_remove__redditor'):
            thread.contributor.remove(redditor)

    def test_remove_invite__fullname(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_'
                'test_remove_invite__fullname'):
            thread.contributor.remove_invite('t2_ll32z')

    def test_remove_invite__redditor(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        redditor = Redditor(self.reddit,
                            _data={'name': 'nmtake', 'id': 'll32z'})
        with self.recorder.use_cassette(
                'TestLiveContributorRelationship_'
                'test_remove_invite__redditor'):
            thread.contributor.remove_invite(redditor)


class TestLiveThreadContribution(IntegrationTest):
    def test_add(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'xyu8kmjvfrww')
        with self.recorder.use_cassette(
                'TestLiveThreadContribution_add'):
            thread.contrib.add('* `LiveThreadContribution.add() test`')

    def test_close(self):
        self.reddit.read_only = False
        thread = LiveThread(self.reddit, 'ya2tmqiyb064')
        with self.recorder.use_cassette(
                'TestLiveThreadContribution_close'):
            thread.contrib.close()


class TestLiveUpdateContribution(IntegrationTest):
    @mock.patch('time.sleep', return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        update = LiveUpdate(self.reddit, 'xyu8kmjvfrww',
                            '5d556760-dbee-11e6-9f46-0e78de675452')
        with self.recorder.use_cassette(
                'TestLiveUpdateContribution_remove'):
            update.contrib.remove()
