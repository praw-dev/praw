"""Tests Subreddit image upload and delete utilities."""

from __future__ import print_function, unicode_literals

import os
import sys
from praw import errors
from .helper import PRAWTest, betamax


class ImageTests(PRAWTest):
    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)
        self.subreddit = self.r.get_subreddit(self.sr)
        test_dir = os.path.dirname(sys.modules[__name__].__file__)
        self.image_path = os.path.join(test_dir, 'files', '{0}')

    @betamax()
    def test_delete_header(self):
        self.subreddit.delete_image(header=True)

    @betamax()
    def test_delete_image(self):
        images = self.subreddit.get_stylesheet()['images']
        self.assertTrue(images)
        for img_data in images[:5]:
            self.subreddit.delete_image(name=img_data['name'])
        updated_images = self.subreddit.get_stylesheet(uniq=1)['images']
        self.assertNotEqual(images, updated_images)

    @betamax()
    def test_delete_invalid_image(self):
        self.assertRaises(errors.BadCSSName,
                          self.subreddit.delete_image, 'invalid_image_name')

    @betamax()
    def test_delete_invalid_params(self):
        self.assertRaises(TypeError, self.subreddit.delete_image, name='Foo',
                          header=True)

    @betamax()
    def test_upload_invalid_file_path(self):
        self.assertRaises(IOError, self.subreddit.upload_image, 'nonexistent')

    @betamax()
    def test_upload_invalid_image(self):
        image = self.image_path.format('white-square.tiff')
        self.assertRaises(errors.ClientException, self.subreddit.upload_image,
                          image)

    @betamax()
    def test_upload_invalid_image_too_small(self):
        image = self.image_path.format('invalid.jpg')
        self.assertRaises(errors.ClientException, self.subreddit.upload_image,
                          image)

    @betamax()
    def test_upload_invalid_image_too_large(self):
        image = self.image_path.format('big')
        self.assertRaises(errors.ClientException, self.subreddit.upload_image,
                          image)

    @betamax()
    def test_upload_invalid_params(self):
        image = self.image_path.format('white-square.jpg')
        self.assertRaises(TypeError, self.subreddit.upload_image, image,
                          name='Foo', header=True)

    @betamax()
    def test_upload_invalid_image_path(self):
        self.assertRaises(IOError, self.subreddit.upload_image, 'bar.png')

    def test_upload_jpg_header(self):
        self.betamax_init()
        image = self.image_path.format('white-square.jpg')
        self.assertTrue(self.subreddit.upload_image(image, header=True))

    def test_upload_jpg_image(self):
        self.betamax_init()
        image = self.image_path.format('white-square.jpg')
        self.assertTrue(self.subreddit.upload_image(image))

    # TODO: readd the following when we can handle the image uploads with
    # betamax.

# def test_upload_jpg_image_named(self):
#     self.betamax_init()
#     image = self.image_path.format('white-square.jpg')
#     name = text_type(self.r.modhash)
#     self.assertTrue(self.subreddit.upload_image(image, name))
#     images_json = self.subreddit.get_stylesheet()['images']
#     self.assertTrue(any(name in text_type(x['name']) for x in images_json))

# def test_upload_jpg_image_no_extension(self):
#     self.betamax_init()
#     image = self.image_path.format('white-square')
#     self.assertTrue(self.subreddit.upload_image(image))

# def test_upload_png_header(self):
#     self.betamax_init()
#     image = self.image_path.format('white-square.png')
#     self.assertTrue(self.subreddit.upload_image(image, header=True))

# def test_upload_png_image(self):
#     self.betamax_init()
#     image = self.image_path.format('white-square.png')
#     self.assertTrue(self.subreddit.upload_image(image))

# def test_upload_png_image_named(self):
#     self.betamax_init()
#     image = self.image_path.format('white-square.png')
#     name = text_type(self.r.modhash)
#     self.assertTrue(self.subreddit.upload_image(image, name))
#     images_json = self.subreddit.get_stylesheet()['images']
#     self.assertTrue(any(name in text_type(x['name']) for x in images_json))
