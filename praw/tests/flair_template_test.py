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

from praw.tests.helper import configure, SUBREDDIT


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def test_add_user_template():
    SUBREDDIT.add_flair_template('text', 'css', True)


def test_add_link_template():
    SUBREDDIT.add_flair_template('text', 'css', True, True)
    SUBREDDIT.add_flair_template(text='text', is_link=True)
    SUBREDDIT.add_flair_template(css_class='blah', is_link=True)
    SUBREDDIT.add_flair_template(is_link=True)


def test_clear_user_templates():
    SUBREDDIT.clear_flair_templates()


def test_clear_link_templates():
    SUBREDDIT.clear_flair_templates(True)
