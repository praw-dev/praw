"""Tests for Subreddit class."""

from __future__ import print_function, unicode_literals
import warnings
from praw import errors
from praw.objects import Subreddit
from six import text_type
from .helper import OAuthPRAWTest, PRAWTest, betamax


class SubredditTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_attribute_error(self):
        self.assertRaises(AttributeError, getattr, self.subreddit, 'foo')

    @betamax()
    def test_display_name_lazy_update(self):
        augmented_name = self.sr.upper()
        subreddit = self.r.get_subreddit(augmented_name)
        self.assertEqual(augmented_name, text_type(subreddit))
        subreddit.created_utc  # induce a lazy load
        self.assertEqual(augmented_name, subreddit.display_name)
        subreddit.refresh()
        self.assertEqual(self.sr, subreddit.display_name)

    @betamax()
    def test_display_name_refresh(self):
        augmented_name = self.sr.upper()
        subreddit = self.r.get_subreddit(augmented_name)
        self.assertEqual(augmented_name, text_type(subreddit))
        subreddit.refresh()
        self.assertEqual(self.sr, subreddit.display_name)
        self.assertEqual(subreddit.display_name, text_type(subreddit))

    @betamax()
    def test_get_contributors_private(self):
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd,
                     disable_warning=True)
        private_sub = self.r.get_subreddit(self.priv_sr)
        self.assertEqual('private', private_sub.subreddit_type)
        self.assertTrue(list(private_sub.get_contributors()))

    @betamax()
    def test_get_contributors_public(self):
        self.assertEqual('public', self.subreddit.subreddit_type)
        self.assertTrue(list(self.subreddit.get_contributors()))

    @betamax()
    def test_get_contributors_public_exception(self):
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd,
                     disable_warning=True)
        self.assertRaises(errors.ModeratorRequired,
                          self.subreddit.get_contributors)

    @betamax()
    def test_get_my_contributions(self):
        self.first(self.r.get_my_contributions(),
                   lambda subreddit: text_type(subreddit) == self.sr)

    @betamax()
    def test_get_my_moderation(self):
        self.first(self.r.get_my_moderation(),
                   lambda subreddit: text_type(subreddit) == self.sr)

    @betamax()
    def test_get_my_subreddits(self):
        for subreddit in self.r.get_my_subreddits():
            self.assertTrue(text_type(subreddit) in subreddit._info_url)

    @betamax()
    def test_get_subreddit_recommendations(self):
        result = self.r.get_subreddit_recommendations(['python', 'redditdev'])
        self.assertTrue(result)
        self.assertTrue(all(isinstance(x, Subreddit) for x in result))

    @betamax()
    def test_multiple_subreddit__fetch(self):
        with warnings.catch_warnings(record=True) as w:
            self.r.get_subreddit('python+redditdev', fetch=True)
            assert len(w) == 1
            assert isinstance(w[0].message, UserWarning)

    @betamax()
    def test_subreddit_refresh(self):
        new_description = 'Description {0}'.format(self.r.modhash)
        self.assertNotEqual(new_description, self.subreddit.public_description)
        self.subreddit.update_settings(public_description=new_description)
        self.subreddit.refresh()
        self.assertEqual(new_description, self.subreddit.public_description)

    @betamax()
    def test_subreddit_search(self):
        self.assertTrue(list(self.subreddit.search('test')))

    @betamax()
    def test_subscribe_and_unsubscribe(self):
        self.subreddit.subscribe()

        self.delay_for_listing_update()
        self.assertTrue(self.subreddit in self.r.get_my_subreddits())
        self.subreddit.unsubscribe()

        self.delay_for_listing_update()
        self.assertFalse(self.subreddit in
                         self.r.get_my_subreddits(params={'u': 1}))


