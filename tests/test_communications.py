from unittest.mock import Mock, patch
from unittest import TestCase
from pytest import mark
from praw.exceptions import RedditAPIException

from hon_patch_notes_game_bot import communications
from hon_patch_notes_game_bot.config.config import (
    COMMUNITY_SUBMISSION_CONTENT_PATH,
    GOLD_COIN_REWARD,
    STAFF_RECIPIENTS_LIST,
    SUBMISSION_CONTENT_PATH,
)


@mark.usefixtures(
    "get_patch_notes_file_class_fixture", "setup_and_teardown_test_database"
)
class TestCommunications(TestCase):
    def setUp(self):
        self.mock_reddit = patch("praw.Reddit")
        self.mock_subreddit = patch("praw.models.Subreddit")
        self.mock_submission = patch("praw.models.Submission")
        self.mock_community_submission = patch("praw.models.Submission")

    def test_send_message_to_staff(self):
        # Inner test function that is called multiple times
        def assert_test(mock_reddit):
            assert (
                communications.send_message_to_staff(
                    mock_reddit,
                    winners_list_path="./tests/cache/winners_list.txt",
                    staff_recipients=STAFF_RECIPIENTS_LIST,
                    version_string="4.9.3",
                    gold_coin_reward=GOLD_COIN_REWARD,
                )
                is None
            )

        self.mock_reddit.redditor = Mock()
        self.mock_reddit.redditor.message.return_value = None

        # Regular use case
        assert_test(self.mock_reddit)

        # Exceptions
        self.mock_reddit.redditor.side_effect = RedditAPIException(
            ["Error type", "Error message", None], "Optional string",
        )
        assert_test(self.mock_reddit)

        self.mock_reddit.redditor.side_effect = Exception()
        assert_test(self.mock_reddit)

    @patch("time.sleep")  # This is mocked so the unit tests do not actually sleep
    def test_send_message_to_winners(self, sleep_func: Mock = Mock()):
        # Inner test function that is called multiple times
        def assert_test(mock_reddit):
            assert (
                communications.send_message_to_winners(
                    mock_reddit,
                    winners_list=["User1", "User2"],
                    version_string="4.9.3",
                    gold_coin_reward=GOLD_COIN_REWARD,
                )
                is None
            )

        self.mock_reddit.redditor = Mock()
        self.mock_reddit.redditor.message.return_value = None

        # Regular use case
        assert_test(self.mock_reddit)

        # Exceptions
        self.mock_reddit.redditor.side_effect = RedditAPIException(
            ["RATELIMIT", "Error message", None], "Optional string",
        )
        assert_test(self.mock_reddit)

        self.mock_reddit.redditor.side_effect = RedditAPIException(
            ["RATELIMIT", "Please try again after 9 minutes", None], "Optional string",
        )
        assert_test(self.mock_reddit)

        self.mock_reddit.redditor.side_effect = Exception()
        assert_test(self.mock_reddit)

    def test_init_submissions(self):
        submission_content_path = f"./tests/{SUBMISSION_CONTENT_PATH}"
        community_submission_content_path = (
            f"./tests/{COMMUNITY_SUBMISSION_CONTENT_PATH}"
        )
        self.mock_reddit.submission = Mock()

        assert (
            communications.init_submissions(
                self.mock_reddit,
                self.mock_subreddit,
                self._database,
                self._patch_notes_file,
                submission_content_path,
                community_submission_content_path,
            )
            is not None
        )

