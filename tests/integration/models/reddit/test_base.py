
from ... import IntegrationTest


class TestFetch(IntegrationTest):
    def setup(self):
        super(TestFetch, self).setup()
        self.redditor = self.reddit.redditor('spez')
        assert self.redditor.name == 'spez'
        assert not self.redditor.fetched
        assert not self.redditor._fetched
        assert len(self.redditor.a) == 1

    def test_implicit_fetch__accelerator(self):
        assert not self.redditor.fetched
        with self.recorder.use_cassette(
                'TestFetch.test_implicit_fetch__accelerator'):
            assert int(self.redditor.created_utc) == 1118030400
        assert self.redditor.fetched

    def test_implicit_fetch__namespace(self):
        assert not self.redditor.fetched
        with self.recorder.use_cassette(
                'TestFetch.test_implicit_fetch__namespace'):
            assert int(self.redditor.a.created_utc) == 1118030400
        assert self.redditor.fetched

    def test_explicit_fetch(self):
        assert not self.redditor.fetched
        assert 'created_utc' not in self.redditor.a
        assert not self.redditor.fetched
        with self.recorder.use_cassette('TestFetch.test_explicit_fetch'):
            self.redditor.fetch()
        assert self.redditor.fetched
        assert 'created_utc' in self.redditor.a
        assert int(self.redditor.a.created_utc) == 1118030400

    def test_refetch(self):
        with self.recorder.use_cassette('TestFetch.test_refetch'):
            self.redditor.fetch()
        assert self.redditor.fetched
        assert 'link_karma' in self.redditor.a
        assert 'created_utc' in self.redditor.a
        assert int(self.redditor.a.created_utc) == 1118030400
        self.redditor._data['created_utc'] = 1
        assert int(self.redditor.a.created_utc) == 1
        with self.recorder.use_cassette('TestFetch.test_refetch'):
            self.redditor.fetch(True)
        assert self.redditor.fetched
        assert int(self.redditor.a.created_utc) == 1118030400

    def test_return(self):
        with self.recorder.use_cassette('TestFetch.test_return'):
            self.redditor.fetch().fetch(True)
