"""praw constants."""

from .endpoints import API_PATH

__version__ = "6.1.2.dev0"

JPEG_HEADER = b"\xff\xd8\xff"
MAX_IMAGE_SIZE = 512000
MIN_PNG_SIZE = 67
MIN_JPEG_SIZE = 128
PNG_HEADER = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"

USER_AGENT_FORMAT = "{{}} PRAW/{}".format(__version__)
