from __future__ import print_function, unicode_literals

import unittest
from praw.decorators import _embed_text, restrict_access


class DecoratorTest(unittest.TestCase):
    def test_require_access_failure(self):
        self.assertRaises(TypeError, restrict_access, scope=None,
                          oauth_only=True)


class EmbedTextTest(unittest.TestCase):
    EMBED_TEXT = "HELLO"

    def test_no_docstring(self):
        new_doc = _embed_text(None, self.EMBED_TEXT)
        self.assertEqual(self.EMBED_TEXT + '\n\n', new_doc)

    def test_one_liner(self):
        new_doc = _embed_text("Returns something cool", self.EMBED_TEXT)
        self.assertEqual("Returns something cool\n\n{0}\n\n"
                         .format(self.EMBED_TEXT), new_doc)

    def test_multi_liner(self):
        doc = """Jiggers the bar

              Only run if foo is instantiated.

              """
        new_doc = _embed_text(doc, self.EMBED_TEXT)
        self.assertEqual(doc + self.EMBED_TEXT + '\n\n\n              ',
                         new_doc)

    def test_single_plus_params(self):
        doc = """Jiggers the bar

              :params foo: Self explanatory.

              """
        expected_doc = """Jiggers the bar

              :params foo: Self explanatory.

              {0}


              """.format(self.EMBED_TEXT)
        new_doc = _embed_text(doc, self.EMBED_TEXT)
        self.assertEqual(expected_doc, new_doc)

    def test_multi_plus_params(self):
        doc = """Jiggers the bar

              Jolly importment.

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              """
        expected_doc = """Jiggers the bar

              Jolly importment.

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              {0}


              """.format(self.EMBED_TEXT)
        new_doc = _embed_text(doc, self.EMBED_TEXT)
        self.assertEqual(expected_doc, new_doc)

    def test_additional_params(self):
        doc = """Jiggers the bar

              Jolly important.

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              The additional parameters are passed directly into
              :meth:`.get_content`. Note: the `url` parameter cannot be
              altered.

              """
        expected_doc = """Jiggers the bar

              Jolly important.

              :params foo: Self explanatory.
              :returns: The jiggered bar.

              The additional parameters are passed directly into
              :meth:`.get_content`. Note: the `url` parameter cannot be
              altered.

              {0}


              """.format(self.EMBED_TEXT)
        new_doc = _embed_text(doc, self.EMBED_TEXT)
        self.assertEqual(expected_doc, new_doc)
