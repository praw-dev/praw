import pickle

import pytest
from praw.models import Subreddit, WikiPage
from praw.models.reddit.subreddit import SubredditFlairTemplates
from praw.models import AdvancedSubmissionFlair, RedditorFlair
from praw.models.flair_helper import FlairHelper

from ... import UnitTest


class TestSubreddit(UnitTest):
    def test_equality(self):
        subreddit1 = Subreddit(
            self.reddit, _data={"display_name": "dummy1", "n": 1}
        )
        subreddit2 = Subreddit(
            self.reddit, _data={"display_name": "Dummy1", "n": 2}
        )
        subreddit3 = Subreddit(
            self.reddit, _data={"display_name": "dummy3", "n": 2}
        )
        assert subreddit1 == subreddit1
        assert subreddit2 == subreddit2
        assert subreddit3 == subreddit3
        assert subreddit1 == subreddit2
        assert subreddit2 != subreddit3
        assert subreddit1 != subreddit3
        assert "dummy1" == subreddit1
        assert subreddit2 == "dummy1"

    def test_construct_failure(self):
        message = "Either `display_name` or `_data` must be provided."
        with pytest.raises(TypeError) as excinfo:
            Subreddit(self.reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Subreddit(self.reddit, "dummy", {"id": "dummy"})
        assert str(excinfo.value) == message

    def test_fullname(self):
        subreddit = Subreddit(
            self.reddit, _data={"display_name": "name", "id": "dummy"}
        )
        assert subreddit.fullname == "t5_dummy"

    def test_hash(self):
        subreddit1 = Subreddit(
            self.reddit, _data={"display_name": "dummy1", "n": 1}
        )
        subreddit2 = Subreddit(
            self.reddit, _data={"display_name": "Dummy1", "n": 2}
        )
        subreddit3 = Subreddit(
            self.reddit, _data={"display_name": "dummy3", "n": 2}
        )
        assert hash(subreddit1) == hash(subreddit1)
        assert hash(subreddit2) == hash(subreddit2)
        assert hash(subreddit3) == hash(subreddit3)
        assert hash(subreddit1) == hash(subreddit2)
        assert hash(subreddit2) != hash(subreddit3)
        assert hash(subreddit1) != hash(subreddit3)

    def test_pickle(self):
        subreddit = Subreddit(
            self.reddit, _data={"display_name": "name", "id": "dummy"}
        )
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(subreddit, protocol=level))
            assert subreddit == other

    def test_repr(self):
        subreddit = Subreddit(self.reddit, display_name="name")
        assert repr(subreddit) == "Subreddit(display_name='name')"

    def test_search__params_not_modified(self):
        params = {"dummy": "value"}
        subreddit = Subreddit(self.reddit, display_name="name")
        generator = subreddit.search(None, params=params)
        assert generator.params["dummy"] == "value"
        assert params == {"dummy": "value"}

    def test_str(self):
        subreddit = Subreddit(
            self.reddit, _data={"display_name": "name", "id": "dummy"}
        )
        assert str(subreddit) == "name"

    def test_submit_failure(self):
        message = "Either `selftext` or `url` must be provided."
        subreddit = Subreddit(self.reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit("Cool title")
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit("Cool title", selftext="a", url="b")
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit("Cool title", selftext="", url="b")
        assert str(excinfo.value) == message

    def test_upload_banner_additional_image(self):
        subreddit = Subreddit(self.reddit, display_name="name")
        with pytest.raises(ValueError):
            subreddit.stylesheet.upload_banner_additional_image(
                "dummy_path", align="asdf"
            )

    def test_submit_type_errors(self):
        subreddit = Subreddit(self.reddit, display_name="name")
        with pytest.raises(TypeError):
            subreddit.submit(
                "test",
                selftext="sdf",
                flair_id="test",
                flair=subreddit.flair.maker.make_link_flair("dummy"),
            )
        with pytest.raises(TypeError):
            subreddit.submit_image(
                "test",
                "test",
                flair_id="test",
                flair=subreddit.flair.maker.make_link_flair("dummy"),
            )
        with pytest.raises(TypeError):
            subreddit.submit_video(
                "test",
                "test",
                flair_id="test",
                flair=subreddit.flair.maker.make_link_flair("dummy"),
            )


class TestSubredditFlair(UnitTest):
    def test_set(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(TypeError):
            subreddit.flair.set(
                "a_redditor", css_class="myCSS", flair_template_id="gibberish"
            )

    def test_maker(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        assert isinstance(subreddit.flair.maker, FlairHelper)

    def test_flair_gen(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        lf = subreddit.flair.maker.make_link_flair("Test")
        assert isinstance(lf, AdvancedSubmissionFlair)
        uf = subreddit.flair.maker.make_user_flair("Test")
        assert isinstance(uf, RedditorFlair)

    def test_delete_error(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(TypeError):
            subreddit.flair.templates.delete(
                template_id="sf",
                flair=subreddit.flair.maker.make_user_flair("Dummy"),
            )


class TestSubredditFlairTemplates(UnitTest):
    def test_not_implemented(self):
        with pytest.raises(NotImplementedError):
            SubredditFlairTemplates(
                Subreddit(self.reddit, pytest.placeholders.test_subreddit)
            ).__iter__()


class TestSubredditWiki(UnitTest):
    def test__getitem(self):
        subreddit = Subreddit(self.reddit, display_name="name")
        wikipage = subreddit.wiki["Foo"]
        assert isinstance(wikipage, WikiPage)
        assert "foo" == wikipage.name


class TestSubredditModmailConversationsStream(UnitTest):
    def test_conversation_stream_init(self):
        submodstream = self.reddit.subreddit("mod").mod.stream
        submodstream.modmail_conversations()
        assert submodstream.subreddit == "all"

    def test_conversation_stream_capilization(self):
        submodstream = self.reddit.subreddit("Mod").mod.stream
        submodstream.modmail_conversations()
        assert submodstream.subreddit == "all"
