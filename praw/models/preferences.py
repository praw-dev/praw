"""Provide the Preferences class."""
from json import dumps
from typing import TYPE_CHECKING, Dict, Union

from ..const import API_PATH

if TYPE_CHECKING:  # pragma: no cover
    from .. import Reddit


class Preferences:
    """A class for Reddit preferences.

    The Preferences class provides access to the Reddit preferences of the
    currently authenticated user.
    """

    def __call__(self) -> Dict[str, Union[bool, int, str]]:
        """Return the preference settings of the authenticated user as a dict.

        This method is intended to be accessed as ``reddit.user.preferences()``
        like so:

        .. code-block:: python

           preferences = reddit.user.preferences()
           print(preferences["show_link_flair"])

        See https://www.reddit.com/dev/api#GET_api_v1_me_prefs for the list
        of possible values.
        """
        return self._reddit.get(API_PATH["preferences"])

    def __init__(self, reddit: "Reddit"):
        """Create a Preferences instance.

        :param reddit: The Reddit instance.
        """
        self._reddit = reddit

    def update(self, **preferences: Union[bool, int, str]):
        """Modify the specified settings.

        :param 3rd_party_data_personalized_ads: Allow Reddit to use data
            provided by third-parties to show you more relevant
            advertisements on Reddit (boolean).
        :param 3rd_party_site_data_personalized_ads: Allow personalization
            of advertisements using third-party website data (boolean).
        :param 3rd_party_site_data_personalized_content: Allow personalization
            of content using third-party website data (boolean).
        :param activity_relevant_ads: Allow Reddit to use your activity on
            Reddit to show you more relevant advertisements (boolean).
        :param allow_clicktracking: Allow Reddit to log my outbound clicks
            for personalization (boolean).
        :param beta: I would like to beta test features for Reddit (boolean).
        :param clickgadget: Show me links I've recently viewed (boolean).
        :param collapse_read_messages: Collapse messages after I've read
            them (boolean).
        :param compress: Compress the link display (boolean).
        :param creddit_autorenew: Use a creddit to automatically renew my
            gold if it expires (boolean).
        :param default_comment_sort: Default comment sort (one of
            ``"confidence"``, ``"top"``, ``"new"``, ``"controversial"``,
            ``"old"``, ``"random"``, ``"qa"``, ``"live"``).
        :param domain_details: Show additional details in the domain text
            when available, such as the source subreddit or the content
            author's url/name (boolean).
        :param email_digests: Send email digests (boolean).
        :param email_messages: Send messages as emails (boolean).
        :param email_unsubscribe_all: Unsubscribe from all emails (boolean).
        :param enable_default_themes: Use reddit theme (boolean).
        :param g: Location (one of ``"GLOBAL"``, ``"AR"``, ``"AU"``, ``"BG"``,
            ``"CA"``, ``"CL"``, ``"CO"``, ``"CZ"``, ``"FI"``, ``"GB"``,
            ``"GR"``, ``"HR"``, ``"HU"``, ``"IE"``, ``"IN"``, ``"IS"``,
            ``"JP"``, ``"MX"``, ``"MY"``, ``"NZ"``, ``"PH"``, ``"PL"``,
            ``"PR"``, ``"PT"``, ``"RO"``, ``"RS"``, ``"SE"``, ``"SG"``,
            ``"TH"``, ``"TR"``, ``"TW"``, ``"US"``, ``"US_AK"``, ``"US_AL"``,
            ``"US_AR"``, ``"US_AZ"``, ``"US_CA"``, ``"US_CO"``, ``"US_CT"``,
            ``"US_DC"``, ``"US_DE"``, ``"US_FL"``, ``"US_GA"``, ``"US_HI"``,
            ``"US_IA"``, ``"US_ID"``, ``"US_IL"``, ``"US_IN"``, ``"US_KS"``,
            ``"US_KY"``, ``"US_LA"``, ``"US_MA"``, ``"US_MD"``, ``"US_ME"``,
            ``"US_MI"``, ``"US_MN"``, ``"US_MO"``, ``"US_MS"``, ``"US_MT"``,
            ``"US_NC"``, ``"US_ND"``, ``"US_NE"``, ``"US_NH"``, ``"US_NJ"``,
            ``"US_NM"``, ``"US_NV"``, ``"US_NY"``, ``"US_OH"``, ``"US_OK"``,
            ``"US_OR"``, ``"US_PA"``, ``"US_RI"``, ``"US_SC"``, ``"US_SD"``,
            ``"US_TN"``, ``"US_TX"``, ``"US_UT"``, ``"US_VA"``, ``"US_VT"``,
            ``"US_WA"``, ``"US_WI"``, ``"US_WV"``, ``"US_WY"``).
        :param hide_ads: Hide ads (boolean).
        :param hide_downs: Don't show me submissions after I've downvoted them,
            except my own (boolean).
        :param hide_from_robots: Don't allow search engines to index my user
            profile (boolean).
        :param hide_locationbar: Hide location bar (boolean).
        :param hide_ups: Don't show me submissions after I've upvoted them,
            except my own (boolean).
        :param highlight_controversial: Show a dagger on comments voted
            controversial (boolean).
        :param highlight_new_comments: Highlight new comments (boolean).
        :param ignore_suggested_sort: Ignore suggested sorts (boolean).
        :param in_redesign_beta: In redesign beta (boolean).
        :param label_nsfw: Label posts that are not safe for work (boolean).
        :param lang: Interface language (IETF language tag, underscore
            separated).
        :param legacy_search: Show legacy search page (boolean).
        :param live_orangereds: Send message notifications in my browser
            (boolean).
        :param mark_messages_read: Mark messages as read when I open my inbox
            (boolean).
        :param media: Thumbnail preference (one of ``"on"``, ``"off"``,
            ``"subreddit"``).
        :param media_preview: Media preview preference (one of ``"on"``,
            ``"off"``, ``"subreddit"``).
        :param min_comment_score: Don't show me comments with a score less than
            this number (int between ``-100`` and ``100``).
        :param min_link_score: Don't show me submissions with a score less than
            this number (int between ``-100`` and ``100``).
        :param monitor_mentions: Notify me when people say my username
            (boolean).
        :param newwindow: Open links in a new window (boolean).
        :param no_profanity: Don't show thumbnails or media previews for
            anything labeled NSFW (boolean).
        :param no_video_autoplay: Don't autoplay Reddit videos on the
            desktop comments page (boolean).
        :param num_comments: Display this many comments by default (int
            between ``1`` and ``500``).
        :param numsites: Number of links to display at once (int between ``1``
            and ``100``).
        :param organic: Show the spotlight box on the home feed (boolean).
        :param other_theme: Subreddit theme to use (subreddit name).
        :param over_18: I am over eighteen years old and willing to view adult
            content (boolean).
        :param private_feeds: Enable private RSS feeds (boolean).
        :param profile_opt_out: View user profiles on desktop using legacy mode
            (boolean).
        :param public_votes: Make my votes public (boolean).
        :param research: Allow my data to be used for research purposes
            (boolean).
        :param search_include_over_18: Include not safe for work (NSFW)
            search results in searches (boolean).
        :param show_flair: Show user flair (boolean).
        :param show_gold_expiration: Show how much gold you have remaining
            on your userpage (boolean).
        :param show_link_flair: Show link flair (boolean).
        :param show_promote: Show promote (boolean).
        :param show_stylesheets: Allow subreddits to show me custom themes
            (boolean).
        :param show_trending: Show trending subreddits on the home feed
            (boolean).
        :param store_visits: Store visits (boolean)
        :param theme_selector: Theme selector (subreddit name).
        :param threaded_messages: Show message conversations in the inbox (
            boolean).
        :param threaded_modmail: Enable threaded modmail display (boolean).
        :param top_karma_subreddits: Top karma subreddits (boolean).
        :param use_global_defaults: Use global defaults (boolean).

        Additional keyword arguments can be provided to handle new settings as
        Reddit introduces them.

        See https://www.reddit.com/dev/api#PATCH_api_v1_me_prefs for the
        most up-to-date list of possible parameters.

        This is intended to be used like so:

        .. code-block:: python

           reddit.user.preferences.update(show_link_flair=True)

        This method returns the new state of the
        preferences as a ``dict``, which can be used to check whether a
        change went through.

        .. code-block:: python

           original_preferences = reddit.user.preferences()
           new_preferences = reddit.user.preferences.update(invalid_param=123)
           print(original_preferences == new_preferences)  # True, no change

        .. warning:: Passing an unknown parameter name or an illegal value
                     (such as an int when a boolean is expected) does not
                     result in an error from the Reddit API. As a consequence,
                     any invalid input will fail silently. To verify that
                     changes have been made, use the return value of this
                     method, which is a dict of the preferences after the
                     update action has been performed.

        Some preferences have names that are not valid keyword arguments in
        Python. To update these, construct a ``dict`` and use ``**`` to unpack
        it as keyword arguments:

        .. code-block:: python

           reddit.user.preferences.update(
                **{"3rd_party_data_personalized_ads": False})

        """
        return self._reddit.patch(
            API_PATH["preferences"], data={"json": dumps(preferences)}
        )
