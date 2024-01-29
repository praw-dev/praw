"""Test praw.reddit."""

from base64 import urlsafe_b64encode

import pytest
from prawcore.exceptions import BadRequest

from praw.exceptions import RedditAPIException
from praw.models import LiveThread
from praw.models.reddit.base import RedditBase
from praw.models.reddit.submission import Submission
from praw.models.reddit.subreddit import Subreddit

from . import IntegrationTest


def comment_ids():
    with open("tests/integration/files/comment_ids.txt") as fp:
        return fp.read()[:8000]


def junk_data():
    with open("tests/integration/files/too_large.jpg", "rb") as fp:
        return urlsafe_b64encode(fp.read()).decode()


class TestDomainListing(IntegrationTest):
    def test_controversial(self, reddit):
        submissions = list(reddit.domain("youtube.com").controversial())
        assert len(submissions) == 100

    def test_hot(self, reddit):
        submissions = list(reddit.domain("youtube.com").hot())
        assert len(submissions) == 100

    def test_new(self, reddit):
        submissions = list(reddit.domain("youtube.com").new())
        assert len(submissions) == 100

    def test_random_rising(self, reddit):
        submissions = list(reddit.domain("youtube.com").random_rising())
        assert len(submissions) == 100

    def test_rising(self, reddit):
        list(reddit.domain("youtube.com").rising())

    def test_top(self, reddit):
        submissions = list(reddit.domain("youtube.com").top())
        assert len(submissions) == 100


