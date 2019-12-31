from praw.models import (
    LinkFlair,
    AdvancedSubmissionFlair,
    RedditorFlair,
)

from ... import UnitTest


class TestFlair(UnitTest):
    def test_attrs(self):
        example = {
            "flair_css_class": "Test",
            "flair_template_id": "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
            "flair_text_editable": True,
            "flair_position": "right",
            "flair_text": "Test",
        }
        example_submission = self.reddit.submission("dummy")
        example_flair = LinkFlair(self.reddit, example_submission, example)
        assert example_flair.flair_css_class == "Test"
        assert (
            example_flair.flair_template_id
            == "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d"
        )
        assert example_flair.flair_text_editable
        assert example_flair.flair_position == "right"
        assert example_flair.flair_text == "Test"

    def test_change(self):
        example = {
            "flair_css_class": "Test",
            "flair_template_id": "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
            "flair_text_editable": True,
            "flair_position": "right",
            "flair_text": "Test",
        }
        example_submission = self.reddit.submission("dummy")
        example_flair = LinkFlair(self.reddit, example_submission, example)
        assert example_flair.flair_text == "Test"
        example_flair.change_info(text="Testing")
        assert example_flair.flair_text == "Testing"

    def test_equality(self):
        example = {
            "flair_css_class": "Test",
            "flair_template_id": "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
            "flair_text_editable": True,
            "flair_position": "right",
            "flair_text": "Test",
        }
        example_submission = self.reddit.submission("dummy")
        example_flair = LinkFlair(self.reddit, example_submission, example)
        example_flair_2 = LinkFlair(self.reddit, example_submission, example)
        assert example_flair == example_flair_2
        assert hash(example_flair) == hash(example_flair_2)
        example_flair.change_info(text="Testt")
        assert example_flair != example_flair_2
        assert hash(example_flair) != hash(example_flair_2)

    def test_str(self):
        example = {
            "flair_css_class": "Test",
            "flair_template_id": "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
            "flair_text_editable": True,
            "flair_position": "right",
            "flair_text": "Test",
        }
        example_submission = self.reddit.submission("dummy")
        example_flair = LinkFlair(self.reddit, example_submission, example)
        assert example_flair == "Test"


class TestFlairMod(UnitTest):
    def test_attrs(self):
        example = {
            "type": "text",
            "text_editable": False,
            "allowable_content": "all",
            "text": "Test",
            "max_emojis": 10,
            "text_color": "dark",
            "mod_only": False,
            "css_class": "Test",
            "richtext": [],
            "background_color": "",
            "id": "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
        }
        example_subreddit = self.reddit.subreddit(
            "dummy", use_flair_class=True
        )
        example_flair = AdvancedSubmissionFlair(
            self.reddit, example_subreddit, example
        )
        assert example_flair.type == "text"
        assert not example_flair.text_editable
        assert example_flair.allowable_content == "all"
        assert example_flair.text == "Test"
        assert example_flair.max_emojis == 10
        assert example_flair.text_color == "dark"
        assert not example_flair.mod_only
        assert example_flair.css_class == "Test"
        assert example_flair.richtext == []
        assert len(example_flair.richtext) == 0
        assert example_flair.background_color == ""
        assert len(example_flair.background_color) == 0
        assert example_flair.id == "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d"

    def test_changes(self):
        example = {
            "type": "text",
            "text_editable": False,
            "allowable_content": "all",
            "text": "Test",
            "max_emojis": 10,
            "text_color": "dark",
            "mod_only": False,
            "css_class": "Test",
            "richtext": [],
            "background_color": "",
            "id": "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
        }
        example_subreddit = self.reddit.subreddit(
            "dummy", use_flair_class=True
        )
        example_flair = AdvancedSubmissionFlair(
            self.reddit, example_subreddit, example
        )
        assert example_flair.text == "Test"
        example_flair.change_info(text="Testing")
        assert example_flair.text == "Testing"
        assert example_flair.css_class == "Test"
        example_flair.change_info(css_class="Testing")
        assert example_flair.css_class == "Testing"

    def test_equality(self):
        example = {
            "type": "text",
            "text_editable": False,
            "allowable_content": "all",
            "text": "Test",
            "max_emojis": 10,
            "text_color": "dark",
            "mod_only": False,
            "css_class": "Test",
            "richtext": [],
            "background_color": "",
            "id": "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
        }
        example_subreddit = self.reddit.subreddit(
            "dummy", use_flair_class=True
        )
        example_flair = AdvancedSubmissionFlair(
            self.reddit, example_subreddit, example
        )
        example_flair_2 = AdvancedSubmissionFlair(
            self.reddit, example_subreddit, example
        )
        example_flair_3 = AdvancedSubmissionFlair(
            self.reddit, example_subreddit, example
        )
        assert example_flair == example_flair_2 == example_flair_3
        assert (
            hash(example_flair)
            == hash(example_flair_2)
            == hash(example_flair_3)
        )
        example_flair.change_info(text="T")
        assert (
            example_flair != example_flair_2
            and example_flair != example_flair_3
        )
        assert hash(example_flair) != hash(example_flair_2) and hash(
            example_flair
        ) != hash(example_flair_3)
        assert example_flair_2 == example_flair_3
        assert hash(example_flair_2) == hash(example_flair_3)
        example_flair_2.change_info(css_class="DSF")
        assert example_flair != example_flair_2
        assert example_flair_2 != example_flair_3
        assert hash(example_flair) != hash(example_flair_2)
        assert hash(example_flair_2) != hash(example_flair_3)

    def test_str(self):
        example = {
            "type": "text",
            "text_editable": False,
            "allowable_content": "all",
            "text": "Test",
            "max_emojis": 10,
            "text_color": "dark",
            "mod_only": False,
            "css_class": "Test",
            "richtext": [],
            "background_color": "",
            "id": "0f7349d8-2a6d-11ea-8529-0e5dee3e1a9d",
        }
        example_subreddit = self.reddit.subreddit(
            "dummy", use_flair_class=True
        )
        example_flair = AdvancedSubmissionFlair(
            self.reddit, example_subreddit, example
        )
        assert example_flair == "Test"


