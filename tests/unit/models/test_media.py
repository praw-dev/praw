import pickle
from pathlib import Path

import pytest

from praw.exceptions import ClientException
from praw.models import (
    EmojiMedia,
    PostMedia,
    StylesheetAsset,
    StylesheetImage,
    WidgetMedia,
)
from praw.models.media import Media

from .. import UnitTest


class TestMedia(UnitTest):
    def test_equality(self):
        media1 = PostMedia(b"data1", name="name1")
        media2 = PostMedia(b"data1", name="name1")
        media3 = PostMedia(b"data2", name="name1")
        media4 = PostMedia(b"data1", name="name2")
        media5 = EmojiMedia(b"data1", name="name1")
        assert media1 == media1
        assert media1 == media2
        assert media1 != media3
        assert media1 != media4
        assert media1 != media5

    def test_hash(self):
        media1 = PostMedia(b"data1", name="name1")
        media2 = PostMedia(b"data1", name="name1")
        media3 = PostMedia(b"data2", name="name2")
        assert hash(media1) == hash(media2)
        assert hash(media1) != hash(media3)

    def test_init__bytes(self):
        media = PostMedia(b"data", name="image.png")
        assert media.name == "image.png"
        assert media._data == b"data"

    def test_init__name_derived_from_path(self, image_path):
        path = image_path("test.png")
        media = PostMedia(path)
        assert media.name == "test.png"
        assert media._data == Path(path).read_bytes()

    def test_init__name_overrides_path(self, image_path):
        media = PostMedia(image_path("test.png"), name="other.png")
        assert media.name == "other.png"

    def test_init__name_required_for_bytes(self):
        message = "'name' is required when 'fp' is a bytes object."
        with pytest.raises(ValueError) as excinfo:
            PostMedia(b"data")
        assert str(excinfo.value) == message

    def test_init__nonexistent_path(self):
        with pytest.raises(FileNotFoundError):
            PostMedia("nonexistent_path.png")

    def test_mime_type(self):
        for name, mime_type in [
            ("test.gif", "image/gif"),
            ("test.jpeg", "image/jpeg"),
            ("test.jpg", "image/jpeg"),
            ("test.mov", "video/quicktime"),
            ("test.mp4", "video/mp4"),
            ("test.png", "image/png"),
        ]:
            assert Media(b"data", name=name)._mime_type == mime_type

    def test_mime_type__unknown(self):
        media = Media(b"data", name="unknown.invalid_extension")
        message = "Unable to determine the MIME type of 'unknown.invalid_extension'."
        with pytest.raises(ClientException) as excinfo:
            media._mime_type
        assert str(excinfo.value) == message

    def test_pickle(self):
        media = PostMedia(b"data", name="image.png")
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(media, protocol=level))
            assert media == other

    def test_repr(self):
        assert repr(PostMedia(b"data", name="image.png")) == "<PostMedia name='image.png'>"
        assert repr(WidgetMedia(b"data", name="image.jpg")) == "<WidgetMedia name='image.jpg'>"


class TestPostMedia(UnitTest):
    def test_upload__expected_mime_prefix(self, reddit):
        media = PostMedia(b"data", name="test.png")
        message = "Expected a mimetype starting with 'video' but got mimetype 'image/png' (from file name 'test.png')."
        with pytest.raises(ClientException) as excinfo:
            media._upload(reddit, expected_mime_prefix="video")
        assert str(excinfo.value) == message


class TestStylesheetAsset(UnitTest):
    def test_lease_data(self):
        media = StylesheetAsset(b"data", name="image.png")
        assert media._build_lease_data(imagetype="bannerBackgroundImage") == {
            "filepath": "image.png",
            "imagetype": "bannerBackgroundImage",
            "mimetype": "image/png",
        }


class TestStylesheetImage(UnitTest):
    def test_image_type(self):
        jpeg = StylesheetImage(b"\xff\xd8\xff data", name="image.jpg")
        assert jpeg._image_type == "jpg"
        png = StylesheetImage(b"\x89PNG data", name="image.png")
        assert png._image_type == "png"
