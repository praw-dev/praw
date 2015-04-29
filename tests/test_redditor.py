"""Tests for Redditor class."""

from __future__ import print_function, unicode_literals
from praw.objects import LoggedInRedditor
from six import text_type
from .helper import PRAWTest, betamax


class RedditorTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.other_user = self.r.get_redditor(self.other_user_name)

    @betamax
    def test_add_remove_friends(self):
        friends = self.r.user.get_friends()
        redditor = friends[0] if friends else self.other_user
        redditor.unfriend()

        self.delay_for_listing_update()
        self.assertTrue(redditor not in self.r.user.get_friends(u=1))
        redditor.friend()

        self.delay_for_listing_update()
        self.assertTrue(redditor in self.r.user.get_friends(u=2))

    @betamax
    def test_duplicate_login(self):
        self.assertEqual(self.un, self.r.user.name)
        self.r.login(self.other_user_name, self.other_user_pswd,
                     disable_warning=True)
        self.assertEqual(self.other_user_name, self.r.user.name)

    @betamax
    def test_get_liked_and_disliked(self):
        user = self.r.user
        sub = self.r.submit(self.sr, 'Sub Title', 'Sub Body')

        self.delay_for_listing_update()
        self.assertEqual(sub, next(user.get_liked()))
        sub.downvote()

        self.delay_for_listing_update()
        self.assertEqual(sub, next(user.get_disliked()))
        self.assertNotEqual(sub, next(user.get_liked(params={'u': 1})))
        sub.upvote()

        self.delay_for_listing_update()
        self.assertEqual(sub, next(user.get_liked(params={'u': 2})))
        self.assertNotEqual(sub, next(user.get_disliked(params={'u': 2})))

    @betamax
    def test_get_hidden(self):
        submission = next(self.r.user.get_hidden())
        submission.hide()

        self.delay_for_listing_update()
        self.assertEqual(submission,
                         next(self.r.user.get_hidden(params={'u': 1})))
        submission.unhide()

        self.delay_for_listing_update()
        self.assertNotEqual(submission,
                            next(self.r.user.get_hidden(params={'u': 2})))

    @betamax
    def test_get_redditor(self):
        self.assertEqual(self.other_user_id, self.other_user.id)

    @betamax
    def test_get_submitted(self):
        redditor = self.r.get_redditor(self.other_non_mod_name)
        self.assertTrue(list(redditor.get_submitted()))

    @betamax
    def test_redditor_comparison(self):
        a1 = next(self.r.get_new()).author
        a2 = self.r.get_redditor(text_type(a1))
        self.assertEqual(a1, a2)
        s1 = next(a1.get_submitted())
        s2 = next(a2.get_submitted())
        self.assertEqual(s1, s2)

    @betamax
    def test_user_set_on_login(self):
        self.assertTrue(isinstance(self.r.user, LoggedInRedditor))
