"""PRAW constants."""

from .endpoints import API_PATH  # noqa: F401

__version__: str = "6.4.1.dev0"

USER_AGENT_FORMAT: str = "{} PRAW/" + __version__

MAX_IMAGE_SIZE: int = 512000
MIN_JPEG_SIZE: int = 128
MIN_PNG_SIZE: int = 67

JPEG_HEADER: bytes = b"\xff\xd8\xff"
PNG_HEADER: bytes = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
