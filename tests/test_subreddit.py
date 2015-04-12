"""Tests for Subreddit class."""

from __future__ import print_function, unicode_literals

from .helper import PRAWTest, betamax


class ModeratorSubredditTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax
    def test_get_mod_log(self):
        self.assertTrue(list(self.subreddit.get_mod_log()))

    @betamax
    def test_get_mod_log_with_mod_by_name(self):
        other = self.r.get_redditor(self.other_user_name)
        actions = list(self.subreddit.get_mod_log(mod=other.name))
        self.assertTrue(actions)
        self.assertTrue(all(x.mod.lower() == other.name.lower()
                            for x in actions))

    @betamax
    def test_get_mod_log_with_mod_by_redditor_object(self):
        other = self.r.get_redditor(self.other_user_name)
        actions = list(self.subreddit.get_mod_log(mod=other))
        self.assertTrue(actions)
        self.assertTrue(all(x.mod.lower() == other.name.lower()
                            for x in actions))

    @betamax
    def test_get_mod_log_with_action_filter(self):
        actions = list(self.subreddit.get_mod_log(action='removelink'))
        self.assertTrue(actions)
        self.assertTrue(all(x.action == 'removelink' for x in actions))

    @betamax
    def test_get_mod_queue(self):
        self.assertTrue(list(self.r.get_subreddit('mod').get_mod_queue()))

    @betamax
    def test_get_mod_queue_with_default_subreddit(self):
        self.assertTrue(list(self.r.get_mod_queue()))

    @betamax
    def test_get_mod_queue_multi(self):
        multi = '{0}+{1}'.format(self.sr, self.priv_sr)
        self.assertTrue(list(self.r.get_subreddit(multi).get_mod_queue()))

    @betamax
    def test_get_unmoderated(self):
        self.assertTrue(list(self.subreddit.get_unmoderated()))

    @betamax
    def test_mod_mail_send(self):
        subject = 'Unique message: AAAA'
        self.r.get_subreddit(self.sr).send_message(subject, 'Content')
        self.first(self.r.get_mod_mail(), lambda msg: msg.subject == subject)
