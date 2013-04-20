# This file is part of PRAW.
#
# PRAW is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PRAW is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PRAW.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable-msg=W0611

import os
import pytest
import sys
import uuid

from six import text_type

from praw import errors
from praw.tests.helper import configure, R, reddit_only, SUBREDDIT  # NOQA


TEST_DIR = os.path.dirname(sys.modules[__name__].__file__)
IMAGE_PATH = os.path.join(TEST_DIR, 'files', '{0}')


def setup_function(function):  # pylint: disable-msg=W0613
    configure()


def test_delete_header():
    SUBREDDIT.delete_image(header=True)


def test_delete_image():
    images = SUBREDDIT.get_stylesheet()['images']
    for img_data in images[5:]:
        SUBREDDIT.delete_image(name=img_data['name'])
    updated_images = SUBREDDIT.get_stylesheet()['images']
    assert images != updated_images


def test_delete_invalid_image():
    # TODO: Patch reddit to return error when this fails
    SUBREDDIT.delete_image(name='invalid_image_name')


def test_delete_invalid_params():
    with pytest.raises(TypeError):  # pylint: disable-msg=E1101
        SUBREDDIT.delete_image(name='Foo', header=True)


def test_upload_invalid_file_path():
    with pytest.raises(IOError):  # pylint: disable-msg=E1101
        SUBREDDIT.upload_image('nonexistent')


def test_upload_uerinvalid_image():
    image = IMAGE_PATH.format('white-square.tiff')
    with pytest.raises(errors.ClientException):  # pylint: disable-msg=E1101
        SUBREDDIT.upload_image(image)


def test_upload_invalid_image_too_small():
    image = IMAGE_PATH.format('invalid.jpg')
    with pytest.raises(errors.ClientException):  # pylint: disable-msg=E1101
        SUBREDDIT.upload_image(image)


def test_upload_invalid_image_too_large():
    image = IMAGE_PATH.format('big')
    with pytest.raises(errors.ClientException):  # pylint: disable-msg=E1101
        SUBREDDIT.upload_image(image)


def test_upload_invalid_params():
    image = IMAGE_PATH.format('white-square.jpg')
    with pytest.raises(TypeError):  # pylint: disable-msg=E1101
        SUBREDDIT.upload_image(image, name='Foo', header=True)


def test_upload_invalid_image_path():
    with pytest.raises(IOError):  # pylint: disable-msg=E1101
        SUBREDDIT.upload_image('bar.png')


@reddit_only
def test_upload_jpg_header():
    image = IMAGE_PATH.format('white-square.jpg')
    assert SUBREDDIT.upload_image(image, header=True)


@reddit_only
def test_upload_jpg_image():
    image = IMAGE_PATH.format('white-square.jpg')
    assert SUBREDDIT.upload_image(image)


@reddit_only
def test_upload_jpg_image_named():
    image = IMAGE_PATH.format('white-square.jpg')
    name = text_type(uuid.uuid4())
    assert SUBREDDIT.upload_image(image, name)
    images_json = SUBREDDIT.get_stylesheet()['images']
    assert any(name in text_type(x['name']) for x in images_json)


@reddit_only
def test_upload_jpg_image_no_extension():
    image = IMAGE_PATH.format('white-square')
    assert SUBREDDIT.upload_image(image)


@reddit_only
def test_upload_png_header():
    image = IMAGE_PATH.format('white-square.png')
    assert SUBREDDIT.upload_image(image, header=True)


@reddit_only
def test_upload_png_image():
    image = IMAGE_PATH.format('white-square.png')
    assert SUBREDDIT.upload_image(image)


@reddit_only
def test_upload_png_image_named():
    image = IMAGE_PATH.format('white-square.png')
    name = text_type(uuid.uuid4())
    assert SUBREDDIT.upload_image(image, name)
    images_json = SUBREDDIT.get_stylesheet()['images']
    assert any(name in text_type(x['name']) for x in images_json)
