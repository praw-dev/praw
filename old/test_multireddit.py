"""Tests for Multireddit class."""

from praw import errors, objects
from .helper import PRAWTest, betamax


class MultiredditTest(PRAWTest):

    def betamax_init(self):
        self.r.login(self.un, self.un_pswd, disable_warning=True)

    def test_multireddit_representations(self):
        multi = objects.Multireddit(self.r, author='Foo', name='Bar')
        self.assertEqual("Multireddit(author='Foo', name='Bar')", repr(multi))
        self.assertEqual('Bar', str(multi))

    @betamax()
    def test_add_and_remove_subreddit(self):
        multi = self.r.user.get_multireddits()[0]
        self.assertTrue(self.sr in (x.display_name for x in multi.subreddits))
        multi.remove_subreddit(self.sr)
        multi.refresh()

        self.assertFalse(self.sr in (x.display_name for x in multi.subreddits))
        multi.add_subreddit(self.sr)
        multi.refresh()
        self.assertTrue(self.sr in (x.display_name for x in multi.subreddits))

    @betamax()
    def test_create_and_delete_multireddit(self):
        name = 'PRAW_{0}'.format(self.r.modhash)[:15]
        multi = self.r.create_multireddit(name)
        self.assertEqual(name.lower(), multi.name.lower())
        self.assertEqual([], multi.subreddits)

        multi.delete()
        self.assertRaises(errors.NotFound, multi.refresh)

    @betamax()
    def test_copy_multireddit(self):
        name = 'praw_{0}'.format(self.r.modhash)[:15]
        multi = self.r.user.get_multireddits()[0]
        new_multi = multi.copy(name)
        self.assertNotEqual(multi.name, new_multi.name)
        self.assertEqual(multi.path, new_multi.copied_from)
        self.assertEqual(name, new_multi.name)
        self.assertEqual(multi.subreddits, new_multi.subreddits)

    @betamax()
    def test_edit_multireddit(self):
        name = 'PRAW_{0}'.format(self.r.modhash)[:15]
        multi = self.r.user.get_multireddits()[0]
        self.assertNotEqual(name, multi.description_md)
        self.assertEqual(name, multi.edit(description_md=name).description_md)
        self.assertEqual(name, multi.refresh().description_md)

    @betamax()
    def test_get_multireddit(self):
        multi = self.r.user.get_multireddit('publicempty')
        self.assertEqual('/user/{0}/m/{1}'.format(self.un, 'publicempty'),
                         multi.path)

    @betamax()
    def test_multireddit_get_new(self):
        multi = self.r.user.get_multireddit('publicempty')
        self.assertEqual([], list(multi.get_new()))
