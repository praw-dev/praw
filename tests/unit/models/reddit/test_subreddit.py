import json
import pickle
from unittest import mock

import pytest

from praw.exceptions import ClientException, MediaPostFailed
from praw.models import InlineGif, InlineImage, InlineVideo, Subreddit, WikiPage
from praw.models.reddit.subreddit import SubredditFlairTemplates

from ... import UnitTest


class TestSubreddit(UnitTest):
    def test_construct_failure(self, reddit):
        message = "Either 'display_name' or '_data' must be provided."
        with pytest.raises(TypeError) as excinfo:
            Subreddit(reddit)
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            Subreddit(reddit, "dummy", {"id": "dummy"})
        assert str(excinfo.value) == message

        with pytest.raises(ValueError):
            Subreddit(reddit, "")

    def test_equality(self, reddit):
        subreddit1 = Subreddit(reddit, _data={"display_name": "dummy1", "n": 1})
        subreddit2 = Subreddit(reddit, _data={"display_name": "Dummy1", "n": 2})
        subreddit3 = Subreddit(reddit, _data={"display_name": "dummy3", "n": 2})
        assert subreddit1 == subreddit1
        assert subreddit2 == subreddit2
        assert subreddit3 == subreddit3
        assert subreddit1 == subreddit2
        assert subreddit2 != subreddit3
        assert subreddit1 != subreddit3
        assert "dummy1" == subreddit1
        assert subreddit2 == "dummy1"

    def test_fullname(self, reddit):
        subreddit = Subreddit(reddit, _data={"display_name": "name", "id": "dummy"})
        assert subreddit.fullname == "t5_dummy"

    def test_hash(self, reddit):
        subreddit1 = Subreddit(reddit, _data={"display_name": "dummy1", "n": 1})
        subreddit2 = Subreddit(reddit, _data={"display_name": "Dummy1", "n": 2})
        subreddit3 = Subreddit(reddit, _data={"display_name": "dummy3", "n": 2})
        assert hash(subreddit1) == hash(subreddit1)
        assert hash(subreddit2) == hash(subreddit2)
        assert hash(subreddit3) == hash(subreddit3)
        assert hash(subreddit1) == hash(subreddit2)
        assert hash(subreddit2) != hash(subreddit3)
        assert hash(subreddit1) != hash(subreddit3)

    @mock.patch("websocket.create_connection")
    @mock.patch(
        "praw.models.Subreddit._upload_media",
        return_value=("fake_media_url", "fake_websocket_url"),
    )
    @mock.patch(
        "praw.Reddit.post", return_value={"json": {"data": {"websocket_url": ""}}}
    )
    def test_invalid_media(
        self, _mock_post, _mock_upload_media, connection_mock, reddit
    ):
        connection_mock().recv.return_value = json.dumps(
            {"payload": {}, "type": "failed"}
        )
        with pytest.raises(MediaPostFailed):
            reddit.subreddit("test").submit_image("Test", "dummy path")

    @mock.patch("praw.models.Subreddit._read_and_post_media")
    @mock.patch("websocket.create_connection")
    @mock.patch(
        "praw.Reddit.post",
        return_value={
            "json": {"data": {"websocket_url": ""}},
            "args": {"action": "", "fields": []},
        },
    )
    def test_media_upload_500(self, _mock_post, connection_mock, mock_method, reddit):
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
            reddit.subreddit("test").submit_image("Test", "/dev/null")

    def test_notes_delete__invalid_args(self, reddit):
        with pytest.raises(TypeError) as excinfo:
            reddit.subreddit("SubTestBot1").mod.notes.delete(note_id="111")
        assert excinfo.value.args[0] == (
            "Either the 'redditor' parameter must be provided or this method must be"
            " called from a Redditor instance (e.g., 'redditor.notes')."
        )

    def test_pickle(self, reddit):
        subreddit = Subreddit(reddit, _data={"display_name": "name", "id": "dummy"})
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(subreddit, protocol=level))
            assert subreddit == other

    def test_repr(self, reddit):
        subreddit = Subreddit(reddit, display_name="name")
        assert repr(subreddit) == "Subreddit(display_name='name')"

    def test_search__params_not_modified(self, reddit):
        params = {"dummy": "value"}
        subreddit = Subreddit(reddit, display_name="name")
        generator = subreddit.search(None, params=params)
        assert generator.params["dummy"] == "value"
        assert params == {"dummy": "value"}

    def test_str(self, reddit):
        subreddit = Subreddit(reddit, _data={"display_name": "name", "id": "dummy"})
        assert str(subreddit) == "name"

    def test_submit_failure(self, reddit):
        message = "Either 'selftext' or 'url' must be provided."
        subreddit = Subreddit(reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit("Cool title")
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit("Cool title", selftext="a", url="b")
        assert str(excinfo.value) == message

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit("Cool title", selftext="", url="b")
        assert str(excinfo.value) == message

    def test_submit_gallery__invalid_path(self, reddit):
        message = "'invalid_image_path' is not a valid image path."
        subreddit = Subreddit(reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(
                "Cool title", [{"image_path": "invalid_image_path"}]
            )
        assert str(excinfo.value) == message

    def test_submit_gallery__missing_path(self, reddit):
        message = "'image_path' is required."
        subreddit = Subreddit(reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(
                "Cool title", [{"caption": "caption"}, {"caption": "caption2"}]
            )
        assert str(excinfo.value) == message

    def test_submit_gallery__too_long_caption(self, reddit):
        message = "Caption must be 180 characters or less."
        subreddit = Subreddit(reddit, display_name="name")
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

    def test_submit_image__bad_filetype(self, image_path, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for file_name in ("test.mov", "test.mp4"):
            image = image_path(file_name)
            with pytest.raises(ClientException):
                subreddit.submit_image("Test Title", image)

    def test_submit_inline_media__invalid_path(self, reddit):
        message = "'invalid_image_path' is not a valid file path."
        subreddit = Subreddit(reddit, display_name="name")
        gif = InlineGif("invalid_image_path", "optional caption")
        image = InlineImage("invalid_image_path", "optional caption")
        video = InlineVideo("invalid_image_path", "optional caption")
        selftext = "Text with {gif1}, {image1}, and {video1} inline"
        media = {"gif1": gif, "image1": image, "video1": video}
        with pytest.raises(ValueError) as excinfo:
            subreddit.submit("title", inline_media=media, selftext=selftext)
        assert str(excinfo.value) == message

    def test_submit_video__bad_filetype(self, image_path, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for file_name in ("test.jpg", "test.png", "test.gif"):
            video = image_path(file_name)
            with pytest.raises(ClientException):
                subreddit.submit_video("Test Title", video)

    def test_upload_banner_additional_image(self, reddit):
        subreddit = Subreddit(reddit, display_name="name")
        with pytest.raises(ValueError):
            subreddit.stylesheet.upload_banner_additional_image(
                "dummy_path", align="asdf"
            )


class TestSubredditFlair(UnitTest):
    def test_set(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(TypeError):
            subreddit.flair.set(
                "a_redditor", css_class="myCSS", flair_template_id="gibberish"
            )


class TestSubredditFlairTemplates(UnitTest):
    def test_not_implemented(self, reddit):
        with pytest.raises(NotImplementedError):
            SubredditFlairTemplates(
                Subreddit(reddit, pytest.placeholders.test_subreddit)
            ).__iter__()


class TestSubredditModmailConversationsStream(UnitTest):
    def test_conversation_stream_capitalization(self, reddit):
        submodstream = reddit.subreddit("Mod").mod.stream
        submodstream.modmail_conversations()
        assert submodstream.subreddit == "all"

    def test_conversation_stream_init(self, reddit):
        submodstream = reddit.subreddit("mod").mod.stream
        submodstream.modmail_conversations()
        assert submodstream.subreddit == "all"


class TestSubredditWiki(UnitTest):
    def test__getitem(self, reddit):
        subreddit = Subreddit(reddit, display_name="name")
        wikipage = subreddit.wiki["Foo"]
        assert isinstance(wikipage, WikiPage)
        assert "foo" == wikipage.name
