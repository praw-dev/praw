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

import pytest
import uuid
from six import next as six_next

from helper import (configure, first, INVALID_USER_NAME, OTHER_USER_NAME,
                    USER_AGENT, R, SUBREDDIT)
from praw import errors, Reddit
from praw.objects import Message


def setup_function(function):
    configure()


def test_get_unread_update_has_mail():
    R.send_message(OTHER_USER_NAME, 'Update has mail', 'body')
    R.login(OTHER_USER_NAME, '1111')
    assert R.user.has_mail
    R.get_unread(limit=1, unset_has_mail=True, update_user=True)
    assert not R.user.has_mail


def test_mark_as_read():
    oth = Reddit(USER_AGENT, disable_update_check=True)
    oth.login('PyAPITestUser3', '1111')
    # pylint: disable-msg=E1101
    msg = six_next(oth.get_unread(limit=1))
    msg.mark_as_read()
    assert msg not in oth.get_unread(limit=5)


def test_mark_as_unread():
    oth = Reddit(USER_AGENT, disable_update_check=True)
    oth.login('PyAPITestUser3', '1111')
    found = first(oth.get_inbox(), lambda msg: not msg.new)
    assert found is not None
    found.mark_as_unread()
    assert found in oth.get_unread()


def test_mark_multiple_as_read():
    oth = Reddit(USER_AGENT, disable_update_check=True)
    oth.login('PyAPITestUser3', '1111')
    messages = []
    for msg in oth.get_unread(limit=None):
        if msg.author != oth.user.name:
            messages.append(msg)
            if len(messages) >= 2:
                break
    assert 2 == len(messages)
    oth.user.mark_as_read(messages)
    unread = list(oth.get_unread(limit=5))
    assert all(msg not in unread for msg in messages)


def test_mod_mail_send():
    subject = 'Unique message: %s' % uuid.uuid4()
    SUBREDDIT.send_message(subject, 'Content')
    found = first(R.get_mod_mail(), lambda msg: msg.subject == subject)
    assert found is not None


def test_reply_to_message_and_verify():
    text = 'Unique message reply: %s' % uuid.uuid4()
    found = first(R.get_inbox(),
                  lambda msg: isinstance(msg, Message)
                  and msg.author == R.user)
    assert found is not None
    reply = found.reply(text)
    assert reply.parent_id == found.fullname


def test_send():
    subject = 'Unique message: %s' % uuid.uuid4()
    R.user.send_message(subject, 'Message content')
    found = first(R.get_inbox(), lambda msg: msg.subject == subject)
    assert found is not None


def test_send_invalid():
    subject = 'Unique message: %s' % uuid.uuid4()
    with pytest.raises(errors.InvalidUser):
        R.send_message(INVALID_USER_NAME, subject, 'Message content')