class TestReddit(IntegrationTest):
    @pytest.mark.add_placeholder(comment_ids=comment_ids())
    def test_bad_request_without_json_text_html_response(self, reddit):
        with pytest.raises(RedditAPIException) as excinfo:
            reddit.request(
                method="GET",
                path=f"/api/morechildren?link_id=t3_n7r3uz&children={comment_ids()}",
            )
        assert (
            str(excinfo.value)
            == "<html><body><h1>400 Bad request</h1>\nYour browser sent an invalid "
            "request.\n</body></html>\n"
        )

    @pytest.mark.add_placeholder(content=junk_data())
    def test_bad_request_without_json_text_plain_response(self, reddit):
        with pytest.raises(RedditAPIException) as excinfo:
            reddit.request(
                method="GET",
                path=f"/api/morechildren?link_id=t3_n7r3uz&children={junk_data()}",
            )
        assert str(excinfo.value) == "Bad Request"

    def test_bare_badrequest(self, reddit):
        data = {
            "sr": "AskReddit",
            "field": "link",
            "kind": "link",
            "title": "l",
            "text": "lol",
            "show_error_list": True,
        }
        reddit.read_only = False
        with pytest.raises(BadRequest):
            reddit.post("/api/validate_submission_field", data=data)

    def test_info(self, reddit):
        bases = ["t1_d7ltv", "t3_5dec", "t5_2qk"]
        items = []
        for i in range(100):
            for base in bases:
                items.append(f"{base}{i:02d}")

        item_generator = reddit.info(fullnames=items)
        results = list(item_generator)
        assert len(results) > 100
        for item in results:
            assert isinstance(item, RedditBase)

    def test_info_sr_names(self, reddit):
        items = [reddit.subreddit("redditdev"), "reddit.com", "t:1337", "nl"]
        item_generator = reddit.info(subreddits=items)
        results = list(item_generator)
        assert len(results) == 4
        for item in results:
            assert isinstance(item, Subreddit)

    def test_info_url(self, reddit):
        results = list(reddit.info(url="youtube.com"))
        assert len(results) > 0
        for item in results:
            assert isinstance(item, Submission)

    def test_live_call(self, reddit):
        thread_id = "ukaeu1ik4sw5"
        thread = reddit.live(thread_id)
        assert thread.title == "reddit updates"

    def test_live_create(self, reddit):
        reddit.read_only = False
        live = reddit.live.create("PRAW Create Test")
        assert isinstance(live, LiveThread)
        assert live.title == "PRAW Create Test"

    def test_live_info(self, reddit):
        ids = """
        ta40aifzobnv ta40l9u2ermf ta40ucdiq366 ta416hjgvbhy ta41ln5vsyaz
        ta42cyzy1nze ta42i49806k0 ta436ojd653m ta43945wgmaa ta43znjvza9t
        ta4418kxie3z ta44mk0nllhm ta45j0yvww9t ta4613lzdh8q ta46l8k86jt9
        ta47qua0xu3n ta489fm9515p ta48ml5k1uk9 ta48zy4jzjcb ta49irvwndau
        ta49upckgoyw ta4a02h9ynsb ta4aa4lrgvst ta4alauoi8ws ta4aqyacr70u

        ta4ekdk6m5g2 ta4ezvoc49gy ta4f3iv06c1n ta4ffvliq5l7 ta4fib9lx3zx
        ta4gka0ll41h ta4h89f6isfg ta4ht7s8he49 ta4i1eb564ar ta4imxhap4fg
        ta4iu3g9whtk ta4j3o05j0d3 ta4kloqi6csg ta4m6kj44dql ta4mlqtihiil
        ta4ng30l3fz1 ta4nldsjimhu ta4pd78tuk29 ta4prwyy1w9i ta4pvu8y6f8o
        ta4ray2odqub ta4rua4oe6a1 ta4tk9fwjgz1 ta4trgqw6mmx ta4tv3sen7u4

        ta4uyh0fnc0a ta4v54gnggcl ta4v5cm004z1 ta4vortaefna ta4wqym9d0v3
        ta4wsuouxjtm ta4x7jr9v0fn ta4yast5e96b ta4z337yzlgu ta4zo9zzo9ui
        ta507u2euo3w ta50exn0mtx1 ta51x2crezff ta52ch48gn6l ta53ijowvc6z
        ta53iy196uod ta541cz1hfb4 ta54n0ncx8pc ta55ytfmre2g ta581bybyjwi
        ta59gcidn2ym ta59mkwnrd43 ta5ar22wzi2w ta5awwo42ibb ta5dhmvylw0l

        ta5hipd6wahr ta5itb7clg3s ta5nlm09y8kb ta5nm0f831x1 ta5oavbflorf
        ta5rnv18s85o ta5ru6ysh254 ta5sfz02nc8b ta5syawj086b ta5t41osygln
        ta5uy3ynoo4a ta5w0seb1xfy ta5wddbh0ln0 ta5zmjzuijwo ta617ozbmxhb
        ta64q6pjz2bs ta696fdie4ne ta6bmog7gvoq ta6f9y7sdzru ta6j838d2wjn
        ta6l4q5c17fd ta6ofypk3yp2 ta6sjmjt1aeb ta6sqhgyv41q ta70eezhz50r

        ta72azs1l4u9 ta74r3dp2pt5 ta7pfcqdx9cl ta8zxbt2sk6z ta94nde51q4i
        """.split()
        gen = reddit.live.info(ids)
        threads = list(gen)
        assert len(threads) > 100
        assert all(isinstance(thread, LiveThread) for thread in threads)
        # output may not reflect input order
        thread_ids = [thread.id for thread in threads]
        assert thread_ids != ids
        assert sorted(thread_ids) == ids

    def test_live_info__contain_invalid_id(self, reddit):
        ids = [
            "3rgnbke2rai6hen7ciytwcxadi",
            "LiveUpdateEvent_sw7bubeycai6hey4ciytwamw3a",  # invalid
            "t8jnufucss07",
        ]  # NBA
        gen = reddit.live.info(ids)
        threads = list(gen)
        assert len(threads) == 2

    def test_live_now__featured(self, reddit):
        thread = reddit.live.now()
        assert isinstance(thread, LiveThread)
        assert thread.id == "z2f981agq7ky"

    def test_live_now__no_featured(self, reddit):
        assert reddit.live.now() is None

    def test_notes__call__(self, reddit):
        reddit.read_only = False
        notes = list(
            reddit.notes(
                pairs=[
                    (reddit.subreddit("SubTestBot1"), "Watchful1"),
                    ("SubTestBot1", reddit.redditor("watchful12")),
                    ("SubTestBot1", "spez"),
                ],
                things=[reddit.submission("jlbw48")],
            )
        )
        assert len(notes) == 4
        assert notes[0].user.name.lower() == "watchful1"
        assert notes[1].user.name.lower() == "watchful12"
        assert notes[2] is None

    def test_notes__things(self, reddit):
        reddit.read_only = False
        thing = reddit.submission("tpbemz")
        notes = list(reddit.notes.things(thing))
        assert len(notes) == 10
        assert notes[0].user == thing.author

    def test_random_subreddit(self, reddit):
        names = set()
        for i in range(3):
            names.add(reddit.random_subreddit().display_name)
        assert len(names) == 3

    def test_subreddit_with_randnsfw(self, reddit):
        subreddit = reddit.subreddit("randnsfw")
        assert subreddit.display_name != "randnsfw"
        assert subreddit.over18

    def test_subreddit_with_random(self, reddit):
        assert reddit.subreddit("random").display_name != "random"

    @pytest.mark.add_placeholder(AVAILABLE_NAME="prawtestuserabcd1234")
    def test_username_available__available(self, reddit):
        assert reddit.username_available("prawtestuserabcd1234")

    def test_username_available__unavailable(self, reddit):
        assert not reddit.username_available("bboe")

    def test_username_available_exception(self, reddit):
        with pytest.raises(RedditAPIException) as exc:
            reddit.username_available("a")
        assert str(exc.value) == "BAD_USERNAME: 'invalid user name' on field 'user'"
