"""Tests for UnauthenticatedReddit class."""

from __future__ import print_function, unicode_literals

import os
import time
from six.moves.urllib.parse import urlparse

from praw.helpers import submissions_between
from praw.errors import PRAWException
from .helper import PRAWTest, betamax, teardown_on_keyboard_interrupt


def mock_time():
    return 1448923624.0

real_time = time.time


class TestHelperSubmissionsBetween(PRAWTest):
    def setUp(self):
        PRAWTest.setUp(self)
        time.time = mock_time
        self.verbosity = 3
        if os.getenv('TRAVIS'):
            self.verbosity = 0

    def tearDown(self):
        PRAWTest.tearDown(self)
        # make sure nose reports correct running time
        time.time = real_time

    @betamax()
    @teardown_on_keyboard_interrupt
    def test_submissions_between_raises_correctly(self):
        with self.assertRaises(PRAWException):
            list(submissions_between(self.r,
                                     self.sr,
                                     extra_cloudsearch_fields={'self': 'yes'},
                                     verbosity=self.verbosity))

    @betamax()
    @teardown_on_keyboard_interrupt
    def test_submissions_between_order(self):
        all_subs = list(submissions_between(self.r,
                                            self.sr,
                                            highest_timestamp=time.time(),
                                            verbosity=self.verbosity))

        for i in range(len(all_subs) - 1):
            self.assertGreaterEqual(all_subs[i].created_utc,
                                    all_subs[i + 1].created_utc)

        sr_obj = self.r.get_subreddit(self.sr)
        all_subs_sr_object = list(
            submissions_between(self.r,
                                sr_obj,
                                verbosity=self.verbosity)
        )

        self.assertEqual(all_subs, all_subs_sr_object)

        all_subs_reversed = list(submissions_between(self.r,
                                                     sr_obj,
                                                     newest_first=False,
                                                     verbosity=self.verbosity))

        self.assertEqual(all_subs, list(reversed(all_subs_reversed)))

    @betamax()
    @teardown_on_keyboard_interrupt
    def test_submissions_between_with_filters(self):
        all_subs = list(submissions_between(self.r,
                                            self.sr,
                                            verbosity=self.verbosity))
        t1 = 1420000000
        t2 = 1441111111

        t1_t2_subs = list(submissions_between(self.r,
                                              self.sr,
                                              lowest_timestamp=t1,
                                              highest_timestamp=t2,
                                              verbosity=self.verbosity))

        def filter_subs(subs,
                        lowest_timestamp=0,
                        highest_timestamp=10**10,
                        criterion=None):
            filtered = [s for s in subs
                        if s.created_utc <= highest_timestamp
                        and s.created_utc >= lowest_timestamp
                        and (criterion is None or criterion(s))]
            # make sure we never accidentally craft a bad test case
            self.assertGreater(len(filtered), 0)
            return filtered

        t1_t2_subs_canon = filter_subs(all_subs, t1, t2)
        self.assertEqual(t1_t2_subs, t1_t2_subs_canon)

        self_subs = list(
            submissions_between(self.r,
                                self.sr,
                                extra_cloudsearch_fields={"self": "1"},
                                verbosity=self.verbosity)
        )
        self_subs_canon = filter_subs(all_subs,
                                      criterion=lambda s: s.is_self)
        self.assertEqual(self_subs, self_subs_canon)

        def wa_criterion(s):
            return not s.is_self and \
                urlparse(s.url).netloc == "web.archive.org"

        wa_cs_fields = {"self": "0",
                        "site": "web.archive.org"}

        subs_wa = list(
            submissions_between(self.r,
                                self.sr,
                                extra_cloudsearch_fields=wa_cs_fields,
                                verbosity=self.verbosity)
        )

        subs_wa_canon = filter_subs(all_subs, criterion=wa_criterion)
        self.assertEqual(subs_wa, subs_wa_canon)

        patu_cs_fields = {"self": "1",
                          "author": "PyAPITestUser2",
                          "title": "test"}

        def patu_criterion(s):
            return s.is_self and \
                s.author.name == "PyAPITestUser2" and\
                "test" in s.title.lower()

        subs_patu = list(
            submissions_between(self.r,
                                self.sr,
                                extra_cloudsearch_fields=patu_cs_fields,
                                verbosity=self.verbosity)
        )

        subs_patu_canon = filter_subs(all_subs, criterion=patu_criterion)
        self.assertEqual(subs_patu, subs_patu_canon)