class ModeratorSubredditTest(PRAWTest):
    def add_remove(self, add, remove, listing, add_callback=None):
        other = self.r.get_redditor(self.other_user_name)

        add(other)
        if add_callback:
            add_callback()
        self.assertTrue(other in listing())

        remove(other)
        self.assertFalse(other in listing(params={'u': 1}))

    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)

    @betamax()
    def test_accept_moderator_invite_fail(self):
        self.assertRaises(errors.InvalidInvite,
                          self.subreddit.accept_moderator_invite)

    @betamax()
    def test_add_moderator__failure(self):
        self.assertTrue(self.r.user in self.subreddit.get_moderators())
        self.assertRaises(errors.AlreadyModerator,
                          self.subreddit.add_moderator, text_type(self.r.user))
        self.assertRaises(errors.AlreadyModerator,
                          self.subreddit.add_moderator, self.r.user)

    @betamax()
    def test_ban(self):
        self.add_remove(self.subreddit.add_ban, self.subreddit.remove_ban,
                        self.subreddit.get_banned)

    @betamax()
    def test_contributors(self):
        self.add_remove(self.subreddit.add_contributor,
                        self.subreddit.remove_contributor,
                        self.subreddit.get_contributors)

    @betamax()
    def test_get_banned__note(self):
        params = {'user': self.other_non_mod_name}
        data = next(self.subreddit.get_banned(user_only=False, params=params))
        self.assertEqual('no reason in particular 2', data['note'])

    @betamax()
    def test_get_mod_log(self):
        self.assertTrue(list(self.subreddit.get_mod_log()))

    @betamax()
    def test_get_mod_log_with_mod_by_name(self):
        other = self.r.get_redditor(self.other_user_name)
        actions = list(self.subreddit.get_mod_log(mod=other.name))
        self.assertTrue(actions)
        self.assertTrue(all(x.mod.lower() == other.name.lower()
                            for x in actions))

    @betamax()
    def test_get_mod_log_with_mod_by_redditor_object(self):
        other = self.r.get_redditor(self.other_user_name)
        actions = list(self.subreddit.get_mod_log(mod=other))
        self.assertTrue(actions)
        self.assertTrue(all(x.mod.lower() == other.name.lower()
                            for x in actions))

    @betamax()
    def test_get_mod_log_with_action_filter(self):
        actions = list(self.subreddit.get_mod_log(action='removelink'))
        self.assertTrue(actions)
        self.assertTrue(all(x.action == 'removelink' for x in actions))

    @betamax()
    def test_get_mod_queue(self):
        self.assertTrue(list(self.r.get_subreddit('mod').get_mod_queue()))

    @betamax()
    def test_get_mod_queue_with_default_subreddit(self):
        self.assertTrue(list(self.r.get_mod_queue()))

    @betamax()
    def test_get_mod_queue_multi(self):
        multi = '{0}+{1}'.format(self.sr, self.priv_sr)
        self.assertTrue(list(self.r.get_subreddit(multi).get_mod_queue()))

    @betamax()
    def test_get_unmoderated(self):
        self.assertTrue(list(self.subreddit.get_unmoderated()))

    @betamax()
    def test_mod_mail_send(self):
        subject = 'Unique message: AAAA'
        self.r.get_subreddit(self.sr).send_message(subject, 'Content')
        self.first(self.r.get_mod_mail(), lambda msg: msg.subject == subject)

    @betamax()
    def test_moderator(self):
        def add_callback():
            self.r.login(self.other_user_name, self.other_user_pswd,
                         disable_warning=True)
            self.r.get_subreddit(self.sr).accept_moderator_invite()
            self.r.login(self.un, self.un_pswd, disable_warning=True)

        self.add_remove(self.subreddit.add_moderator,
                        self.subreddit.remove_moderator,
                        self.subreddit.get_moderators,
                        add_callback)

    @betamax()
    def test_set_settings(self):
        # The only required argument is title. All others will be set
        # to their defaults.
        title = 'Reddit API Test {0}'.format(self.r.modhash)
        self.subreddit.set_settings(title)
        settings = self.subreddit.get_settings()
        self.assertEqual(title, settings['title'])
        for setting in ['description', 'public_description']:
            self.assertEqual('', settings[setting])

    @betamax()
    def test_set_stylesheet(self):
        self.assertRaises(errors.BadCSS, self.subreddit.set_stylesheet,
                          'INVALID CSS')

        stylesheet = ('div.titlebox span.number:after {{\ncontent: " {0}"\n}}'
                      .format(self.r.modhash))
        self.subreddit.set_stylesheet(stylesheet)
        self.assertEqual(stylesheet,
                         self.subreddit.get_stylesheet()['stylesheet'])

        self.subreddit.set_stylesheet('')
        self.assertEqual(
            '', self.subreddit.get_stylesheet(uniq=1)['stylesheet'])

    @betamax()
    def test_update_settings__descriptions(self):
        self.maxDiff = None
        settings = self.subreddit.get_settings()
        settings['description'] = 'Description {0}'.format(self.r.modhash)
        settings['public_description'] = ('Public Description {0}'
                                          .format(self.r.modhash))
        self.subreddit.update_settings(
            description=settings['description'],
            public_description=settings['public_description'])
        self.assertEqual(settings, self.subreddit.get_settings(uniq=1))

    @betamax()
    def test_wiki_ban(self):
        self.add_remove(self.subreddit.add_wiki_ban,
                        self.subreddit.remove_wiki_ban,
                        self.subreddit.get_wiki_banned)

    @betamax()
    def test_wiki_contributors(self):
        self.add_remove(self.subreddit.add_wiki_contributor,
                        self.subreddit.remove_wiki_contributor,
                        self.subreddit.get_wiki_contributors)


