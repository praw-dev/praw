"""Tests for UnauthenticatedReddit class."""
text_type = betamax = PRAWTest = None


class UnauthenticatedRedditTest(PRAWTest):
    @betamax()
    def test_get_random_submission(self):
        submissions = set()
        for _ in range(3):
            submissions.add(text_type(self.r.get_random_submission()))
        self.assertTrue(len(submissions) > 1)

        submissions = set()
        for _ in range(3):
            item = self.r.get_random_submission('redditdev')
            self.assertEqual(item.subreddit.display_name, 'redditdev')
            submissions.add(text_type(item))
        self.assertTrue(len(submissions) > 1)

    @betamax()
    def test_info_by_id(self):
        self.assertEqual(self.link_id,
                         self.r.get_info(thing_id=self.link_id).fullname)

    @betamax()
    def test_info_by_invalid_id(self):
        self.assertEqual(None, self.r.get_info(thing_id='INVALID'))

    @betamax()
    def test_info_by_known_url_returns_known_id_link_post(self):
        found_links = self.r.get_info(self.link_url_link)
        tmp = self.r.get_submission(url=self.link_url)
        self.assertTrue(tmp in found_links)

    @betamax()
    def test_info_by_url_also_found_by_id(self):
        found_by_url = self.r.get_info(self.link_url_link)[0]
        found_by_id = self.r.get_info(thing_id=found_by_url.fullname)
        self.assertEqual(found_by_id, found_by_url)

    @betamax()
    def test_info_by_url_maximum_listing(self):
        self.assertEqual(100, len(self.r.get_info('http://www.reddit.com',
                                                  limit=101)))

    @betamax()
    def test_search(self):
        self.assertTrue(len(list(self.r.search('test'))) > 2)

    @betamax()
    def test_search_multiply_submitted_url(self):
        self.assertTrue(
            len(list(self.r.search('http://www.livememe.com/'))) > 2)

    @betamax()
    def test_search_single_submitted_url(self):
        self.assertEqual(
            1, len(list(self.r.search('http://www.livememe.com/vg972qp'))))

    @betamax()
    def test_search_with_syntax(self):
        no_syntax = self.r.search('timestamp:1354348800..1354671600',
                                  subreddit=self.sr)
        self.assertFalse(list(no_syntax))
        with_syntax = self.r.search('timestamp:1354348800..1354671600',
                                    subreddit=self.sr, syntax='cloudsearch')
        self.assertTrue(list(with_syntax))

    @betamax()
    def test_search_with_time_window(self):
        num = 50
        submissions = len(list(self.r.search('test', subreddit=self.sr,
                                             period='all', limit=num)))
        self.assertTrue(submissions == num)
