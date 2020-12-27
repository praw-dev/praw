import pickle

from praw.models import InlineGif, InlineImage, InlineMedia, InlineVideo

from ... import UnitTest


class TestInlineMedia(UnitTest):
    def test_equality(self):
        media1 = InlineMedia(path="path1", caption="caption1")
        media1.media_id = "media_id1"
        media2 = InlineMedia(path="path1", caption="caption1")
        media2.media_id = "media_id1"
        media3 = InlineMedia(path="path2", caption="caption2")
        media3.media_id = "media_id2"
        assert media1 == media1
        assert media2 == media2
        assert media3 == media3
        assert media1 == media2
        assert media2 != media3
        assert media1 != media3

    def test_pickle(self):
        media = InlineMedia(path="path1", caption="caption1")
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(media, protocol=level))
            assert media == other

    def test_repr(self):
        media = InlineMedia(path="path1", caption="caption1")
        no_caption = InlineMedia(path="path1")
        gif = InlineGif(path="gif_path1", caption="gif_caption1")
        image = InlineImage(path="image_path1", caption="image_caption1")
        video = InlineVideo(path="video_path1", caption="video_caption1")
        assert repr(media) == "<InlineMedia caption='caption1'>"
        assert repr(no_caption) == "<InlineMedia caption=None>"
        assert repr(gif) == "<InlineGif caption='gif_caption1'>"
        assert repr(image) == "<InlineImage caption='image_caption1'>"
        assert repr(video) == "<InlineVideo caption='video_caption1'>"

    def test_str(self):
        media = InlineMedia(path="path1", caption="caption1")
        no_caption = InlineMedia(path="path1")
        gif = InlineGif(path="gif_path1", caption="gif_caption1")
        image = InlineImage(path="image_path1", caption="image_caption1")
        video = InlineVideo(path="video_path1", caption="video_caption1")
        media.media_id = "media_media_id"
        no_caption.media_id = "media_media_id_no_caption"
        gif.media_id = "gif_media_id"
        image.media_id = "image_media_id"
        video.media_id = "video_media_id"
        assert str(media) == '\n\n![None](media_media_id "caption1")\n\n'
        assert str(no_caption) == '\n\n![None](media_media_id_no_caption "")\n\n'
        assert str(gif) == '\n\n![gif](gif_media_id "gif_caption1")\n\n'
        assert str(image) == '\n\n![img](image_media_id "image_caption1")\n\n'
        assert str(video) == '\n\n![video](video_media_id "video_caption1")\n\n'