class OAuthSubredditTest(OAuthPRAWTest):
    @betamax()
    def test_add_remove_moderator_oauth(self):
        self.r.refresh_access_information(self.refresh_token['modothers'])
        subreddit = self.r.get_subreddit(self.sr)
        subreddit.add_moderator(self.other_user_name)

        # log in as other user
        self.r.refresh_access_information(self.other_refresh_token['modself'])
        self.r.accept_moderator_invite(self.sr)

        # now return to original user.
        self.r.refresh_access_information(self.refresh_token['modothers'])
        subreddit.remove_moderator(self.other_user_name)

        self.assertFalse(self.other_user_name.lower() in [user.name.lower()
                         for user in subreddit.get_moderators()])

    @betamax()
    def test_get_edited_oauth(self):
        self.r.refresh_access_information(self.refresh_token['read'])

        edits = self.r.get_subreddit(self.sr).get_edited()
        self.assertTrue(list(edits))
        self.assertTrue(all(hasattr(x, 'edited') for x in edits))
        self.assertTrue(all(isinstance(x.edited, (float, int)) for x in edits))

    @betamax()
    def test_get_moderators_contributors_oauth(self):
        self.r.refresh_access_information(self.refresh_token['read'])

        subreddit = self.r.get_subreddit(self.sr)
        self.assertTrue(list(subreddit.get_moderators()))
        self.assertTrue(list(subreddit.get_contributors()))

        subreddit = self.r.get_subreddit('redditdev')
        self.assertTrue(list(subreddit.get_moderators()))
        self.assertRaises(errors.Forbidden, list, subreddit.get_contributors())

    @betamax()
    def test_get_modlog_oauth(self):
        num = 50
        self.r.refresh_access_information(self.refresh_token['modlog'])
        result = self.r.get_subreddit(self.sr).get_mod_log(limit=num)
        self.assertEqual(num, len(list(result)))

    @betamax()
    def test_get_priv_sr_comments_oauth(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        self.assertTrue(list(self.r.get_comments(self.priv_sr)))

    @betamax()
    def test_get_priv_sr_listing_oauth(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        subreddit = self.r.get_subreddit(self.priv_sr)
        self.assertTrue(list(subreddit.get_top()))

    @betamax()
    def test_join_leave_moderator_oauth(self):
        subreddit = self.r.get_subreddit(self.sr)
        self.r.refresh_access_information(self.refresh_token['modothers'])
        subreddit.add_moderator(self.other_user_name)
        self.r.refresh_access_information(
            self.refresh_token['modcontributors'])
        subreddit.add_contributor(self.other_user_name)

        # log in as other user
        self.r.refresh_access_information(self.other_refresh_token['modself'])
        self.r.accept_moderator_invite(self.sr)

        self.r.leave_moderator(subreddit)
        subreddit.leave_contributor()

        subreddit.refresh()
        self.assertFalse(subreddit.user_is_moderator)
        self.assertFalse(subreddit.user_is_contributor)

    @betamax()
    def test_mute_unmute_oauth(self):
        self.r.refresh_access_information(
            self.refresh_token['modcontributors'])
        subreddit = self.r.get_subreddit(self.sr)

        def user_is_muted(username, cachebuster):
            self.r.refresh_access_information(self.refresh_token['read'])
            mutes = list(subreddit.get_muted(params={'uniq': cachebuster}))
            self.r.refresh_access_information(
                self.refresh_token['modcontributors'])
            return any(mute['name'] == username for mute in mutes)

        user = self.r.get_redditor(self.other_user_name)
        subreddit.add_mute(user)  # by Redditor obj
        self.assertTrue(user_is_muted(self.other_user_name, 1))
        subreddit.remove_mute(user.name)  # by string
        self.assertFalse(user_is_muted(self.other_user_name, 2))

        self.r.refresh_access_information(
            self.refresh_token['privatemessages'])
        modmail = next(subreddit.get_mod_mail())
        self.r.refresh_access_information(
            self.refresh_token['modcontributors'])

        sender = modmail.author.name
        modmail.mute_modmail_author()
        self.assertTrue(user_is_muted(sender, 3))
        modmail.unmute_modmail_author()
        self.assertFalse(user_is_muted(sender, 4))

    @betamax()
    def test_raise_invalidsubreddit_oauth(self):
        self.r.refresh_access_information(self.refresh_token['submit'])
        self.assertRaises(errors.InvalidSubreddit, self.r.submit, '?', 'title',
                          'body')
        invalid_sub = errors.InvalidSubreddit()
        self.assertEqual(invalid_sub.ERROR_TYPE, str(invalid_sub))

    @betamax()
    def test_set_stylesheet_oauth(self):
        subreddit = self.r.get_subreddit(self.sr)
        self.r.refresh_access_information(self.refresh_token['modconfig'])
        subreddit.set_stylesheet('*{}')
        self.assertEqual(subreddit.get_stylesheet()['stylesheet'], '*{}')
        subreddit.set_stylesheet('')

    @betamax()
    def test_set_settings_oauth(self):
        subreddit = self.r.get_subreddit(self.sr)
        self.r.refresh_access_information(self.refresh_token['modconfig'])
        new_title = subreddit.title + 'x' if len(subreddit.title) < 99 else 'x'
        subreddit.set_settings(title=new_title)
        subreddit.refresh()
        self.assertEqual(subreddit.title, new_title)

    @betamax()
    def test_subscribe_oauth(self):
        subreddit = self.r.get_subreddit(self.sr)

        # Subreddit.user_is_subscriber returns NoneType without `read`.
        # Refreshing back and forth is inconvenient, but less hackish
        # than storing / reassigning access tokens manually, so it's okay.
        self.r.refresh_access_information(self.refresh_token['subscribe'])
        subreddit.subscribe()
        self.r.refresh_access_information(self.refresh_token['read'])
        subreddit.refresh()
        self.assertTrue(subreddit.user_is_subscriber)

        self.r.refresh_access_information(self.refresh_token['subscribe'])
        subreddit.unsubscribe()
        self.r.refresh_access_information(self.refresh_token['read'])
        subreddit.refresh()
        self.assertFalse(subreddit.user_is_subscriber)
