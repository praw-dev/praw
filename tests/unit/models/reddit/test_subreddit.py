import json
import pickle
from unittest import mock

import pytest

from praw.exceptions import ClientException, MediaPostFailed
from praw.models import InlineGif, InlineImage, InlineVideo, PostMedia, StylesheetAsset, Subreddit, WikiPage
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
        assert subreddit1 == "dummy1"
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
        "praw.models.PostMedia._upload",
        return_value="fake_media_url",
    )
    @mock.patch(
        "praw.Reddit.post", return_value={"json": {"data": {"websocket_url": ""}}}
    )
    def test_invalid_media(
        self, _mock_post, _mock_upload, connection_mock, reddit
    ):
        connection_mock().recv.return_value = json.dumps(
            {"payload": {}, "type": "failed"}
        )
        with pytest.raises(MediaPostFailed):
            reddit.subreddit("test").submit_image(image_media=PostMedia(b"", name="dummy.png"), title="Test")

    @mock.patch("praw.models.PostMedia._post_to_s3")
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

        response = mock.Mock()
        response.ok = False
        response.status_code = 500
        response.text = "<Error/>"
        mock_method.return_value = response
        with pytest.raises(ServerError):
            reddit.subreddit("test").submit_image(image_media=PostMedia(b"", name="test.png"), title="Test")

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

    def test_submit__failure(self, reddit):
        message = "Either 'selftext' and/or 'url' must be provided."
        subreddit = Subreddit(reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit("Cool title")
        assert str(excinfo.value) == message

    def test_submit__url_selftext_inline_media_disallowed(self, reddit):
        # `selftext` and `url` are no longer mutually exclusive,
        # but `inline_media` is not supported for link post selftext
        message = "As of 2025-05-07, `inline_media` is not supported for link post selftext. Only Markdown text can be added to non-self posts."
        subreddit = Subreddit(reddit, display_name="name")
        gif = InlineGif(caption="optional caption", media=PostMedia(b"", name="test.gif"))
        image = InlineImage(caption="optional caption", media=PostMedia(b"", name="test.png"))
        video = InlineVideo(caption="optional caption", media=PostMedia(b"", name="test.mp4"))
        selftext = "Text with {gif1}, {image1}, and {video1} inline"
        media = {"gif1": gif, "image1": image, "video1": video}
        with pytest.raises(TypeError) as excinfo:
            subreddit.submit("Cool title",
                             url="https://praw.readthedocs.org/en/stable/",
                             inline_media=media,
                             selftext=selftext)
        assert str(excinfo.value) == message

    def test_submit_gallery__invalid_image_media(self, reddit):
        message = "'image_media' is required and must be a PostMedia instance."
        subreddit = Subreddit(reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(images=[{"image_media": "a string is not PostMedia"}], title="Cool title")
        assert str(excinfo.value) == message

    def test_submit_gallery__missing_image_media(self, reddit):
        message = "'image_media' is required and must be a PostMedia instance."
        subreddit = Subreddit(reddit, display_name="name")

        with pytest.raises(TypeError) as excinfo:
            subreddit.submit_gallery(images=[{"caption": "caption"}, {"caption": "caption2"}], title="Cool title")
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
                images=[{"image_media": PostMedia(b"", name="test.png"), "caption": caption}],
                title="Cool title",
            )
        assert str(excinfo.value) == message

    def test_submit_image__bad_filetype(self, image_path, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for file_name in ("test.mov", "test.mp4"):
            image = PostMedia(image_path(file_name))
            with pytest.raises(ClientException):
                subreddit.submit_image(image_media=image, title="Test Title")

    def test_submit_inline_media__invalid_media(self, reddit):
        message = "'media' must be a PostMedia instance."
        subreddit = Subreddit(reddit, display_name="name")
        gif = InlineGif(caption="optional caption", media="not_post_media")
        image = InlineImage(caption="optional caption", media="not_post_media")
        video = InlineVideo(caption="optional caption", media="not_post_media")
        selftext = "Text with {gif1}, {image1}, and {video1} inline"
        media = {"gif1": gif, "image1": image, "video1": video}
        with pytest.raises(TypeError) as excinfo:
            subreddit.submit("title", inline_media=media, selftext=selftext)
        assert str(excinfo.value) == message

    def test_submit_video__bad_filetype(self, image_path, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for file_name in ("test.jpg", "test.png", "test.gif"):
            video = PostMedia(image_path(file_name))
            with pytest.raises(ClientException):
                subreddit.submit_video(title="Test Title", video_media=video)

    def test_upload_banner_additional_image(self, reddit):
        subreddit = Subreddit(reddit, display_name="name")
        with pytest.raises(ValueError):
            subreddit.stylesheet.upload_banner_additional_image(
                StylesheetAsset(b"", name="dummy.png"), align="asdf"
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
        assert wikipage.name == "foo"
