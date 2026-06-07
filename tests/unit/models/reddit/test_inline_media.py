import pickle

from praw.models import InlineGif, InlineImage, InlineMedia, InlineVideo, PostMedia

from ... import UnitTest


class TestInlineMedia(UnitTest):
    def test_equality(self):
        media1 = InlineMedia(caption="caption1", media=PostMedia(b"data1", name="name1"))
        media1.media_id = "media_id1"
        media2 = InlineMedia(caption="caption1", media=PostMedia(b"data1", name="name1"))
        media2.media_id = "media_id1"
        media3 = InlineMedia(caption="caption2", media=PostMedia(b"data2", name="name2"))
        media3.media_id = "media_id2"
        assert media1 == media1
        assert media2 == media2
        assert media3 == media3
        assert media1 == media2
        assert media2 != media3
        assert media1 != media3

    def test_hash(self):
        media1 = InlineMedia(caption="caption1", media=PostMedia(b"data1", name="name1"))
        media1.media_id = "media_id1"
        media2 = InlineMedia(caption="caption1", media=PostMedia(b"data1", name="name1"))
        media2.media_id = "media_id1"
        media3 = InlineMedia(caption="caption2", media=PostMedia(b"data2", name="name2"))
        media3.media_id = "media_id2"
        assert hash(media1) == hash(media1)
        assert hash(media2) == hash(media2)
        assert hash(media3) == hash(media3)
        assert hash(media1) == hash(media2)
        assert hash(media2) != hash(media3)
        assert hash(media1) != hash(media3)

    def test_pickle(self):
        media = InlineMedia(caption="caption1", media=PostMedia(b"data1", name="name1"))
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(media, protocol=level))
            assert media == other

    def test_repr(self):
        media = InlineMedia(caption="caption1", media=PostMedia(b"data1", name="name1"))
        no_caption = InlineMedia(media=PostMedia(b"data1", name="name1"))
        gif = InlineGif(caption="gif_caption1", media=PostMedia(b"gif_data1", name="gif_name1"))
        image = InlineImage(caption="image_caption1", media=PostMedia(b"image_data1", name="image_name1"))
        video = InlineVideo(caption="video_caption1", media=PostMedia(b"video_data1", name="video_name1"))
        assert repr(media) == "<InlineMedia caption='caption1'>"
        assert repr(no_caption) == "<InlineMedia caption=None>"
        assert repr(gif) == "<InlineGif caption='gif_caption1'>"
        assert repr(image) == "<InlineImage caption='image_caption1'>"
        assert repr(video) == "<InlineVideo caption='video_caption1'>"

    def test_str(self):
        media = InlineMedia(caption="caption1", media=PostMedia(b"data1", name="name1"))
        no_caption = InlineMedia(media=PostMedia(b"data1", name="name1"))
        gif = InlineGif(caption="gif_caption1", media=PostMedia(b"gif_data1", name="gif_name1"))
        image = InlineImage(caption="image_caption1", media=PostMedia(b"image_data1", name="image_name1"))
        video = InlineVideo(caption="video_caption1", media=PostMedia(b"video_data1", name="video_name1"))
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
