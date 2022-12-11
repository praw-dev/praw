import pytest

from praw.exceptions import ClientException, RedditAPIException
from praw.models import Rule

from ... import IntegrationTest


class TestRule(IntegrationTest):
    def test_add_rule(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule = subreddit.rules.mod.add(
            short_name="PRAW Test",
            kind="all",
            description="Test by PRAW",
            violation_reason="PTest",
        )
        assert rule.short_name == "PRAW Test"
        assert rule.kind == "all"
        assert rule.description == "Test by PRAW"
        assert rule.violation_reason == "PTest"

    def test_add_rule_without_violation_reason(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule = subreddit.rules.mod.add(short_name="PRAW Test 2", kind="comment")
        assert rule.short_name == "PRAW Test 2"
        assert rule.kind == "comment"
        assert rule.description == ""
        assert rule.violation_reason == "PRAW Test 2"

    def test_delete_rule(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rules = list(subreddit.rules)
        rule = rules[-1]
        rule.mod.delete()
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        assert len(list(subreddit.rules)) == (len(rules) - 1)

    @pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
    def test_iter_call(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        assert subreddit.rules()["rules"][0]["short_name"] == "Test post 12"

    @pytest.mark.cassette_name("TestRule.test_iter_rules")
    def test_iter_rule_int(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        assert isinstance(subreddit.rules[0], Rule)

    @pytest.mark.cassette_name("TestRule.test_iter_rules")
    def test_iter_rule_invalid(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule = subreddit.rules["fake rule"]
        with pytest.raises(ClientException) as excinfo:
            rule.kind
        assert (
            excinfo.value.args[0]
            == f"Subreddit {subreddit} does not have the rule fake rule"
        )

    @pytest.mark.cassette_name("TestRule.test_iter_rules")
    def test_iter_rule_negative_int(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        assert isinstance(subreddit.rules[-1], Rule)

    @pytest.mark.cassette_name("TestRule.test_iter_rules")
    def test_iter_rule_slice(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rules = subreddit.rules[-3:]
        assert len(rules) == 3
        for rule in rules:
            assert isinstance(rule, Rule)

    @pytest.mark.cassette_name("TestRule.test_iter_rules")
    def test_iter_rule_string(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule = subreddit.rules["PRAW Test"]
        assert isinstance(rule, Rule)
        rule._fetch()
        assert rule.kind

    def test_iter_rules(self, reddit):
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for rule in subreddit.rules:
            assert isinstance(rule, Rule)

    def test_reorder_rules(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule_list = list(subreddit.rules)
        reordered = rule_list[2:3] + rule_list[0:2] + rule_list[3:]
        rule_info = {rule.short_name: rule for rule in rule_list}
        subreddit.rules.mod.reorder(reordered)
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        new_rules = list(subreddit.rules)
        assert new_rules != rule_list
        for rule in new_rules:
            assert rule_info[rule.short_name] == rule

    def test_reorder_rules_double(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule_list = list(subreddit.rules)
        with pytest.raises(RedditAPIException):
            subreddit.rules.mod.reorder(rule_list + rule_list[0:1])

    def test_reorder_rules_empty(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        with pytest.raises(RedditAPIException):
            subreddit.rules.mod.reorder([])

    def test_reorder_rules_no_reorder(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule_list = list(subreddit.rules)
        assert subreddit.rules.mod.reorder(rule_list) == rule_list

    def test_reorder_rules_omit(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule_list = list(subreddit.rules)
        with pytest.raises(RedditAPIException):
            subreddit.rules.mod.reorder(rule_list[:-1])

    def test_update_rule(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule = subreddit.rules[0]
        rule2 = rule.mod.update(
            description="Updated rule",
            kind="link",
            violation_reason="PUpdate",
        )
        assert rule.description != rule2.description
        assert rule2.description == "Updated rule"
        assert rule.kind != rule2.kind
        assert rule2.kind == "link"
        assert rule.violation_reason != rule2.violation_reason
        assert rule2.violation_reason == "PUpdate"

    def test_update_rule_no_params(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule = subreddit.rules[1]
        rule2 = rule.mod.update()
        for attr in (
            "created_utc",
            "description",
            "kind",
            "priority",
            "short_name",
            "subreddit",
            "violation_reason",
        ):
            assert getattr(rule, attr) == getattr(rule2, attr)

    def test_update_rule_short_name(self, reddit):
        reddit.read_only = False
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        rule = subreddit.rules[1]
        rule2 = rule.mod.update(
            short_name="PRAW Update",
            description="Updated rule",
            kind="comment",
            violation_reason="PUpdate",
        )
        assert rule != rule2
        assert rule2.short_name == "PRAW Update"
        assert rule.description != rule2.description
        assert rule2.description == "Updated rule"
        assert rule.kind != rule2.kind
        assert rule2.kind == "comment"
        assert rule.violation_reason != rule2.violation_reason
        assert rule2.violation_reason == "PUpdate"
        subreddit = reddit.subreddit(pytest.placeholders.test_subreddit)
        for new_rule in subreddit.rules:
            assert new_rule.short_name != rule.short_name
