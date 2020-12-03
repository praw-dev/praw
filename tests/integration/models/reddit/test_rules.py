from unittest import mock

import pytest

from praw.exceptions import ClientException, RedditAPIException
from praw.models import Rule

from ... import IntegrationTest


class TestRule(IntegrationTest):
    @property
    def subreddit(self):
        return self.reddit.subreddit(pytest.placeholders.test_subreddit)

    def test_add_rule(self):
        self.reddit.read_only = False
        with self.use_cassette():
            rule = self.subreddit.rules.mod.add(
                "PRAW Test",
                "all",
                description="Test by PRAW",
                violation_reason="PTest",
            )
        assert rule.short_name == "PRAW Test"
        assert rule.kind == "all"
        assert rule.description == "Test by PRAW"
        assert rule.violation_reason == "PTest"

    def test_add_rule_without_violation_reason(self):
        self.reddit.read_only = False
        with self.use_cassette():
            rule = self.subreddit.rules.mod.add("PRAW Test 2", "comment")
            assert rule.short_name == "PRAW Test 2"
            assert rule.kind == "comment"
            assert rule.description == ""
            assert rule.violation_reason == "PRAW Test 2"

    @mock.patch("time.sleep", return_value=None)
    def test_delete_rule(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            rules = list(self.subreddit.rules)
            rule = rules[-1]
            rule.mod.delete()
            assert len(list(self.subreddit.rules)) == (len(rules) - 1)

    def test_iter_rules(self):
        with self.use_cassette():
            for rule in self.subreddit.rules:
                assert isinstance(rule, Rule)

    @pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
    def test_iter_call(self):
        with self.use_cassette():
            assert self.subreddit.rules()["rules"][0]["short_name"] == "Test post 12"

    def test_iter_rule_string(self):
        with self.use_cassette("TestRule.test_iter_rules"):
            rule = self.subreddit.rules["PRAW Test"]
            assert isinstance(rule, Rule)
            rule._fetch()
            assert rule.kind

    def test_iter_rule_invalid(self):
        with self.use_cassette("TestRule.test_iter_rules"):
            rule = self.subreddit.rules["fake rule"]
            with pytest.raises(ClientException) as excinfo:
                rule.kind
            assert (
                excinfo.value.args[0]
                == f"Subreddit {self.subreddit} does not have the rule fake rule"
            )

    def test_iter_rule_int(self):
        with self.use_cassette("TestRule.test_iter_rules"):
            assert isinstance(self.subreddit.rules[0], Rule)

    def test_iter_rule_negative_int(self):
        with self.use_cassette("TestRule.test_iter_rules"):
            assert isinstance(self.subreddit.rules[-1], Rule)

    def test_iter_rule_slice(self):
        with self.use_cassette("TestRule.test_iter_rules"):
            rules = self.subreddit.rules[-3:]
            assert len(rules) == 3
            for rule in rules:
                assert isinstance(rule, Rule)

    @mock.patch("time.sleep", return_value=None)
    def test_reorder_rules(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            rule_list = list(self.subreddit.rules)
            reordered = rule_list[2:3] + rule_list[0:2] + rule_list[3:]
            rule_info = {rule.short_name: rule for rule in rule_list}
            self.subreddit.rules.mod.reorder(reordered)
            new_rules = list(self.subreddit.rules)
            assert new_rules != rule_list
            for rule in new_rules:
                assert rule_info[rule.short_name] == rule

    @mock.patch("time.sleep", return_value=None)
    def test_reorder_rules_double(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            rule_list = list(self.subreddit.rules)
            with pytest.raises(RedditAPIException):
                self.subreddit.rules.mod.reorder(rule_list + rule_list[0:1])

    @mock.patch("time.sleep", return_value=None)
    def test_reorder_rules_empty(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            with pytest.raises(RedditAPIException):
                self.subreddit.rules.mod.reorder([])

    @mock.patch("time.sleep", return_value=None)
    def test_reorder_rules_no_reorder(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            rule_list = list(self.subreddit.rules)
            assert self.subreddit.rules.mod.reorder(rule_list) == rule_list

    @mock.patch("time.sleep", return_value=None)
    def test_reorder_rules_omit(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            rule_list = list(self.subreddit.rules)
            with pytest.raises(RedditAPIException):
                self.subreddit.rules.mod.reorder(rule_list[:-1])

    @mock.patch("time.sleep", return_value=None)
    def test_update_rule(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            rule = self.subreddit.rules[0]
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

    @mock.patch("time.sleep", return_value=None)
    def test_update_rule_short_name(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            rule = self.subreddit.rules[1]
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
            for new_rule in self.subreddit.rules:
                assert new_rule.short_name != rule.short_name

    @mock.patch("time.sleep", return_value=None)
    def test_update_rule_no_params(self, _):
        self.reddit.read_only = False
        with self.use_cassette():
            rule = self.subreddit.rules[1]
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
