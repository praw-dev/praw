#!/usr/bin/env python

# This file is part of PRAW.
#
# PRAW is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PRAW is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PRAW.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable-msg=C0103, C0302, R0903, R0904, W0201

import unittest
import uuid
from six import next as six_next

from helper import AuthenticatedHelper, first, USER_AGENT
from praw import errors, Reddit
from praw.objects import Message


class MessageTest(unittest.TestCase, AuthenticatedHelper):
    def setUp(self):
        self.configure()

    def test_get_unread_update_has_mail(self):
        self.r.send_message(self.other_user_name, 'Update has mail', 'body')
        self.r.login(self.other_user_name, '1111')
        self.assertTrue(self.r.user.has_mail)
        self.r.get_unread(limit=1, unset_has_mail=True, update_user=True)
        self.assertFalse(self.r.user.has_mail)

    def test_mark_as_read(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        # pylint: disable-msg=E1101
        msg = six_next(oth.get_unread(limit=1))
        msg.mark_as_read()
        self.assertTrue(msg not in oth.get_unread(limit=5))

    def test_mark_as_unread(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        found = first(oth.get_inbox(), lambda msg: not msg.new)
        self.assertTrue(found is not None)
        found.mark_as_unread()
        self.assertTrue(found in oth.get_unread())

    def test_mark_multiple_as_read(self):
        oth = Reddit(USER_AGENT, disable_update_check=True)
        oth.login('PyAPITestUser3', '1111')
        messages = []
        for msg in oth.get_unread(limit=None):
            if msg.author != oth.user.name:
                messages.append(msg)
                if len(messages) >= 2:
                    break
        self.assertEqual(2, len(messages))
        oth.user.mark_as_read(messages)
        unread = list(oth.get_unread(limit=5))
        self.assertTrue(all(msg not in unread for msg in messages))

    def test_mod_mail_send(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.get_subreddit(self.sr).send_message(subject, 'Content')
        found = first(self.r.get_mod_mail(),
                      lambda msg: msg.subject == subject)
        self.assertTrue(found is not None)

    def test_reply_to_message_and_verify(self):
        text = 'Unique message reply: %s' % uuid.uuid4()
        found = first(self.r.get_inbox(),
                      lambda msg: isinstance(msg, Message)
                      and msg.author == self.r.user)
        self.assertTrue(found is not None)
        reply = found.reply(text)
        self.assertEqual(reply.parent_id, found.fullname)

    def test_send(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.r.user.send_message(subject, 'Message content')
        found = first(self.r.get_inbox(), lambda msg: msg.subject == subject)
        self.assertTrue(found is not None)

    def test_send_invalid(self):
        subject = 'Unique message: %s' % uuid.uuid4()
        self.assertRaises(errors.InvalidUser, self.r.send_message,
                          self.invalid_user_name, subject, 'Message content')
