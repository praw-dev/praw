"""Tests for Subreddit flair."""

from __future__ import print_function, unicode_literals
from praw import errors
from .helper import PRAWTest, betamax, flair_diff


class FlairTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_add_link_flair(self):
        flair_text = 'Flair: {0}'.format(self.r.modhash)
        submission = next(self.subreddit.get_new())
        submission.set_flair(flair_text)
        self.assertEqual(flair_text, submission.refresh().link_flair_text)

    @betamax()
    def test_add_user_flair__css_only(self):
        flair_css = self.r.modhash
        self.subreddit.set_flair(self.r.user, flair_css_class=flair_css)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(None, flair['flair_text'])
        self.assertEqual(flair_css, flair['flair_css_class'])

    @betamax()
    def test_add_user_flair__text_and_css(self):
        flair_text = 'Text & CSS: {0}'.format(self.r.modhash)
        flair_css = self.r.modhash
        self.subreddit.set_flair(self.r.user, flair_text, flair_css)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(flair_text, flair['flair_text'])
        self.assertEqual(flair_css, flair['flair_css_class'])

    @betamax()
    def test_add_user_flair__text_only(self):
        flair_text = 'Text Only: {0}'.format(self.r.modhash)
        self.subreddit.set_flair(self.r.user, flair_text)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(flair_text, flair['flair_text'])
        self.assertEqual(None, flair['flair_css_class'])

    @betamax()
    def test_add_user_flair_to_invalid_user(self):
        self.assertRaises(errors.InvalidFlairTarget, self.subreddit.set_flair,
                          self.invalid_user_name)

    @betamax()
    def test_clear_user_flair(self):
        self.subreddit.set_flair(self.r.user)
        flair = self.subreddit.get_flair(self.r.user)
        self.assertEqual(None, flair['flair_text'])
        self.assertEqual(None, flair['flair_css_class'])

    @betamax()
    def test_delete_flair(self):
        flair = next(self.subreddit.get_flair_list(limit=1))
        self.subreddit.delete_flair(flair['user'])
        self.assertTrue(flair not in self.subreddit.get_flair_list())

    @betamax()
    def test_flair_csv_and_flair_list(self):
        # Clear all flair
        self.subreddit.clear_all_flair()
        self.delay_for_listing_update()
        self.assertEqual([], list(self.subreddit.get_flair_list(limit=1023)))
        # Set flair
        flair_mapping = [{'user': 'reddit', 'flair_text': 'dev'},
                         {'user': self.un, 'flair_css_class': 'xx'},
                         {'user': self.other_user_name,
                          'flair_text': 'AWESOME',
                          'flair_css_class': 'css'}]
        self.subreddit.set_flair_csv(flair_mapping)
        self.assertEqual([], flair_diff(flair_mapping,
                                        list(self.subreddit.get_flair_list())))

    @betamax()
    def test_flair_csv_empty(self):
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, [])

    @betamax()
    def test_flair_csv_many(self):
        users = ('reddit', self.un, self.other_user_name)
        flair_text_a = 'Flair: {0}'.format(self.r.modhash)
        flair_text_b = 'Second Flair: {0}'.format(self.r.modhash)
        flair_mapping = [{'user': 'reddit', 'flair_text': flair_text_a}] * 99
        for user in users:
            flair_mapping.append({'user': user, 'flair_text': flair_text_b})
        self.subreddit.set_flair_csv(flair_mapping)
        for user in users:
            flair = self.subreddit.get_flair(user)
            self.assertEqual(flair_text_b, flair['flair_text'])

    @betamax()
    def test_flair_csv_optional_args(self):
        flair_mapping = [{'user': 'reddit', 'flair_text': 'reddit'},
                         {'user': self.other_user_name, 'flair_css_class':
                          'blah'}]
        self.subreddit.set_flair_csv(flair_mapping)
        expected = {'flair_css_class': '', 'flair_text': 'reddit',
                    'user': 'reddit'}
        self.assertEqual(expected, self.subreddit.get_flair('reddit'))
        expected = {'flair_css_class': 'blah', 'flair_text': None,
                    'user': self.other_user_name}
        self.assertEqual(expected,
                         self.subreddit.get_flair(self.other_user_name))

    @betamax()
    def test_flair_csv_requires_user(self):
        flair_mapping = [{'flair_text': 'hsdf'}]
        self.assertRaises(errors.ClientException,
                          self.subreddit.set_flair_csv, flair_mapping)


class FlairSelectorTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.priv_sr)
        self.user_flair_templates = (
            ('UserCssClassOne', ('21e00aae-09cf-11e3-a4f1-12313d281541',
                                 'default_user_flair_text_one')),
            ('UserCssClassTwo', ('2f6504c2-09cf-11e3-9d8d-12313d281541',
                                 'default_user_flair_text_two')))
        self.link_flair_templates = (
            ('LinkCssClassOne', ('36a573c0-09cf-11e3-b5f7-12313d096169',
                                 'default_link_flair_text_one')),
            ('LinkCssClassTwo', ('3b73f516-09cf-11e3-9a71-12313d281541',
                                 'default_link_flair_text_two')))

    def new_user_flair_class(self):
        flair = self.subreddit.get_flair(self.r.user)['flair_css_class']
        return next(x for x in self.user_flair_templates if x[0] != flair)

    def new_link_flair_class(self, submission):
        flair = submission.link_flair_css_class
        return next(x for x in self.link_flair_templates if x[0] != flair)

    @betamax()
    def test_add_link_flair_to_invalid_subreddit(self):
        submission = next(self.r.get_subreddit('python').get_new())
        self.assertRaises(errors.Forbidden,
                          self.subreddit.set_flair, submission, 'text')

    @betamax()
    def test_select_link_flair(self):
        sub = next(self.subreddit.get_new())
        f_class, (f_id, f_default_text) = self.new_link_flair_class(sub)
        sub.select_flair(flair_template_id=f_id)
        sub.refresh()
        self.assertEqual(f_default_text, sub.link_flair_text)
        self.assertEqual(f_class, sub.link_flair_css_class)

    @betamax()
    def test_select_link_flair_custom_text(self):
        sub = next(self.subreddit.get_new())
        flair_class, (flair_id, _) = self.new_link_flair_class(sub)
        flair_text = 'Flair: {0}'.format(self.r.modhash)
        sub.select_flair(flair_template_id=flair_id, flair_text=flair_text)
        sub.refresh()
        self.assertEqual(flair_text, sub.link_flair_text)
        self.assertEqual(flair_class, sub.link_flair_css_class)

    @betamax()
    def test_select_link_flair_remove(self):
        sub = next(self.subreddit.get_new())
        if sub.link_flair_css_class is None:
            flair_id = self.new_link_flair_class(sub)[0][1]
            sub.select_flair(flair_template_id=flair_id)
        sub.select_flair()
        sub.refresh()
        self.assertEqual(None, sub.link_flair_text)
        self.assertEqual(None, sub.link_flair_css_class)

    @betamax()
    def test_select_user_flair(self):
        f_class, (f_id, f_default_text) = self.new_user_flair_class()
        self.subreddit.select_flair(flair_template_id=f_id)
        flair = self.subreddit.get_flair(self.r.user, uniq=1)
        self.assertEqual(f_default_text, flair['flair_text'])
        self.assertEqual(f_class, flair['flair_css_class'])

    @betamax()
    def test_select_user_flair_custom_text(self):
        flair_class, (flair_id, _) = self.new_user_flair_class()
        flair_text = 'Flair: {0}'.format(self.r.modhash)
        self.subreddit.select_flair(flair_template_id=flair_id,
                                    flair_text=flair_text)
        flair = self.subreddit.get_flair(self.r.user, uniq=1)
        self.assertEqual(flair_text, flair['flair_text'])
        self.assertEqual(flair_class, flair['flair_css_class'])

    @betamax()
    def test_select_user_flair_remove(self):
        flair = self.subreddit.get_flair(self.r.user)
        if flair['flair_css_class'] is None:
            flair_id = self.new_user_flair_class()[1][0]
            self.subreddit.select_flair(flair_template_id=flair_id)
        self.subreddit.select_flair()
        flair = self.subreddit.get_flair(self.r.user, uniq=1)
        self.assertEqual(None, flair['flair_text'])
        self.assertEqual(None, flair['flair_css_class'])
