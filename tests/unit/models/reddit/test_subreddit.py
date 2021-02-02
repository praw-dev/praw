import json
import pickle
from unittest import mock

import pytest

from praw.exceptions import MediaPostFailed
from praw.models import InlineGif, InlineImage, InlineVideo, Subreddit, WikiPage
from praw.models.reddit.subreddit import SubredditFlairTemplates

from ... import UnitTest


class TestSubreddit(UnitTest):
    def test_equality(self):
        subreddit1 = Subreddit(self.reddit, _data={"display_name": "dummy1", "n": 1})
        subreddit2 = Subreddit(self.reddit, _data={"display_name": "Dummy1", "n": 2})
        subreddit3 = Subreddit(self.reddit, _data={"display_name": "dummy3", "n": 2})
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

        with pytest.raises(ValueError):
            Subreddit(self.reddit, "")

    def test_fullname(self):
        subreddit = Subreddit(
            self.reddit, _data={"display_name": "name", "id": "dummy"}
        )
        assert subreddit.fullname == "t5_dummy"

    def test_hash(self):
        subreddit1 = Subreddit(self.reddit, _data={"display_name": "dummy1", "n": 1})
        subreddit2 = Subreddit(self.reddit, _data={"display_name": "Dummy1", "n": 2})
        subreddit3 = Subreddit(self.reddit, _data={"display_name": "dummy3", "n": 2})
        assert hash(subreddit1) == hash(subreddit1)
        assert hash(subreddit2) == hash(subreddit2)
        assert hash(subreddit3) == hash(subreddit3)
        assert hash(subreddit1) == hash(subreddit2)
        assert hash(subreddit2) != hash(subreddit3)
        assert hash(subreddit1) != hash(subreddit3)

    @mock.patch(
        "praw.Reddit.post", return_value={"json": {"data": {"websocket_url": ""}}}
    )
    @mock.patch(
        "praw.models.Subreddit._upload_media",
        return_value=("fake_media_url", "fake_websocket_url"),
    )
    @mock.patch("websocket.create_connection")
    def test_invalid_media(self, connection_mock, _mock_upload_media, _mock_post):
        connection_mock().recv.return_value = json.dumps(
            {"payload": {}, "type": "failed"}
        )
        with pytest.raises(MediaPostFailed):
            self.reddit.subreddit("test").submit_image("Test", "dummy path")

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

    def test_submit_gallery__missing_path(self):
        message = "'image_path' is required."
        subreddit = Subreddit(self.reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(
                "Cool title", images=[{"caption": "caption"}, {"caption": "caption2"}]
            )
        assert str(excinfo.value) == message

    def test_submit_gallery__invalid_path(self):
        message = "'invalid_image_path' is not a valid image path."
        subreddit = Subreddit(self.reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(
                "Cool title", images=[{"image_path": "invalid_image_path"}]
            )
        assert str(excinfo.value) == message

    def test_submit_gallery__too_long_caption(self):
        message = "Caption must be 180 characters or less."
        subreddit = Subreddit(self.reddit, display_name="name")
        caption = "wayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy too long caption"
        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(
                "Cool title", images=[{"image_path": __file__, "caption": caption}]
            )
        assert str(excinfo.value) == message

    def test_submit_inline_media__invalid_path(self):
        message = "'invalid_image_path' is not a valid file path."
        subreddit = Subreddit(self.reddit, display_name="name")
        gif = InlineGif("invalid_image_path", "optional caption")
        image = InlineImage("invalid_image_path", "optional caption")
        video = InlineVideo("invalid_image_path", "optional caption")
        selftext = "Text with {gif1}, {image1}, and {video1} inline"
        media = {"gif1": gif, "image1": image, "video1": video}
        with pytest.raises(ValueError) as excinfo:
            subreddit.submit("title", selftext=selftext, inline_media=media)
        assert str(excinfo.value) == message

    def test_upload_banner_additional_image(self):
        subreddit = Subreddit(self.reddit, display_name="name")
        with pytest.raises(ValueError):
            subreddit.stylesheet.upload_banner_additional_image(
                "dummy_path", align="asdf"
            )


class TestSubredditFlair(UnitTest):
    def test_set(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(TypeError):
            subreddit.flair.set(
                "a_redditor", css_class="myCSS", flair_template_id="gibberish"
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

    def test_conversation_stream_capitalization(self):
        submodstream = self.reddit.subreddit("Mod").mod.stream
        submodstream.modmail_conversations()
        assert submodstream.subreddit == "all"