class TestRedditorFlair(UnitTest):
    def test_attrs(self):
        example = {
            "allowable_content": "all",
            "text": "Test",
            "text_color": "light",
            "mod_only": False,
            "background_color": "#cc8b00",
            "id": "0be1ace4-2a75-11ea-8018-0ecef10bc461",
            "css_class": "Test",
            "max_emojis": 10,
            "richtext": [],
            "text_editable": True,
            "override_css": False,
            "type": "text",
        }
        example_subreddit = self.reddit.subreddit(
            "dummy", use_flair_class=True
        )
        example_flair = RedditorFlair(self.reddit, example_subreddit, example)
        assert example_flair.type == "text"
        assert example_flair.text_editable
        assert example_flair.allowable_content == "all"
        assert example_flair.text == "Test"
        assert example_flair.max_emojis == 10
        assert example_flair.text_color == "light"
        assert not example_flair.mod_only
        assert example_flair.css_class == "Test"
        assert example_flair.richtext == []
        assert len(example_flair.richtext) == 0
        assert example_flair.background_color == "#cc8b00"
        assert len(example_flair.background_color) > 0
        assert example_flair.id == "0be1ace4-2a75-11ea-8018-0ecef10bc461"

    def test_changes(self):
        example = {
            "allowable_content": "all",
            "text": "Test",
            "text_color": "light",
            "mod_only": False,
            "background_color": "#cc8b00",
            "id": "0be1ace4-2a75-11ea-8018-0ecef10bc461",
            "css_class": "Text",
            "max_emojis": 10,
            "richtext": [],
            "text_editable": True,
            "override_css": False,
            "type": "text",
        }

        example_subreddit = self.reddit.subreddit(
            "dummy", use_flair_class=True
        )
        example_flair = RedditorFlair(self.reddit, example_subreddit, example)
        assert example_flair.text == "Test"
        example_flair.change_info(text="Testing")
        assert example_flair.text == "Testing"
        assert example_flair.css_class == "Text"
        example_flair.change_info(css_class="Testing")
        assert example_flair.css_class == "Testing"

    def test_equality(self):
        example = {
            "allowable_content": "all",
            "text": "Test",
            "text_color": "light",
            "mod_only": False,
            "background_color": "#cc8b00",
            "id": "0be1ace4-2a75-11ea-8018-0ecef10bc461",
            "css_class": "Test",
            "max_emojis": 10,
            "richtext": [],
            "text_editable": True,
            "override_css": False,
            "type": "text",
        }
        example_subreddit = self.reddit.subreddit(
            "dummy", use_flair_class=True
        )
        example_flair = RedditorFlair(self.reddit, example_subreddit, example)
        example_flair_2 = RedditorFlair(
            self.reddit, example_subreddit, example
        )
        example_flair_3 = RedditorFlair(
            self.reddit, example_subreddit, example
        )
        assert example_flair == example_flair_2 == example_flair_3
        assert (
            hash(example_flair)
            == hash(example_flair_2)
            == hash(example_flair_3)
        )
        example_flair.change_info(text="T")
        assert (
            example_flair != example_flair_2
            and example_flair != example_flair_3
        )
        assert hash(example_flair) != hash(example_flair_2) and hash(
            example_flair
        ) != hash(example_flair_3)
        assert example_flair_2 == example_flair_3
        assert hash(example_flair_2) == hash(example_flair_3)
        example_flair_2.change_info(css_class="DSF")
        assert example_flair != example_flair_2
        assert example_flair_2 != example_flair_3
        assert hash(example_flair) != hash(example_flair_2)
        assert hash(example_flair_2) != hash(example_flair_3)

    def test_str(self):
        example = {
            "allowable_content": "all",
            "text": "Test",
            "text_color": "light",
            "mod_only": False,
            "background_color": "#cc8b00",
            "id": "0be1ace4-2a75-11ea-8018-0ecef10bc461",
            "css_class": "Test",
            "max_emojis": 10,
            "richtext": [],
            "text_editable": True,
            "override_css": False,
            "type": "text",
        }
        example_subreddit = self.reddit.subreddit(
            "dummy", use_flair_class=True
        )
        example_flair = RedditorFlair(self.reddit, example_subreddit, example)
        assert example_flair == "Test"
