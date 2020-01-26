"""PRAW constants."""
from .endpoints import API_PATH  # noqa: F401

__version__ = "6.6.0.dev0"

USER_AGENT_FORMAT = "{} PRAW/" + __version__

MAX_IMAGE_SIZE = 512000
MIN_JPEG_SIZE = 128
MIN_PNG_SIZE = 67

JPEG_HEADER = b"\xff\xd8\xff"
PNG_HEADER = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
