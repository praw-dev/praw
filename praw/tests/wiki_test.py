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

from six import text_type
import unittest
import uuid

from helper import BasicHelper


class WikiTests(unittest.TestCase, BasicHelper):
    def setUp(self):
        self.configure()
        self.subreddit = self.r.get_subreddit(self.sr)

    def test_edit_wiki_page(self):
        self.r.login(self.un, '1111')
        page = self.subreddit.get_wiki_page('test')
        content = 'Body: {0}'.format(uuid.uuid4())
        page.edit(content)
        self.disable_cache()
        page = self.subreddit.get_wiki_page('test')
        self.assertEqual(content, page.content_md)

    def test_get_wiki_page(self):
        self.assertEqual(
            'ucsantabarbara:index',
            text_type(self.r.get_wiki_page('ucsantabarbara', 'index')))

    def test_get_wiki_pages(self):
        retval = self.subreddit.get_wiki_pages()
        self.assertTrue(len(retval) > 0)
        tmp = self.subreddit.get_wiki_page(retval[0].page).content_md
        self.assertEqual(retval[0].content_md, tmp)
