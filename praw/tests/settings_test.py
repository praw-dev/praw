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

import uuid

from helper import configure, SUBREDDIT


def setup_function(function):
    configure()


def test_set_settings():
    title = 'Reddit API Test %s' % uuid.uuid4()
    SUBREDDIT.set_settings(title)
    assert SUBREDDIT.get_settings()['title'] == title


def test_set_stylesheet():
    stylesheet = ('div.titlebox span.number:after {\ncontent: " %s"\n' %
                  uuid.uuid4())
    SUBREDDIT.set_stylesheet(stylesheet)
    assert stylesheet == SUBREDDIT.get_stylesheet()['stylesheet']


def test_update_settings_description():
    settings = SUBREDDIT.get_settings()
    settings['description'] = 'Description %s' % uuid.uuid4()
    SUBREDDIT.update_settings(description=settings['description'])
    new = SUBREDDIT.get_settings()
    # The id should change, but nothing else
    key = 'prev_description_id'
    assert settings[key] != new[key]
    del settings[key]
    del new[key]
    assert settings == new


def test_update_settings_public_description():
    settings = SUBREDDIT.get_settings()
    settings['public_description'] = 'Description %s' % uuid.uuid4()
    SUBREDDIT.update_settings(
        public_description=settings['public_description'])
    new = SUBREDDIT.get_settings()
    # The id should change, but nothing else
    key = 'prev_public_description_id'
    assert settings[key] != new[key]
    del settings[key]
    del new[key]
    assert settings == new
