"""Tests for Message class."""

from __future__ import print_function, unicode_literals
from praw import errors
from praw.objects import Message
from six import text_type
from .helper import OAuthPRAWTest, PRAWTest, betamax


class MessageTest(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.other_user = self.r.get_redditor(self.other_user_name)

    @betamax()
    def test_get_comment_replies(self):
        comment_reply = next(self.r.get_comment_replies(limit=1))
        comment_parent = self.r.get_info(thing_id=comment_reply.parent_id)
        self.assertEqual(comment_parent.author.name, self.r.user.name)

    @betamax()
    def test_get_message(self):
        message1 = next(self.r.get_inbox(limit=1))
        message2 = self.r.get_message(message1.id)
        self.assertEqual(message1, message2)
        self.assertEqual(self.r.user.name.lower(), message2.dest.lower())
        self.assertTrue(isinstance(message2.replies, list))

    @betamax()
    def test_get_post_replies(self):
        comment_reply = next(self.r.get_post_replies(limit=1))
        self.assertTrue(comment_reply.is_root)
        comment_parent = self.r.get_info(thing_id=comment_reply.parent_id)
        self.assertEqual(comment_parent.author.name, self.r.user.name)

    @betamax()
    def test_get_unread_update_has_mail(self):
        self.r.send_message(self.other_user_name, 'Update has mail', 'body')

        self.r.login(self.other_user_name, self.other_user_pswd,
                     disable_warning=True)
        self.assertTrue(self.r.user.has_mail)
        self.r.get_unread(limit=1, unset_has_mail=True, update_user=True)
        self.assertFalse(self.r.user.has_mail)

    @betamax()
    def test_mark_as_read(self):
        self.r.login(self.other_user_name, self.other_user_pswd,
                     disable_warning=True)
        msg = next(self.r.get_unread(limit=1))
        msg.mark_as_read()

        self.delay_for_listing_update()
        self.assertFalse(msg in self.r.get_unread(limit=5))

    @betamax()
    def test_mark_as_unread(self):
        self.r.login(self.other_user_name, self.other_user_pswd,
                     disable_warning=True)
        msg = self.first(self.r.get_inbox(), lambda msg: not msg.new)
        self.assertFalse(msg in self.r.get_unread())
        msg.mark_as_unread()

        self.delay_for_listing_update()
        self.assertTrue(msg in self.r.get_unread(limit=24))

    @betamax()
    def test_mark_multiple_as_read(self):
        self.r.login(self.other_user_name, self.other_user_pswd,
                     disable_warning=True)
        message_generator = self.r.get_unread(limit=None)
        messages = []
        while len(messages) < 2:
            message = next(message_generator)
            if message.author != self.r.user.name:
                messages.append(message)
        self.assertEqual(2, len(messages))
        self.r.user.mark_as_read(messages)

        self.delay_for_listing_update()
        unread = list(self.r.get_unread(limit=25))
        self.assertFalse(any(msg in unread for msg in messages))

    @betamax()
    def test_reply_to_message_and_verify(self):
        def predicate(msg):
            return isinstance(msg, Message) and msg.author == self.r.user

        message = self.first(self.r.get_inbox(), predicate)
        reply = message.reply('Message reply')
        self.assertEqual(message.fullname, reply.parent_id)

    @betamax()
    def test_send(self):
        subject = 'Subject: {0}'.format(self.r.modhash)
        self.none(self.r.get_inbox(), lambda msg: msg.subject == subject)
        self.r.user.send_message(subject, 'Message content')

        self.delay_for_listing_update()
        self.first(self.r.get_inbox(limit=24),
                   lambda msg: msg.subject == subject)

    @betamax()
    def test_send_from_subreddit(self):
        subject = 'Subject: {0}'.format(self.r.modhash)
        self.r.send_message(self.other_user_name, subject, 'Message content',
                            from_sr=self.sr)

        self.r.login(self.other_user_name, self.other_user_pswd,
                     disable_warning=True)
        message = next(self.r.get_unread(limit=1))
        self.assertEqual(None, message.author)
        self.assertEqual(self.sr, text_type(message.subreddit))
        self.assertEqual(subject, message.subject)

    @betamax()
    def test_send_invalid(self):
        self.assertRaises(errors.InvalidUser, self.r.send_message,
                          self.invalid_user_name, 'Subject', 'Content')


class OAuthMessageTest(OAuthPRAWTest):
    @betamax()
    def test_read_inbox_oauth(self):
        self.r.refresh_access_information(
            self.refresh_token['privatemessages'])
        self.assertTrue(list(self.r.get_inbox(limit=25)))

    @betamax()
    def test_send_privatemessage_oauth(self):
        self.r.refresh_access_information(
            self.refresh_token['privatemessages'])

        self.r.send_message(self.other_user_name, 'subject', 'body')
        message = next(self.r.get_sent(limit=1))

        reply = message.reply('body2')
        # Must use assertTrue because Python 2.6 doesn't have assertIsInstance
        self.assertTrue(isinstance(reply, Message))
        self.assertEqual(reply.parent_id, message.fullname)
