"""Test praw.models.subreddit."""
import socket
import sys
from json import dumps
from os.path import abspath, dirname, join
from unittest import mock

import pytest
import requests
import websocket
from prawcore import BadRequest, Forbidden, NotFound, RequestException, TooLarge

from praw.const import PNG_HEADER
from praw.exceptions import (
    ClientException,
    InvalidFlairTemplateID,
    RedditAPIException,
    TooLargeMediaException,
    WebSocketException,
)
from praw.models import (
    Comment,
    InlineGif,
    InlineImage,
    InlineVideo,
    ListingGenerator,
    ModAction,
    ModmailAction,
    ModmailConversation,
    ModmailMessage,
    Redditor,
    Stylesheet,
    Submission,
    Subreddit,
    SubredditMessage,
    WikiPage,
)

from ... import IntegrationTest


class WebsocketMock:
    POST_URL = "https://reddit.com/r/<TEST_SUBREDDIT>/comments/{}/test_title/"

    @classmethod
    def make_dict(cls, post_id):
        return {"payload": {"redirect": cls.POST_URL.format(post_id)}}

    def __init__(self, *post_ids):
        self.post_ids = post_ids
        self.i = -1

    def close(self, *args, **kwargs):
        pass

    def recv(self):
        if not self.post_ids:
            raise websocket.WebSocketTimeoutException()
        assert 0 <= self.i + 1 < len(self.post_ids)
        self.i += 1
        return dumps(self.make_dict(self.post_ids[self.i]))


class WebsocketMockException:
    def __init__(self, recv_exc=None, close_exc=None):
        """Initialize a WebsocketMockException.

        :param recv_exc: An exception to be raised during a call to recv().
        :param close_exc: An exception to be raised during close().

        The purpose of this class is to mock a WebSockets connection that is
        faulty or times out, to see how PRAW handles it.
        """
        self._recv_exc = recv_exc
        self._close_exc = close_exc

    def close(self, *args, **kwargs):
        if self._close_exc is not None:
            raise self._close_exc

    def recv(self):
        if self._recv_exc is not None:
            raise self._recv_exc
        else:
            return dumps(
                {
                    "payload": {
                        "redirect": "https://reddit.com/r/<TEST_SUBREDDIT>/comments/abcdef/test_title/"
                    }
                }
            )


