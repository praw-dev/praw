"""This file should be updated as files/classes/functions are deprecated."""

import pytest

from praw.exceptions import APIException

from . import UnitTest


@pytest.mark.filterwarnings("error", category=DeprecationWarning)
class TestDeprecation(UnitTest):
    def test_validate_on_submit(self):
        with pytest.raises(DeprecationWarning):
            self.reddit.validate_on_submit
        self.reddit.validate_on_submit = True
        assert self.reddit.validate_on_submit
        self.reddit.validate_on_submit = False
        with pytest.raises(DeprecationWarning):
            self.reddit.validate_on_submit

    def test_api_exception(self):
        exc = APIException(["test", "testing", "test"])
        with pytest.raises(DeprecationWarning):
            exc.error_type
        with pytest.raises(DeprecationWarning):
            exc.message
        with pytest.raises(DeprecationWarning):
            exc.field

    def test_subreddit_rules_call(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").rules()
        assert (
            excinfo.value.args[0]
            == "Calling SubredditRules to get a list of rules is deprecated. "
            "Remove the parentheses to use the iterator. View the "
            "PRAW documentation on how to change the code in order to use the"
            "iterator (https://praw.readthedocs.io/en/latest/code_overview"
            "/other/subredditrules.html#praw.models.reddit.rules."
            "SubredditRules.__call__)."
        )

    def test_SubredditWidgetsModeration_add_button_widget_buttons_dict(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_button_widget(
                "test", "test", [{}], None
            )
        assert (
            excinfo.value.args[0]
            == "Providing a list of dictionaries for the ``buttons`` "
            "parameter is deprecated. Please replace the dictionary with "
            "a call to widgets.mod.generate_button. See the documentation "
            "for the add_button_widget method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.add_button_widget on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_add_button_widget_styles_dict(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_button_widget(
                "test", "test", [None], {}
            )
        assert (
            excinfo.value.args[0]
            == "Providing a dictionary for the ``styles`` parameter is "
            "deprecated. Please replace the dictionary with a call to "
            "widgets.mod.generate_styles. See the documentation for the "
            "generate_styles method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.generate_styles on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_add_calendar_configuration_dict(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_calendar(
                "test", "test", True, {}, None
            )
        assert (
            excinfo.value.args[0]
            == "Providing a dictionary for the ``configuration`` parameter "
            "is deprecated. Please replace the dictionary with a call to "
            "widgets.mod.generate_calendar_configuration. See the "
            "documentation for the add_calendar method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.add_calendar on how to port code."
        )

    def test_SubredditWidgetsModeration_add_calendar_styles_dict(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_calendar(
                "test", "test", True, None, {}
            )
        assert (
            excinfo.value.args[0]
            == "Providing a dictionary for the ``styles`` parameter is "
            "deprecated. Please replace the dictionary with a call to "
            "widgets.mod.generate_styles. See the documentation for the "
            "generate_styles method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.generate_styles on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_add_community_list_styles_dict(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_community_list(
                None, None, {}, None
            )
        assert (
            excinfo.value.args[0]
            == "Providing a dictionary for the ``styles`` parameter is "
            "deprecated. Please replace the dictionary with a call to "
            "widgets.mod.generate_styles. See the documentation for the "
            "generate_styles method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.generate_styles on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_add_custom_widget_image_data_dict(
        self,
    ):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_custom_widget(
                None, None, None, None, [{}], None
            )
        assert (
            excinfo.value.args[0]
            == "Providing a list of dictionaries for the ``image_data`` "
            "parameter is deprecated. Please replace the dictionaries "
            "with calls to widgets.mod.generate_image_data. See the "
            "documentation for the add_custom_widget method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.add_custom_widget on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_add_custom_widget_styles_dict(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_custom_widget(
                None, None, None, None, [None], {}
            )
        assert (
            excinfo.value.args[0]
            == "Providing a dictionary for the ``styles`` parameter is "
            "deprecated. Please replace the dictionary with a call to "
            "widgets.mod.generate_styles. See the documentation for the "
            "generate_styles method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.generate_styles on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_add_image_widget_data_dict(self,):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_image_widget(
                None, [{}], None
            )
        assert (
            excinfo.value.args[0]
            == "Providing a list of dictionaries for the ``data`` "
            "parameter is deprecated. Please replace the dictionaries "
            "with calls to widgets.mod.generate_image. See the "
            "documentation for the add_image_widget method at "
            "https://praw.readthedocs.io/en/latest/code_overview"
            "/other/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.add_image_widget on how to "
            "port code."
        )

    def test_SubredditWidgetsModeration_add_image_widget_styles_dict(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_image_widget(
                None, [None], {}
            )
        assert (
            excinfo.value.args[0]
            == "Providing a dictionary for the ``styles`` parameter is "
            "deprecated. Please replace the dictionary with a call to "
            "widgets.mod.generate_styles. See the documentation for the "
            "generate_styles method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.generate_styles on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_add_menu_data_dict(self,):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_menu([{}])
        assert (
            excinfo.value.args[0]
            == "Providing a list of dictionaries for the ``data`` "
            "parameter is deprecated. Please replace the "
            "dictionaries with calls to "
            "widgets.mod.generate_menu_link and "
            "widgets.mod.generate_submenu. See the documentation for "
            "the add_menu method at "
            "https://praw.readthedocs.io/en/latest/code_overview"
            "/other/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.add_menu on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_add_post_flair_widget_styles_dict(
        self,
    ):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_post_flair_widget(
                None, None, [None], {}
            )
        assert (
            excinfo.value.args[0]
            == "Providing a dictionary for the ``styles`` parameter is "
            "deprecated. Please replace the dictionary with a call to "
            "widgets.mod.generate_styles. See the documentation for the "
            "generate_styles method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.generate_styles on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_add_text_area_styles_dict(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.add_text_area(
                None, None, {}
            )
        assert (
            excinfo.value.args[0]
            == "Providing a dictionary for the ``styles`` parameter is "
            "deprecated. Please replace the dictionary with a call to "
            "widgets.mod.generate_styles. See the documentation for the "
            "generate_styles method at "
            "https://praw.readthedocs.io/en/latest/code_overview/other"
            "/subredditwidgetsmoderation.html#praw.models"
            ".SubredditWidgetsModeration.generate_styles on how to port "
            "code."
        )

    def test_SubredditWidgetsModeration_agenerate_button_hoverState_dict(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddit("test").widgets.mod.generate_button(
                None, None, None, hoverState={}
            )
        assert (
            excinfo.value.args[0]
            == "Providing a dictionary for parameter ``hoverState`` is "
            "deprecated. Please provide an instance of the Hover "
            "class, which can be generated by the generate_hover"
            " method. See the documentation for the add_button_widget "
            "method at https://praw.readthedocs.io/en/latest/"
            "code_overview/other/subredditwidgetsmoderation.html#praw"
            ".models.SubredditWidgetsModeration.add_button_widget on "
            "how to port code."
        )
