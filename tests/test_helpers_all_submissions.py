"""Tests for UnauthenticatedReddit class."""

from __future__ import print_function, unicode_literals

from praw.helpers import all_submissions
from .helper import PRAWTest, betamax


class TestHelperAllSubmissions(PRAWTest):
    @betamax()
    def test_all_submissions(self):
        test_now = 1448923624

        all_subs = list(all_submissions(self.r,
                                        self.sr,
                                        highest_timestamp=test_now,
                                        verbosity=3))

        for i in xrange(len(all_subs) - 1):
            self.assertGreaterEqual(all_subs[i].created_utc,
                                    all_subs[i + 1].created_utc)

        sr_obj = self.r.get_subreddit(self.sr)
        all_subs_sr_object = list(all_submissions(self.r,
                                                  sr_obj,
                                                  highest_timestamp=test_now,
                                                  verbosity=3))

        def get_submissions_data(submissions_list):
            return [(s.created_utc, s.title, s.url) for s in submissions_list]

        self.assertItemsEqual(get_submissions_data(all_subs),
                              get_submissions_data(all_subs_sr_object))

        all_subs_reversed = list(all_submissions(self.r,
                                                 self.r.get_subreddit(self.sr),
                                                 highest_timestamp=test_now,
                                                 newest_first=False,
                                                 verbosity=3))

        self.assertItemsEqual(get_submissions_data(all_subs),
                              get_submissions_data(reversed(all_subs_reversed)))

        t1 = 1440000000
        t2 = 1441111111

        t1_t2_subs = list(all_submissions(self.r,
                                          self.sr,
                                          lowest_timestamp=t2,
                                          highest_timestamp=t1,
                                          verbosity=3))

        def filter_subs_between(subs, lowest_timestamp, highest_timestamp):
            return [s for s in subs
                    if s.created_utc <= highest_timestamp
                    and s.created_utc >= lowest_timestamp]

        t1_t2_subs_canon = filter_subs_between(all_subs, t1, t2)
        self.assertItemsEqual(get_submissions_data(t1_t2_subs),
                              get_submissions_data(t1_t2_subs_canon))
