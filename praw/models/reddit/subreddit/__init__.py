"""Provide the :class:`.Subreddit` class and its helper classes."""

from __future__ import annotations

from praw.models.reddit.subreddit.filters import SubredditFilters
from praw.models.reddit.subreddit.flair import (
    SubredditFlair,
    SubredditFlairTemplates,
    SubredditLinkFlairTemplates,
    SubredditRedditorFlairTemplates,
)
from praw.models.reddit.subreddit.moderation import (
    SubredditModeration,
    SubredditModerationStream,
)
from praw.models.reddit.subreddit.modmail import Modmail
from praw.models.reddit.subreddit.quarantine import SubredditQuarantine
from praw.models.reddit.subreddit.relationship import (
    ContributorRelationship,
    ModeratorRelationship,
    SubredditRelationship,
)
from praw.models.reddit.subreddit.stream import SubredditStream
from praw.models.reddit.subreddit.stylesheet import SubredditStylesheet
from praw.models.reddit.subreddit.subreddit import Subreddit
from praw.models.reddit.subreddit.wiki import SubredditWiki

__all__ = [
    "ContributorRelationship",
    "ModeratorRelationship",
    "Modmail",
    "Subreddit",
    "SubredditFilters",
    "SubredditFlair",
    "SubredditFlairTemplates",
    "SubredditLinkFlairTemplates",
    "SubredditModeration",
    "SubredditModerationStream",
    "SubredditQuarantine",
    "SubredditRedditorFlairTemplates",
    "SubredditRelationship",
    "SubredditStream",
    "SubredditStylesheet",
    "SubredditWiki",
]
