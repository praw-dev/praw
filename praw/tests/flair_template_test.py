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

from helper import configure, R, SR


def setup_function(function):
    configure()


def test_add_user_template():
    subreddit = R.get_subreddit(SR)
    subreddit.add_flair_template('text', 'css', True)


def test_add_link_template():
    subreddit = R.get_subreddit(SR)
    subreddit.add_flair_template('text', 'css', True, True)
    subreddit.add_flair_template(text='text', is_link=True)
    subreddit.add_flair_template(css_class='blah', is_link=True)
    subreddit.add_flair_template(is_link=True)


def test_clear_user_templates():
    subreddit = R.get_subreddit(SR)
    subreddit.clear_flair_templates()


def test_clear_link_templates():
    subreddit = R.get_subreddit(SR)
    subreddit.clear_flair_templates(True)
