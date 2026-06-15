"""PRAW constants."""

from praw.endpoints import API_PATH  # noqa: F401

JPEG_HEADER = b"\xff\xd8\xff"

MAX_IMAGE_SIZE = 512000

MIN_JPEG_SIZE = 128
MIN_PNG_SIZE = 67
PNG_HEADER = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"

__version__ = "8.0.1"
USER_AGENT_FORMAT = f"{{}} PRAW/{__version__}"
