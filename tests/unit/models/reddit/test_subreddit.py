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

    @mock.patch("praw.models.Subreddit._read_and_post_media")
    @mock.patch(
        "praw.Reddit.post",
        return_value={
            "json": {"data": {"websocket_url": ""}},
            "args": {"action": "", "fields": []},
        },
    )
    @mock.patch("websocket.create_connection")
    def test_media_upload_500(self, connection_mock, _mock_post, mock_method):
        from prawcore.exceptions import ServerError
        from requests.exceptions import HTTPError

        http_response = mock.Mock()
        http_response.status_code = 500

        response = mock.Mock()
        response.ok = True
        response.raise_for_status = mock.Mock(
            side_effect=HTTPError(response=http_response)
        )
        mock_method.return_value = response
        with pytest.raises(ServerError):
            self.reddit.subreddit("test").submit_image("Test", "/dev/null")

    def test_notes_delete__invalid_args(self):
        with pytest.raises(TypeError) as excinfo:
            self.reddit.subreddit("SubTestBot1").mod.notes.delete(note_id="111")
        assert excinfo.value.args[0] == (
            "Either the `redditor` parameter must be provided or this method must be"
            " called from a Redditor instance (e.g., `redditor.notes`)."
        )

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

    def test_submit_image__invalid_image_fp(self):
        message = "media_fp is not of type bytes."
        subreddit = Subreddit(self.reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_image("Cool title", image_fp="invalid_image")
        assert str(excinfo.value) == message

    def test_submit_gallery__missing_image_path_and_image_fp(self):
        message = "Values for keys image_path and image_fp are null for dictionary at index 0."
        subreddit = Subreddit(self.reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(
                "Cool title", [{"caption": "caption"}, {"caption": "caption2"}]
            )
        assert str(excinfo.value) == message

    def test_submit_gallery__invalid_image_path(self):
        message = "invalid_image is not a valid file path."
        subreddit = Subreddit(self.reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery("Cool title", [{"image_path": "invalid_image"}])
        assert str(excinfo.value) == message

    def test_submit_gallery__invalid_image_fp(self):
        subreddit = Subreddit(self.reddit, display_name="name")

        message = (
            "'image_fp' dictionary value at index 0 contains an invalid bytes object."
        )
        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(
                "Cool title", [{"image_fp": "invalid_image", "mime_type": "image/png"}]
            )
        assert str(excinfo.value) == message

    def test_submit_gallery__too_long_caption(self):
        message = "Caption must be 180 characters or less."
        subreddit = Subreddit(self.reddit, display_name="name")
        caption = (
            "wayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
            "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
            "yyyyyyyyyyyyyyyy too long caption"
        )
        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(
                "Cool title", [{"image_path": __file__, "caption": caption}]
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
            subreddit.submit("title", inline_media=media, selftext=selftext)
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
