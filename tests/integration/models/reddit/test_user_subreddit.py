from tests.integration import IntegrationTest


class TestUserSubreddit(IntegrationTest):
    def test_update(self, reddit):
        reddit.read_only = False
        before_settings = reddit.user.me().subreddit.mod.settings()
        new_title = f"{before_settings['title']}x"
        new_title = (
            "x"
            if (len(new_title) >= 20 and "placeholder" not in new_title)
            else new_title
        )
        reddit.user.me().subreddit.mod.update(title=new_title)
        assert reddit.user.me(use_cache=False).subreddit.title == new_title
        after_settings = reddit.user.me().subreddit.mod.settings()

        # Ensure that nothing has changed besides what was specified.
        before_settings["title"] = new_title
        assert before_settings == after_settings