class TestSubreddit(IntegrationTest):
    @staticmethod
    def image_path(name):
        test_dir = abspath(dirname(sys.modules[__name__].__file__))
        return join(test_dir, "..", "..", "files", name)

    @mock.patch("time.sleep", return_value=None)
    def test_create(self, _):
        self.reddit.read_only = False
        new_name = "PRAW_rrldkyrfln"
        with self.use_cassette():
            subreddit = self.reddit.subreddit.create(
                name=new_name,
                title="Sub",
                link_type="any",
                subreddit_type="public",
                wikimode="disabled",
            )
            assert subreddit.display_name == new_name
            assert subreddit.submission_type == "any"

    def test_create__exists(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                self.reddit.subreddit.create(
                    "redditdev",
                    title="redditdev",
                    link_type="any",
                    subreddit_type="public",
                    wikimode="disabled",
                )
            assert excinfo.value.items[0].error_type == "SUBREDDIT_EXISTS"

    def test_create__invalid_parameter(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                # Supplying invalid setting for link_type
                self.reddit.subreddit.create(
                    name="PRAW_iavynavffv",
                    title="sub",
                    link_type="abcd",
                    subreddit_type="public",
                    wikimode="disabled",
                )
            assert excinfo.value.items[0].error_type == "INVALID_OPTION"

    def test_create__missing_parameter(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                # Not supplying required field title.
                self.reddit.subreddit.create(
                    name="PRAW_iavynavffv",
                    title=None,
                    link_type="any",
                    subreddit_type="public",
                    wikimode="disabled",
                )
            assert excinfo.value.items[0].error_type == "NO_TEXT"

    @mock.patch("time.sleep", return_value=None)
    def test_message(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            subreddit.message("Test from PRAW", message="Test content")

    @mock.patch("time.sleep", return_value=None)
    def test_post_requirements(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            data = subreddit.post_requirements()
            tags = [
                "domain_blacklist",
                "body_restriction_policy",
                "domain_whitelist",
                "title_regexes",
                "body_blacklisted_strings",
                "body_required_strings",
                "title_text_min_length",
                "is_flair_required",
                "title_text_max_length",
                "body_regexes",
                "link_repost_age",
                "body_text_min_length",
                "link_restriction_policy",
                "body_text_max_length",
                "title_required_strings",
                "title_blacklisted_strings",
                "guidelines_text",
                "guidelines_display_policy",
            ]
            assert list(data) == tags

    def test_random(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submissions = [
                subreddit.random(),
                subreddit.random(),
                subreddit.random(),
                subreddit.random(),
            ]
        assert len(submissions) == len(set(submissions))

    def test_random__returns_none(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("wallpapers")
            assert subreddit.random() is None

    def test_sticky(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            submission = subreddit.sticky()
            assert isinstance(submission, Submission)

    def test_sticky__not_set(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            with pytest.raises(NotFound):
                subreddit.sticky(2)

    def test_search(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("all")
            for item in subreddit.search(
                "praw oauth search", limit=None, syntax="cloudsearch"
            ):
                assert isinstance(item, Submission)

    @mock.patch("time.sleep", return_value=None)
    def test_submit__flair(self, _):
        flair_id = "17bf09c4-520c-11e7-8073-0ef8adb5ef68"
        flair_text = "Test flair text"
        flair_class = "test-flair-class"
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission = subreddit.submit(
                "Test Title",
                selftext="Test text.",
                flair_id=flair_id,
                flair_text=flair_text,
            )
            assert submission.link_flair_css_class == flair_class
            assert submission.link_flair_text == flair_text

    @mock.patch("time.sleep", return_value=None)
    def test_submit__selftext(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission = subreddit.submit("Test Title", selftext="Test text.")
            assert submission.author == self.reddit.config.username
            assert submission.selftext == "Test text."
            assert submission.title == "Test Title"

    @mock.patch("time.sleep", return_value=None)
    def test_submit__selftext_blank(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission = subreddit.submit("Test Title", selftext="")
            assert submission.author == self.reddit.config.username
            assert submission.selftext == ""
            assert submission.title == "Test Title"

    @mock.patch("time.sleep", return_value=None)
    def test_submit__selftext_inline_media(self, _):
        self.reddit.read_only = False
        with self.recorder.use_cassette(
            "TestSubreddit.test_submit__selftext_inline_media"
        ):
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            gif = InlineGif(self.image_path("test.gif"), "optional caption")
            image = InlineImage(self.image_path("test.png"), "optional caption")
            video = InlineVideo(self.image_path("test.mp4"), "optional caption")
            selftext = (
                "Text with a gif {gif1} an image {image1} and a video {video1} inline"
            )
            media = {"gif1": gif, "image1": image, "video1": video}
            submission = subreddit.submit(
                "title", selftext=selftext, inline_media=media
            )
            assert submission.author == pytest.placeholders.username
            assert (
                submission.selftext
                == "Text with a gif\n\n[optional caption](https://i.redd.it/3vwgfvq3tyq51.gif)\n\nan image\n\n[optional caption](https://preview.redd.it/9147est3tyq51.png?width=128&format=png&auto=webp&s=54d1a865a9339dcca9ec19eb1e357079c81e5100)\n\nand a video\n\n[optional caption](https://reddit.com/link/j4p2rk/video/vsie20v3tyq51/player)\n\ninline"
            )
            assert submission.title == "title"

    @mock.patch("time.sleep", return_value=None)
    def test_submit_live_chat(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission = subreddit.submit(
                "Test Title", selftext="", discussion_type="CHAT"
            )
            assert submission.discussion_type == "CHAT"

    @mock.patch("time.sleep", return_value=None)
    def test_submit__url(self, _):
        url = "https://praw.readthedocs.org/en/stable/"
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission = subreddit.submit("Test Title", url=url)
            assert submission.author == self.reddit.config.username
            assert submission.url == url
            assert submission.title == "Test Title"

    @mock.patch("time.sleep", return_value=None)
    def test_submit__nsfw(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            submission = subreddit.submit(
                "Test Title", selftext="Test text.", nsfw=True
            )
            assert submission.over_18 is True

    @mock.patch("time.sleep", return_value=None)
    def test_submit__spoiler(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.subreddit = self.reddit.subreddit(
                pytest.placeholders.test_subreddit
            )
            submission = subreddit.submit(
                "Test Title", selftext="Test text.", spoiler=True
            )
            assert submission.spoiler is True

    @mock.patch("time.sleep", return_value=None)
    def test_submit__verify_invalid(self, _):
        self.reddit.read_only = False
        self.reddit.validate_on_submit = True
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            with pytest.raises(
                (RedditAPIException, BadRequest)
            ):  # waiting for prawcore fix
                subreddit.submit("dfgfdgfdgdf", url="https://www.google.com")

    @mock.patch("time.sleep", return_value=None)
    def test_submit_poll(self, _):
        options = ["Yes", "No", "3", "4", "5", "6"]
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission = subreddit.submit_poll(
                "Test Poll",
                selftext="Test poll text.",
                options=options,
                duration=6,
            )
            assert submission.author == self.reddit.config.username
            assert submission.selftext.startswith("Test poll text.")
            assert submission.title == "Test Poll"
            assert [str(option) for option in submission.poll_data.options] == options
            assert submission.poll_data.voting_end_timestamp > submission.created_utc

    @mock.patch("time.sleep", return_value=None)
    def test_submit_poll__flair(self, _):
        flair_id = "9ac711a4-1ddf-11e9-aaaa-0e22784c70ce"
        flair_text = "Test flair text"
        flair_class = ""
        options = ["Yes", "No"]
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission = subreddit.submit_poll(
                "Test Poll",
                selftext="Test poll text.",
                flair_id=flair_id,
                flair_text=flair_text,
                options=options,
                duration=6,
            )
            assert submission.link_flair_text == flair_text
            assert submission.link_flair_css_class == flair_class

    @mock.patch("time.sleep", return_value=None)
    def test_submit_poll__live_chat(self, _):
        options = ["Yes", "No"]
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            submission = subreddit.submit_poll(
                "Test Poll",
                selftext="",
                discussion_type="CHAT",
                options=options,
                duration=2,
            )
            assert submission.discussion_type == "CHAT"

    def test_submit_gallery(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubreddit.test_submit_gallery"):
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            images = [
                {"image_path": self.image_path("test.png")},
                {"image_path": self.image_path("test.jpg"), "caption": "test.jpg"},
                {
                    "image_path": self.image_path("test.gif"),
                    "outbound_url": "https://example.com",
                },
                {
                    "image_path": self.image_path("test.png"),
                    "caption": "test.png",
                    "outbound_url": "https://example.com",
                },
            ]

            submission = subreddit.submit_gallery("Test Title", images)
            assert submission.author == pytest.placeholders.username
            assert submission.is_gallery
            assert submission.title == "Test Title"
            items = submission.gallery_data["items"]
            assert isinstance(submission.gallery_data["items"], list)
            for i, item in enumerate(items):
                test_data = images[i]
                test_data.pop("image_path")
                item.pop("id")
                item.pop("media_id")
                assert item == test_data

    def test_submit_gallery_disabled(self):
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubreddit.test_submit_gallery_disabled"):
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            images = [
                {"image_path": self.image_path("test.png")},
                {"image_path": self.image_path("test.jpg"), "caption": "test.jpg"},
                {
                    "image_path": self.image_path("test.gif"),
                    "outbound_url": "https://example.com",
                },
                {
                    "image_path": self.image_path("test.png"),
                    "caption": "test.png",
                    "outbound_url": "https://example.com",
                },
            ]

            with pytest.raises(RedditAPIException):
                subreddit.submit_gallery("Test Title", images)

    def test_submit_gallery__flair(self):
        flair_id = "6fc213da-cae7-11ea-9274-0e2407099e45"
        flair_text = "test"
        flair_class = "test-flair-class"
        self.reddit.read_only = False
        with self.recorder.use_cassette("TestSubreddit.test_submit_gallery__flair"):
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            images = [
                {"image_path": self.image_path("test.png")},
                {"image_path": self.image_path("test.jpg"), "caption": "test.jpg"},
                {
                    "image_path": self.image_path("test.gif"),
                    "outbound_url": "https://example.com",
                },
                {
                    "image_path": self.image_path("test.png"),
                    "caption": "test.png",
                    "outbound_url": "https://example.com",
                },
            ]
            submission = subreddit.submit_gallery(
                "Test Title", images, flair_id=flair_id, flair_text=flair_text
            )
            assert submission.link_flair_css_class == flair_class
            assert submission.link_flair_text == flair_text

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMock(
            "k5rhpg", "k5rhsu", "k5rhx3"  # update with cassette
        ),
    )
    def test_submit_image(self, _, __):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for i, file_name in enumerate(("test.png", "test.jpg", "test.gif")):
                image = self.image_path(file_name)

                submission = subreddit.submit_image(f"Test Title {i}", image)
                assert submission.author == self.reddit.config.username
                assert submission.is_reddit_media_domain
                assert submission.title == f"Test Title {i}"

    @mock.patch("time.sleep", return_value=None)
    def test_submit_image__large(self, _, tmp_path):
        reddit = self.reddit
        reddit.read_only = False
        mock_data = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Error>"
            "<Code>EntityTooLarge</Code>"
            "<Message>Your proposed upload exceeds the maximum allowed size</Message>"
            "<ProposedSize>20971528</ProposedSize>"
            "<MaxSizeAllowed>20971520</MaxSizeAllowed>"
            "<RequestId>23F056D6990D87E0</RequestId>"
            "<HostId>iYEVOuRfbLiKwMgHt2ewqQRIm0NWL79uiC2rPLj9P0PwW554MhjY2/O8d9JdKTf1iwzLjwWMnGQ=</HostId>"
            "</Error>"
        )
        _post = reddit._core._requestor._http.post

        def patch_request(url, *args, **kwargs):
            """Patch requests to return mock data on specific url."""
            if "https://reddit-uploaded-media.s3-accelerate.amazonaws.com" in url:
                response = requests.Response()
                response._content = mock_data.encode("utf-8")
                response.status_code = 400
                return response
            return _post(url, *args, **kwargs)

        reddit._core._requestor._http.post = patch_request
        fake_png = PNG_HEADER + b"\x1a" * 10  # Normally 1024 ** 2 * 20 (20 MB)
        with open(tmp_path.joinpath("fake_img.png"), "wb") as tempfile:
            tempfile.write(fake_png)
        with self.use_cassette():
            with pytest.raises(TooLargeMediaException):
                reddit.subreddit("test").submit_image("test", tempfile.name)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("websocket.create_connection", return_value=WebsocketMock())
    def test_submit_image__bad_websocket(self, _, __):
        self.reddit.read_only = False
        with self.use_cassette("TestSubreddit.test_submit_image"):
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for file_name in ("test.png", "test.jpg"):
                image = self.image_path(file_name)

                with pytest.raises(ClientException):
                    subreddit.submit_image("Test Title", image)

    @mock.patch("time.sleep", return_value=None)
    def test_submit_image__bad_filetype(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for file_name in ("test.mov", "test.mp4"):
                image = self.image_path(file_name)
                with pytest.raises(ClientException):
                    subreddit.submit_image("Test Title", image)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection", return_value=WebsocketMock("ah3gqo")
    )  # update with cassette
    def test_submit_image__flair(self, _, __):
        flair_id = "6bd28436-1aa7-11e9-9902-0e05ab0fad46"
        flair_text = "Test flair text"
        flair_class = "test-flair-class"
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.jpg")
            submission = subreddit.submit_image(
                "Test Title", image, flair_id=flair_id, flair_text=flair_text
            )
            assert submission.link_flair_css_class == flair_class
            assert submission.link_flair_text == flair_text

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection", return_value=WebsocketMock("k5s3b3")
    )  # update with cassette
    def test_submit_image_chat(self, _=None, __=None):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.jpg")
            submission = subreddit.submit_image(
                "Test Title", image, discussion_type="CHAT"
            )
            assert submission.discussion_type == "CHAT"

    @mock.patch("time.sleep", return_value=None)
    def test_submit_image_verify_invalid(self, _):
        self.reddit.read_only = False
        self.reddit.validate_on_submit = True
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.jpg")
            with pytest.raises(
                (RedditAPIException, BadRequest)
            ):  # waiting for prawcore fix
                subreddit.submit_image(
                    "gdfgfdgdgdgfgfdgdfgfdgfdg", image, without_websockets=True
                )

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection", side_effect=BlockingIOError
    )  # happens with timeout=0
    def test_submit_image__timeout_1(self, _, __):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.jpg")
            with pytest.raises(WebSocketException):
                subreddit.submit_image("Test Title", image)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        side_effect=socket.timeout
        # happens with timeout=0.00001
    )
    def test_submit_image__timeout_2(self, _, __):

        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.jpg")
            with pytest.raises(WebSocketException):
                subreddit.submit_image("Test Title", image)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMockException(
            recv_exc=websocket.WebSocketTimeoutException()
        ),  # happens with timeout=0.1
    )
    def test_submit_image__timeout_3(self, _, __):

        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.jpg")
            with pytest.raises(WebSocketException):
                subreddit.submit_image("Test Title", image)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMockException(
            close_exc=websocket.WebSocketTimeoutException()
        ),  # could happen, and PRAW should handle it
    )
    def test_submit_image__timeout_4(self, _, __):

        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.jpg")
            with pytest.raises(WebSocketException):
                subreddit.submit_image("Test Title", image)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMockException(
            recv_exc=websocket.WebSocketConnectionClosedException()
        ),  # from issue #1124
    )
    def test_submit_image__timeout_5(self, _, __):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.jpg")
            with pytest.raises(WebSocketException):
                subreddit.submit_image("Test Title", image)

    @mock.patch("time.sleep", return_value=None)
    def test_submit_image__without_websockets(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for file_name in ("test.png", "test.jpg", "test.gif"):
                image = self.image_path(file_name)

                submission = subreddit.submit_image(
                    "Test Title", image, without_websockets=True
                )
                assert submission is None

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMock("k5rsq3", "k5rt9d"),  # update with cassette
    )
    def test_submit_video(self, _, __):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for i, file_name in enumerate(("test.mov", "test.mp4")):
                video = self.image_path(file_name)

                submission = subreddit.submit_video(f"Test Title {i}", video)
                assert submission.author == self.reddit.config.username
                assert submission.is_video
                assert submission.title == f"Test Title {i}"

    @mock.patch("time.sleep", return_value=None)
    def test_submit_video__bad_filetype(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for file_name in ("test.jpg", "test.png", "test.gif"):
                video = self.image_path(file_name)
                with pytest.raises(ClientException):
                    subreddit.submit_video("Test Title", video)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("websocket.create_connection", return_value=WebsocketMock())
    def test_submit_video__bad_websocket(self, _, __):
        self.reddit.read_only = False
        with self.use_cassette("TestSubreddit.test_submit_video"):
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for file_name in ("test.mov", "test.mp4"):
                video = self.image_path(file_name)

                with pytest.raises(ClientException):
                    subreddit.submit_video("Test Title", video)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection", return_value=WebsocketMock("ahells")
    )  # update with cassette
    def test_submit_video__flair(self, _, __):
        flair_id = "6bd28436-1aa7-11e9-9902-0e05ab0fad46"
        flair_text = "Test flair text"
        flair_class = "test-flair-class"
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.mov")
            submission = subreddit.submit_video(
                "Test Title", image, flair_id=flair_id, flair_text=flair_text
            )
            assert submission.link_flair_css_class == flair_class
            assert submission.link_flair_text == flair_text

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection", return_value=WebsocketMock("flnyhf")
    )  # update with cassette
    def test_submit_video_chat(self, _=None, __=None):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.mov")
            submission = subreddit.submit_video(
                "Test Title", image, discussion_type="CHAT"
            )
            assert submission.discussion_type == "CHAT"

    @mock.patch("time.sleep", return_value=None)
    def test_submit_video_verify_invalid(self, _):
        self.reddit.read_only = False
        self.reddit.validate_on_submit = True
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            image = self.image_path("test.mov")
            with pytest.raises(
                (RedditAPIException, BadRequest)
            ):  # waiting for prawcore fix
                subreddit.submit_video(
                    "gdfgfdgdgdgfgfdgdfgfdgfdg", image, without_websockets=True
                )

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMock("k5rvt5", "k5rwbo"),  # update with cassette
    )
    def test_submit_video__thumbnail(self, _, __):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for video_name, thumb_name in (
                ("test.mov", "test.jpg"),
                ("test.mp4", "test.png"),
            ):
                video = self.image_path(video_name)
                thumb = self.image_path(thumb_name)

                submission = subreddit.submit_video(
                    "Test Title", video, thumbnail_path=thumb
                )
                assert submission.author == self.reddit.config.username
                assert submission.is_video
                assert submission.title == "Test Title"

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection", side_effect=BlockingIOError
    )  # happens with timeout=0
    def test_submit_video__timeout_1(self, _, __):

        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            video = self.image_path("test.mov")
            with pytest.raises(WebSocketException):
                subreddit.submit_video("Test Title", video)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        side_effect=socket.timeout
        # happens with timeout=0.00001
    )
    def test_submit_video__timeout_2(self, _, __):

        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            video = self.image_path("test.mov")
            with pytest.raises(WebSocketException):
                subreddit.submit_video("Test Title", video)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMockException(
            recv_exc=websocket.WebSocketTimeoutException()
        ),  # happens with timeout=0.1
    )
    def test_submit_video__timeout_3(self, _, __):

        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            video = self.image_path("test.mov")
            with pytest.raises(WebSocketException):
                subreddit.submit_video("Test Title", video)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMockException(
            close_exc=websocket.WebSocketTimeoutException()
        ),  # could happen, and PRAW should handle it
    )
    def test_submit_video__timeout_4(self, _, __):

        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            video = self.image_path("test.mov")
            with pytest.raises(WebSocketException):
                subreddit.submit_video("Test Title", video)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMockException(
            close_exc=websocket.WebSocketConnectionClosedException()
        ),  # from issue #1124
    )
    def test_submit_video__timeout_5(self, _, __):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            video = self.image_path("test.mov")
            with pytest.raises(WebSocketException):
                subreddit.submit_video("Test Title", video)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch(
        "websocket.create_connection",
        return_value=WebsocketMock("k5s10u", "k5s11v"),  # update with cassette
    )
    def test_submit_video__videogif(self, _, __):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for file_name in ("test.mov", "test.mp4"):
                video = self.image_path(file_name)

                submission = subreddit.submit_video("Test Title", video, videogif=True)
                assert submission.author == self.reddit.config.username
                assert submission.is_video
                assert submission.title == "Test Title"

    @mock.patch("time.sleep", return_value=None)
    def test_submit_video__without_websockets(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
            for file_name in ("test.mov", "test.mp4"):
                video = self.image_path(file_name)

                submission = subreddit.submit_video(
                    "Test Title", video, without_websockets=True
                )
                assert submission is None

    def test_subscribe(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            subreddit.subscribe()

    def test_subscribe__multiple(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            subreddit.subscribe(["redditdev", self.reddit.subreddit("iama")])

    def test_traffic(self):
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            traffic = subreddit.traffic()
            assert isinstance(traffic, dict)

    def test_traffic__not_public(self):
        subreddit = self.reddit.subreddit("announcements")
        with self.use_cassette():
            with pytest.raises(NotFound):
                subreddit.traffic()

    def test_unsubscribe(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            subreddit.unsubscribe()

    def test_unsubscribe__multiple(self):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            subreddit.unsubscribe(["redditdev", self.reddit.subreddit("iama")])


class TestSubredditFilters(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test__iter__all(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            filters = list(self.reddit.subreddit("all").filters)
        assert len(filters) > 0
        assert all(isinstance(x, Subreddit) for x in filters)

    @mock.patch("time.sleep", return_value=None)
    def test__iter__mod(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            filters = list(self.reddit.subreddit("mod").filters)
        assert len(filters) > 0
        assert all(isinstance(x, Subreddit) for x in filters)

    @mock.patch("time.sleep", return_value=None)
    def test_add(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.subreddit("all").filters.add("redditdev")

    @mock.patch("time.sleep", return_value=None)
    def test_add__subreddit_model(self, _):
        self.reddit.read_only = False
        with self.use_cassette("TestSubredditFilters.test_add"):
            self.reddit.subreddit("all").filters.add(self.reddit.subreddit("redditdev"))

    @mock.patch("time.sleep", return_value=None)
    def test_add__non_special(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(NotFound):
                self.reddit.subreddit("redditdev").filters.add("redditdev")

    @mock.patch("time.sleep", return_value=None)
    def test_remove(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.reddit.subreddit("mod").filters.remove("redditdev")

    @mock.patch("time.sleep", return_value=None)
    def test_remove__subreddit_model(self, _):
        self.reddit.read_only = False
        with self.use_cassette("TestSubredditFilters.test_remove"):
            self.reddit.subreddit("mod").filters.remove(
                self.reddit.subreddit("redditdev")
            )

    @mock.patch("time.sleep", return_value=None)
    def test_remove__non_special(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(NotFound):
                self.reddit.subreddit("redditdev").filters.remove("redditdev")


class TestSubredditFlair(IntegrationTest):
    REDDITOR = pytest.placeholders.username

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test__call(self):
        self.reddit.read_only = False
        with self.use_cassette():
            mapping = self.subreddit.flair()
            assert len(list(mapping)) > 0
            assert all(isinstance(x["user"], Redditor) for x in mapping)

    def test__call__user_filter(self):
        self.reddit.read_only = False
        with self.use_cassette():
            mapping = self.subreddit.flair(redditor=self.REDDITOR)
            assert len(list(mapping)) == 1

    def test_configure(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.flair.configure(
                position=None,
                self_assign=True,
                link_position=None,
                link_self_assign=True,
            )

    def test_configure__defaults(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.flair.configure()

    def test_delete(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.flair.delete(self.reddit.config.username)

    @mock.patch("time.sleep", return_value=None)
    def test_delete_all(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            response = self.subreddit.flair.delete_all()
            assert len(response) > 100
            assert all("removed" in x["status"] for x in response)

    def test_set__flair_id(self):
        self.reddit.read_only = False
        with self.use_cassette():
            redditor = self.reddit.redditor(self.reddit.config.username)
            flair = "11c32eee-1482-11e9-bfc0-0efc81a5e8e8"
            self.subreddit.flair.set(
                redditor, "redditor flair", flair_template_id=flair
            )

    def test_set__flair_id_default_text(self):
        self.reddit.read_only = False
        with self.use_cassette():
            redditor = self.reddit.redditor(self.reddit.config.username)
            flair = "11c32eee-1482-11e9-bfc0-0efc81a5e8e8"
            self.subreddit.flair.set(redditor, flair_template_id=flair)

    def test_set__redditor(self):
        self.reddit.read_only = False
        with self.use_cassette():
            redditor = self.subreddit._reddit.redditor(self.reddit.config.username)
            self.subreddit.flair.set(redditor, "redditor flair")

    def test_set__redditor_css_only(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.flair.set(
                self.reddit.config.username, css_class="some class"
            )

    def test_set__redditor_string(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.flair.set(
                self.reddit.config.username, "new flair", "some class"
            )

    def test_update(self):
        self.reddit.read_only = False
        redditor = self.subreddit._reddit.redditor(self.reddit.config.username)
        flair_list = [
            redditor,
            "spez",
            {"user": "bsimpson"},
            {"user": "spladug", "flair_text": "", "flair_css_class": ""},
        ]
        with self.use_cassette():
            response = self.subreddit.flair.update(flair_list, css_class="default")
        assert all(x["ok"] for x in response)
        assert not any(x["errors"] for x in response)
        assert not any(x["warnings"] for x in response)
        assert len([x for x in response if "added" in x["status"]]) == 3
        assert len([x for x in response if "removed" in x["status"]]) == 1
        for i, name in enumerate([str(redditor), "spez", "bsimpson", "spladug"]):
            assert name in response[i]["status"]

    def test_update__comma_in_text(self):
        self.reddit.read_only = False
        flair_list = [
            {"user": "bsimpson"},
            {"user": "spladug", "flair_text": "a,b"},
        ]
        with self.use_cassette():
            response = self.subreddit.flair.update(flair_list, css_class="default")
            assert all(x["ok"] for x in response)

    @mock.patch("time.sleep", return_value=None)
    def test_update_quotes(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            response = self.subreddit.flair.update(
                [self.reddit.user.me()], text='"testing"', css_class="testing"
            )
            assert all(x["ok"] for x in response)
            flair = next(self.subreddit.flair(self.reddit.user.me()))
            assert flair["flair_text"] == '"testing"'
            assert flair["flair_css_class"] == "testing"


class TestSubredditFlairTemplates(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test__iter(self):
        self.reddit.read_only = False
        with self.use_cassette():
            templates = list(self.subreddit.flair.templates)
        assert len(templates) > 100

        for flair_template in templates:
            assert flair_template["id"]

    def test_add(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.flair.templates.add(
                "PRAW", css_class="myCSS", background_color="#ABCDEF"
            )

    def test_clear(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.flair.templates.clear()

    @mock.patch("time.sleep", return_value=None)
    def test_delete(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.delete(template["id"])

    @mock.patch("time.sleep", return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.update(
                template["id"],
                "PRAW updated",
                css_class="myCSS",
                text_color="dark",
                background_color="#00FFFF",
            )

    @mock.patch("time.sleep", return_value=None)
    def test_update_invalid(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(InvalidFlairTemplateID):
                self.subreddit.flair.templates.update(
                    "fake id",
                    "PRAW updated",
                    css_class="myCSS",
                    text_color="dark",
                    background_color="#00FFFF",
                    fetch=True,
                )

    @mock.patch("time.sleep", return_value=None)
    def test_update_fetch(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.update(
                template["id"],
                "PRAW updated",
                css_class="myCSS",
                text_color="dark",
                background_color="#00FFFF",
                fetch=True,
            )

    @mock.patch("time.sleep", return_value=None)
    def test_update_fetch_no_css_class(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.update(
                template["id"],
                "PRAW updated",
                text_color="dark",
                background_color="#00FFFF",
                fetch=True,
            )

    @mock.patch("time.sleep", return_value=None)
    def test_update_fetch_no_text(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.update(
                template["id"],
                css_class="myCSS",
                text_color="dark",
                background_color="#00FFFF",
                fetch=True,
            )

    @mock.patch("time.sleep", return_value=None)
    def test_update_fetch_no_text_or_css_class(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.update(
                template["id"],
                text_color="dark",
                background_color="#00FFFF",
                fetch=True,
            )

    @mock.patch("time.sleep", return_value=None)
    def test_update_fetch_only(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.update(template["id"], fetch=True)
            newtemplate = list(
                filter(
                    lambda _template: _template["id"] == template["id"],
                    self.subreddit.flair.templates,
                )
            )[0]
            assert newtemplate == template

    @mock.patch("time.sleep", return_value=None)
    def test_update_false(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            template = list(self.subreddit.flair.templates)[0]
            self.subreddit.flair.templates.update(
                template["id"], text_editable=True, fetch=True
            )
            self.subreddit.flair.templates.update(
                template["id"], text_editable=False, fetch=True
            )
            newtemplate = list(
                filter(
                    lambda _template: _template["id"] == template["id"],
                    self.subreddit.flair.templates,
                )
            )[0]
            assert newtemplate["text_editable"] is False


class TestSubredditLinkFlairTemplates(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test__iter(self):
        self.reddit.read_only = False
        with self.use_cassette():
            templates = list(self.subreddit.flair.link_templates)
        assert len(templates) > 100

        for template in templates:
            assert template["id"]
            assert isinstance(template["richtext"], list)
            assert all(isinstance(item, dict) for item in template["richtext"])

    def test_add(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.flair.link_templates.add(
                "PRAW", css_class="myCSS", text_color="light"
            )

    def test_clear(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.flair.link_templates.clear()


class TestSubredditListings(IntegrationTest):
    def test_comments(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("askreddit")
            comments = list(subreddit.comments())
        assert len(comments) == 100

    def test_controversial(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("askreddit")
            submissions = list(subreddit.controversial())
        assert len(submissions) == 100

    def test_gilded(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("askreddit")
            submissions = list(subreddit.gilded())
        assert len(submissions) >= 50

    def test_hot(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("askreddit")
            submissions = list(subreddit.hot())
        assert len(submissions) == 100

    def test_new(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("askreddit")
            submissions = list(subreddit.new())
        assert len(submissions) == 100

    def test_random_rising(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("askreddit")
            submissions = list(subreddit.random_rising())
        assert len(submissions) == 100

    def test_rising(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("askreddit")
            submissions = list(subreddit.rising())
        assert len(submissions) == 100

    def test_top(self):
        with self.use_cassette():
            subreddit = self.reddit.subreddit("askreddit")
            submissions = list(subreddit.top())
        assert len(submissions) == 100


class TestSubredditModeration(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_accept_invite__no_invite(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                self.subreddit.mod.accept_invite()
            assert excinfo.value.items[0].error_type == "NO_INVITE_FOUND"

    def test_edited(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.edited():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count == 100

    def test_edited__only_comments(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.edited(only="comments"):
                assert isinstance(item, Comment)
                count += 1
            assert count == 100

    def test_edited__only_submissions(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.edited(only="submissions"):
                assert isinstance(item, Submission)
                count += 1
            assert count > 0

    def test_inbox(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.subreddit("all").mod.inbox():
                assert isinstance(item, SubredditMessage)
                count += 1
            assert count == 100

    def test_log(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.subreddit("mod").mod.log():
                assert isinstance(item, ModAction)
                count += 1
            assert count == 100

    def test_log__filters(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.subreddit("mod").mod.log(
                action="invitemoderator", mod=self.reddit.redditor("bboe_dev")
            ):
                assert isinstance(item, ModAction)
                assert item.action == "invitemoderator"
                assert isinstance(item.mod, Redditor)
                assert item.mod == "bboe_dev"
                count += 1
            assert count > 0

    def test_modqueue(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.modqueue():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count > 0

    def test_modqueue__only_comments(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.modqueue(only="comments"):
                assert isinstance(item, Comment)
                count += 1
            assert count > 0

    def test_modqueue__only_submissions(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.modqueue(only="submissions"):
                assert isinstance(item, Submission)
                count += 1
            assert count > 0

    def test_reports(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.reports():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count == 100

    def test_reports__only_comments(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.reports(only="comments"):
                assert isinstance(item, Comment)
                count += 1
            assert count > 0

    def test_reports__only_submissions(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.reports(only="submissions"):
                assert isinstance(item, Submission)
                count += 1
            assert count == 100

    def test_spam(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.spam():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count > 0

    def test_spam__only_comments(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.spam(only="comments"):
                assert isinstance(item, Comment)
                count += 1
            assert count > 0

    def test_spam__only_submissions(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.spam(only="submissions"):
                assert isinstance(item, Submission)
                count += 1
            assert count > 0

    def test_unmoderated(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.subreddit.mod.unmoderated():
                assert isinstance(item, (Comment, Submission))
                count += 1
            assert count > 0

    def test_unread(self):
        self.reddit.read_only = False
        with self.use_cassette():
            count = 0
            for item in self.reddit.subreddit("all").mod.unread():
                assert isinstance(item, SubredditMessage)
                count += 1
            assert count > 0

    @mock.patch("time.sleep", return_value=None)
    def test_update(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            before_settings = self.subreddit.mod.settings()
            new_title = f"{before_settings['title']}x"
            new_title = (
                "x"
                if (len(new_title) >= 20 and "placeholder" not in new_title)
                else new_title
            )
            self.subreddit.mod.update(title=new_title)
            assert self.subreddit.title == new_title
            after_settings = self.subreddit.mod.settings()

            # Ensure that nothing has changed besides what was specified.
            before_settings["title"] = new_title
            assert before_settings == after_settings


class TestSubredditModmail(IntegrationTest):
    @property
    def redditor(self):
        return self.reddit.redditor(pytest.placeholders.username)

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_bulk_read(self):
        self.reddit.read_only = False
        with self.use_cassette():
            for conversation in self.subreddit.modmail.bulk_read(state="new"):
                assert isinstance(conversation, ModmailConversation)

    @mock.patch("time.sleep", return_value=None)
    def test_call(self, _):
        self.reddit.read_only = False
        conversation_id = "ik72"
        with self.use_cassette():
            conversation = self.reddit.subreddit("all").modmail(conversation_id)
            assert isinstance(conversation.user, Redditor)
            for message in conversation.messages:
                assert isinstance(message, ModmailMessage)
            for action in conversation.mod_actions:
                assert isinstance(action, ModmailAction)

    @mock.patch("time.sleep", return_value=None)
    def test_call__internal(self, _):
        self.reddit.read_only = False
        conversation_id = "nbhy"
        with self.use_cassette():
            conversation = self.reddit.subreddit("all").modmail(conversation_id)
            for message in conversation.messages:
                assert isinstance(message, ModmailMessage)
            for action in conversation.mod_actions:
                assert isinstance(action, ModmailAction)

    @mock.patch("time.sleep", return_value=None)
    def test_call__mark_read(self, _):
        self.reddit.read_only = False
        conversation = self.reddit.subreddit("all").modmail("o7wz", mark_read=True)
        with self.use_cassette():
            assert conversation.last_unread is None

    @mock.patch("time.sleep", return_value=None)
    def test_conversations(self, _):
        self.reddit.read_only = False
        conversations = self.reddit.subreddit("all").modmail.conversations()
        with self.use_cassette():
            for conversation in conversations:
                assert isinstance(conversation, ModmailConversation)
                assert isinstance(conversation.authors[0], Redditor)

    @mock.patch("time.sleep", return_value=None)
    def test_conversations__params(self, _):
        self.reddit.read_only = False
        conversations = self.reddit.subreddit("all").modmail.conversations(state="mod")
        with self.use_cassette():
            for conversation in conversations:
                assert conversation.is_internal

    @mock.patch("time.sleep", return_value=None)
    def test_conversations__other_subreddits(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit("modmailtestA")
        conversations = subreddit.modmail.conversations(
            other_subreddits=["modmailtestB"]
        )
        with self.use_cassette():
            assert len(set(conversation.owner for conversation in conversations)) > 1

    @mock.patch("time.sleep", return_value=None)
    def test_create(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            conversation = self.subreddit.modmail.create(
                "Subject", "Body", self.redditor
            )
        assert isinstance(conversation, ModmailConversation)

    def test_subreddits(self):
        self.reddit.read_only = False
        with self.use_cassette():
            for subreddit in self.subreddit.modmail.subreddits():
                assert isinstance(subreddit, Subreddit)

    def test_unread_count(self):
        self.reddit.read_only = False
        with self.use_cassette():
            assert isinstance(self.subreddit.modmail.unread_count(), dict)


class TestSubredditQuarantine(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_opt_in(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit("ferguson")
        with self.use_cassette():
            with pytest.raises(Forbidden):
                next(subreddit.hot())
            subreddit.quaran.opt_in()
            assert isinstance(next(subreddit.hot()), Submission)

    @mock.patch("time.sleep", return_value=None)
    def test_opt_out(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit("ferguson")
        with self.use_cassette():
            subreddit.quaran.opt_out()
            with pytest.raises(Forbidden):
                next(subreddit.hot())


class TestSubredditRelationships(IntegrationTest):
    REDDITOR = "pyapitestuser3"

    @mock.patch("time.sleep", return_value=None)
    def add_remove(self, base, user, relationship, _):
        relationship = getattr(base, relationship)
        relationship.add(user)
        relationships = list(relationship())
        assert user in relationships
        redditor = relationships[relationships.index(user)]
        assert isinstance(redditor, Redditor)
        assert hasattr(redditor, "date")
        relationship.remove(user)
        assert user not in relationship()

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_banned(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.add_remove(self.subreddit, self.REDDITOR, "banned")

    def test_banned__user_filter(self):
        self.reddit.read_only = False
        banned = self.subreddit.banned(redditor="pyapitestuser3")
        with self.use_cassette():
            assert len(list(banned)) == 1

    def test_contributor(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.add_remove(self.subreddit, self.REDDITOR, "contributor")

    @mock.patch("time.sleep", return_value=None)
    def test_contributor_leave(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.contributor.leave()

    def test_contributor__user_filter(self):
        self.reddit.read_only = False
        contributor = self.subreddit.contributor(redditor="pyapitestuser3")
        with self.use_cassette():
            assert len(list(contributor)) == 1

    @mock.patch("time.sleep", return_value=None)
    def test_moderator(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            # Moderators can only be invited.
            # As of 2016-03-18 there is no API endpoint to get the moderator
            # invite list.
            self.subreddit.moderator.add(self.REDDITOR)
            assert self.REDDITOR not in self.subreddit.moderator()

    @mock.patch("time.sleep", return_value=None)
    def test_moderator__limited_permissions(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            # Moderators can only be invited.
            # As of 2016-03-18 there is no API endpoint to get the moderator
            # invite list.
            self.subreddit.moderator.add(self.REDDITOR, permissions=["access", "wiki"])
            assert self.REDDITOR not in self.subreddit.moderator()

    def test_moderator_invite__invalid_perm(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                self.subreddit.moderator.invite(self.REDDITOR, permissions=["a"])
            assert excinfo.value.items[0].error_type == "INVALID_PERMISSIONS"

    @mock.patch("time.sleep", return_value=None)
    def test_moderator_invite__no_perms(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            # Moderators can only be invited.
            # As of 2016-03-18 there is no API endpoint to get the moderator
            # invite list.
            self.subreddit.moderator.invite(self.REDDITOR, permissions=[])
            assert self.REDDITOR not in self.subreddit.moderator()

    @mock.patch("time.sleep", return_value=None)
    def test_moderator_invited_moderators(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            invited = self.subreddit.moderator.invited()
            assert isinstance(invited, ListingGenerator)
            for moderator in invited:
                assert isinstance(moderator, Redditor)

    @mock.patch("time.sleep", return_value=None)
    def test_moderator_leave(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.moderator.leave()

    def test_moderator_update(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.moderator.update(self.REDDITOR, permissions=["config"])

    def test_moderator_update_invite(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.moderator.update_invite(self.REDDITOR, permissions=["mail"])

    def test_moderator__user_filter(self):
        self.reddit.read_only = False
        with self.use_cassette():
            moderator = self.subreddit.moderator(redditor="pyapitestuser3")
        assert len(moderator) == 1
        assert "mod_permissions" in moderator[0].__dict__

    def test_muted(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.add_remove(self.subreddit, self.REDDITOR, "muted")

    def test_moderator_remove_invite(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.moderator.remove_invite(self.REDDITOR)

    def test_wiki_banned(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.add_remove(self.subreddit.wiki, self.REDDITOR, "banned")

    def test_wiki_contributor(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.add_remove(self.subreddit.wiki, self.REDDITOR, "contributor")


class TestSubredditStreams(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test_comments(self, _):
        with self.use_cassette():
            generator = self.reddit.subreddit("all").stream.comments()
            for i in range(400):
                assert isinstance(next(generator), Comment)

    @mock.patch("time.sleep", return_value=None)
    def test_comments__with_pause(self, _):
        with self.use_cassette():
            comment_stream = self.reddit.subreddit("kakapo").stream.comments(
                pause_after=0
            )
            comment_count = 1
            pause_count = 1
            comment = next(comment_stream)
            while comment is not None:
                comment_count += 1
                comment = next(comment_stream)
            while comment is None:
                pause_count += 1
                comment = next(comment_stream)
            assert comment_count == 17
            assert pause_count == 2

    @mock.patch("time.sleep", return_value=None)
    def test_comments__with_skip_existing(self, _):
        with self.use_cassette("TestSubredditStreams.test_comments__with_pause"):
            generator = self.reddit.subreddit("all").stream.comments(skip_existing=True)
            count = 0
            try:
                for comment in generator:
                    count += 1
            except RequestException:
                pass
            # This test uses the same cassette as test_comments which shows
            # that there are at least 400 comments in the stream.
            assert count < 400

    def test_submissions(self):
        with self.use_cassette():
            generator = self.reddit.subreddit("all").stream.submissions()
            for i in range(101):
                assert isinstance(next(generator), Submission)

    @mock.patch("time.sleep", return_value=None)
    def test_submissions__with_pause(self, _):
        with self.use_cassette("TestSubredditStreams.test_submissions"):
            generator = self.reddit.subreddit("all").stream.submissions(pause_after=-1)
            submission = next(generator)
            submission_count = 0
            while submission is not None:
                submission_count += 1
                submission = next(generator)
            assert submission_count == 100

    @mock.patch("time.sleep", return_value=None)
    def test_submissions__with_pause_and_skip_after(self, _):
        with self.use_cassette("TestSubredditStreams.test_submissions"):
            generator = self.reddit.subreddit("all").stream.submissions(
                pause_after=-1, skip_existing=True
            )
            submission = next(generator)
            assert submission is None  # The first thing yielded should be None
            submission_count = 0
            submission = next(generator)
            while submission is not None:
                submission_count += 1
                submission = next(generator)
            assert submission_count < 100


class TestSubredditModerationStreams(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    @mock.patch("time.sleep", return_value=None)
    def test_edited(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            generator = self.subreddit.mod.stream.edited()
            for i in range(10):
                assert isinstance(next(generator), (Comment, Submission))

    @mock.patch("time.sleep", return_value=None)
    def test_log(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            generator = self.subreddit.mod.stream.log()
            for i in range(101):
                assert isinstance(next(generator), ModAction)

    @mock.patch("time.sleep", return_value=None)
    def test_modmail_conversations(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            generator = self.reddit.subreddit("mod").mod.stream.modmail_conversations()
            for i in range(10):
                assert isinstance(next(generator), ModmailConversation)

    @mock.patch("time.sleep", return_value=None)
    def test_modqueue(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            generator = self.subreddit.mod.stream.modqueue()
            for i in range(10):
                assert isinstance(next(generator), (Comment, Submission))

    @mock.patch("time.sleep", return_value=None)
    def test_spam(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            generator = self.subreddit.mod.stream.spam()
            for i in range(10):
                assert isinstance(next(generator), (Comment, Submission))

    @mock.patch("time.sleep", return_value=None)
    def test_reports(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            generator = self.subreddit.mod.stream.reports()
            for i in range(10):
                assert isinstance(next(generator), (Comment, Submission))

    @mock.patch("time.sleep", return_value=None)
    def test_unmoderated(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            generator = self.subreddit.mod.stream.unmoderated()
            for i in range(10):
                assert isinstance(next(generator), (Comment, Submission))

    @mock.patch("time.sleep", return_value=None)
    def test_unread(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            generator = self.reddit.subreddit("mod").mod.stream.unread()
            for i in range(2):
                assert isinstance(next(generator), SubredditMessage)


class TestSubredditStylesheet(IntegrationTest):
    @staticmethod
    def image_path(name):
        test_dir = abspath(dirname(sys.modules[__name__].__file__))
        return join(test_dir, "..", "..", "files", name)

    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_call(self):
        with self.use_cassette():
            stylesheet = self.subreddit.stylesheet()
        assert isinstance(stylesheet, Stylesheet)
        assert len(stylesheet.images) > 0
        assert stylesheet.stylesheet != ""

    def test_delete_banner(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.delete_banner()

    def test_delete_banner_additional_image(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.delete_banner_additional_image()

    def test_delete_banner_hover_image(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.delete_banner_hover_image()

    def test_delete_header(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.delete_header()

    def test_delete_image(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.delete_image("praw")

    def test_delete_mobile_header(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.delete_mobile_header()

    def test_delete_mobile_icon(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.delete_mobile_icon()

    def test_update(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.update("p { color: red; }")

    def test_update__with_reason(self):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.update("div { color: red; }", reason="use div")

    def test_upload(self):
        self.reddit.read_only = False
        with self.use_cassette():
            response = self.subreddit.stylesheet.upload(
                "praw", self.image_path("white-square.png")
            )
        assert response["img_src"].endswith(".png")

    def test_upload__invalid(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                self.subreddit.stylesheet.upload("praw", self.image_path("invalid.jpg"))
        assert excinfo.value.items[0].error_type == "IMAGE_ERROR"

    def test_upload__invalid_ext(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException) as excinfo:
                self.subreddit.stylesheet.upload(
                    "praw.png", self.image_path("white-square.png")
                )
        assert excinfo.value.items[0].error_type == "BAD_CSS_NAME"

    def test_upload__too_large(self):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(TooLarge):
                self.subreddit.stylesheet.upload(
                    "praw", self.image_path("too_large.jpg")
                )

    @mock.patch("time.sleep", return_value=None)
    def test_upload_banner__jpg(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.upload_banner(self.image_path("white-square.jpg"))

    @mock.patch("time.sleep", return_value=None)
    def test_upload_banner__png(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.upload_banner(self.image_path("white-square.png"))

    @mock.patch("time.sleep", return_value=None)
    def test_upload_banner_additional_image__jpg(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.upload_banner_additional_image(
                self.image_path("white-square.jpg")
            )

    @mock.patch("time.sleep", return_value=None)
    def test_upload_banner_additional_image__png(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.upload_banner_additional_image(
                self.image_path("white-square.png")
            )

    @mock.patch("time.sleep", return_value=None)
    def test_upload_banner_additional_image__align(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            for alignment in ("left", "centered", "right"):
                self.subreddit.stylesheet.upload_banner_additional_image(
                    self.image_path("white-square.png"), align=alignment
                )

    @mock.patch("time.sleep", return_value=None)
    def test_upload_banner_hover_image__jpg(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.upload_banner_additional_image(
                self.image_path("white-square.png")
            )
            self.subreddit.stylesheet.upload_banner_hover_image(
                self.image_path("white-square.jpg")
            )

    @mock.patch("time.sleep", return_value=None)
    def test_upload_banner_hover_image__png(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            self.subreddit.stylesheet.upload_banner_additional_image(
                self.image_path("white-square.jpg")
            )
            self.subreddit.stylesheet.upload_banner_hover_image(
                self.image_path("white-square.png")
            )

    def test_upload_header__jpg(self):
        self.reddit.read_only = False
        with self.use_cassette():
            response = self.subreddit.stylesheet.upload_header(
                self.image_path("white-square.jpg")
            )
        assert response["img_src"].endswith(".jpg")

    def test_upload_header__png(self):
        self.reddit.read_only = False
        with self.use_cassette():
            response = self.subreddit.stylesheet.upload_header(
                self.image_path("white-square.png")
            )
        assert response["img_src"].endswith(".png")

    def test_upload_mobile_header(self):
        self.reddit.read_only = False
        with self.use_cassette():
            response = self.subreddit.stylesheet.upload_mobile_header(
                self.image_path("header.jpg")
            )
        assert response["img_src"].endswith(".jpg")

    def test_upload_mobile_icon(self):
        self.reddit.read_only = False
        with self.use_cassette():
            response = self.subreddit.stylesheet.upload_mobile_icon(
                self.image_path("icon.jpg")
            )
        assert response["img_src"].endswith(".jpg")

    @mock.patch("time.sleep", return_value=None)
    def test_upload__others_invalid(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            for method in [
                "upload_header",
                "upload_mobile_header",
                "upload_mobile_icon",
            ]:
                with pytest.raises(RedditAPIException) as excinfo:
                    getattr(self.subreddit.stylesheet, method)(
                        self.image_path("invalid.jpg")
                    )
                assert excinfo.value.items[0].error_type == "IMAGE_ERROR"

    def test_upload__others_too_large(self):
        self.reddit.read_only = False
        with self.use_cassette():
            for method in [
                "upload_header",
                "upload_mobile_header",
                "upload_mobile_icon",
            ]:
                with pytest.raises(TooLarge):
                    getattr(self.subreddit.stylesheet, method)(
                        self.image_path("too_large.jpg")
                    )


class TestSubredditWiki(IntegrationTest):
    @mock.patch("time.sleep", return_value=None)
    def test__iter(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)
        with self.use_cassette():
            count = 0
            for wikipage in subreddit.wiki:
                assert isinstance(wikipage, WikiPage)
                count += 1
            assert count > 0

    @mock.patch("time.sleep", return_value=None)
    def test_create(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)

        with self.use_cassette():
            wikipage = subreddit.wiki.create(
                "PRAW New Page", "This is the new wiki page"
            )
            assert wikipage.name == "praw_new_page"
            assert wikipage.content_md == "This is the new wiki page"

    @mock.patch("time.sleep", return_value=None)
    def test_revisions(self, _):
        self.reddit.read_only = False
        subreddit = self.reddit.subreddit(pytest.placeholders.test_subreddit)

        with self.use_cassette():
            count = 0
            for revision in subreddit.wiki.revisions(limit=4):
                count += 1
                assert isinstance(revision["author"], Redditor)
                assert isinstance(revision["page"], WikiPage)
            assert count == 4
