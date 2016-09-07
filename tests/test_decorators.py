from __future__ import print_function, unicode_literals

from .helper import OAuthPRAWTest, betamax
from .mock_response import MockResponse
from praw import errors
from praw.decorator_helpers import _make_func_args
from praw.decorators import restrict_access
from praw.internal import _modify_relationship
from six import text_type


class DecoratorTest(OAuthPRAWTest):
    def test_require_access_failure(self):
        self.assertRaises(TypeError, restrict_access, scope=None,
                          oauth_only=True)

    def test_make_func_args(self):
        def foo(arg1, arg2, arg3):
            pass

        def bar(arg1, arg2, arg3, *args, **kwargs):
            pass

        arglist = ['arg1', 'arg2', 'arg3']

        self.assertEqual(_make_func_args(foo), arglist)
        self.assertEqual(_make_func_args(bar), arglist)

    def test_restrict_access_permission_errors(self):
        # PRAW doesn't currently use _modify_relationship for friending but
        # this same check might be needed in the future, so, lets use this to
        # our advantage, temporarily bind a custom unfriend function, ensure
        # the proper error is raised, and then, unbind this function.
        redditor = self.r.get_redditor(self.un)
        redditor.temp_make_friend = _modify_relationship('friend')
        self.assertRaises(errors.LoginRequired, redditor.temp_make_friend,
                          thing=None, user=self.other_user_name)
        del redditor.temp_make_friend

        # PRAW doesn't currently use restrict_access for mod duties without
        # setting a scope but this might be needed in the future, so, lets use
        # _modify_relationship  to our advantage, temporarily bind a custom
        # nonsense function, ensure the proper error is raised, and then,
        # unbind this function. This can also be used to detect the
        # ModeratorRequired exception from restrict_access as PRAW doesn't have
        # any functions that would ordinarily end in this outcome, as all
        # moderator reddit endpoints are oauth compatible.
        subreddit = self.r.get_subreddit(self.sr)
        type(subreddit).temp_nonsense = _modify_relationship('nonsense')
        self.assertRaises(errors.LoginRequired,
                          subreddit.temp_nonsense, user=self.un)
        self.r.login(self.other_non_mod_name, self.other_non_mod_pswd,
                     disable_warning=True)
        subreddit = self.r.get_subreddit(self.sr)
        self.assertRaises(errors.ModeratorRequired,
                          subreddit.temp_nonsense, user=self.un)
        del type(subreddit).temp_nonsense

        # PRAW doesn't currently have a method in which the subreddit
        # is taken from function defaults, so, let's write one instead
        @restrict_access(mod=True, scope=None)
        def fake_func(obj, **kwargs):
            return None
        type(self.r).fake_func = fake_func
        self.assertRaises(errors.ModeratorRequired, self.r.fake_func)
        del type(self.r).fake_func

    @betamax()
    def test_error_list(self):
        # use the other account to get a InvalidCaptcha
        self.r.refresh_access_information(self.other_refresh_token['submit'])
        # implicitly tests the RateLimitExceeded Exception as well
        err_list = self.assertExceptionList(
            [errors.InvalidCaptcha, errors.RateLimitExceeded], self.r.submit,
            self.sr, "test ratelimit error 1", 'ratelimit error test call 1')
        captcha_err, ratelimit_err = err_list.errors
        self.assertEqual('`{0}` on field `{1}`'.format(captcha_err.message,
                                                       captcha_err.field),
                         str(captcha_err))
        self.assertEqual('`{0}` on field `{1}`'.format(ratelimit_err.message,
                                                       ratelimit_err.field),
                         str(ratelimit_err))
        expected_list_str = '\n' + "".join(
            '\tError {0}) {1}\n'.format(i, text_type(error))
            for i, error in enumerate(err_list.errors))
        self.assertEqual(expected_list_str, str(err_list))

    @betamax()
    def test_limit_chars(self):
        self.r.refresh_access_information(self.refresh_token['read'])
        submission = self.r.get_submission(
            submission_id=self.submission_limit_chars_id)
        before_limit = text_type(
            '{0} :: {1}').format(
            submission.score,
            submission.title.replace('\r\n', ' '))
        expected = before_limit[:self.r.config.output_chars_limit - 3]
        expected += '...'
        self.assertEqual(str(submission), expected)
        self.assertLess(str(submission), before_limit)

    @betamax()
    def test_raise_nonspecific_apiexception(self):
        self.r.refresh_access_information(self.refresh_token['submit'])
        err = self.assertRaisesAndReturn(errors.APIException,
                                         self.r.submit, self.sr,
                                         "".join("0" for i in range(301)),
                                         "BODY")
        self.assertEqual('({0}) `{1}` on field `{2}`'.format(err.error_type,
                                                             err.message,
                                                             err.field),
                         str(err))

    @betamax(pass_recorder=True)
    def test_raise_not_modified(self, recorder):
        self.r.refresh_access_information(self.refresh_token['read'])
        with MockResponse.as_context(
                recorder.current_cassette.interactions[-1], status_code=304,
                reason="Not Modified", json={'error': 304},
                headers={"Content-Length": 1}):
            err = self.assertRaisesAndReturn(
                errors.NotModified, list, self.r.get_subreddit(
                    self.sr).get_new(limit=25))
        self.assertEqual(str(err), 'That page has not been modified.')
