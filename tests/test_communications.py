from unittest.mock import Mock, patch
from pytest import mark
from praw.exceptions import RedditAPIException

from hon_patch_notes_game_bot import communications
from hon_patch_notes_game_bot.config.config import (
    COMMUNITY_SUBMISSION_CONTENT_PATH,
    GOLD_COIN_REWARD,
    STAFF_RECIPIENTS_LIST,
    SUBMISSION_CONTENT_PATH,
)
from tests.test_database import database_path, Database


@patch("praw.Reddit")
def test_send_message_to_staff(mock_reddit: Mock):
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

    mock_reddit.redditor = Mock()
    mock_reddit.redditor.message.return_value = None

    # Regular use case
    assert_test(mock_reddit)

    # Exceptions
    mock_reddit.redditor.side_effect = RedditAPIException(
        ["Error type", "Error message", None], "Optional string",
    )
    assert_test(mock_reddit)

    mock_reddit.redditor.side_effect = Exception()
    assert_test(mock_reddit)


@patch("praw.Reddit")
@patch("time.sleep")  # This is mocked so the unit tests do not actually sleep
def test_send_message_to_winners(mock_reddit: Mock, sleep_func: Mock = Mock()):
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

    mock_reddit.redditor = Mock()
    mock_reddit.redditor.message.return_value = None

    # Regular use case
    assert_test(mock_reddit)

    # Exceptions
    mock_reddit.redditor.side_effect = RedditAPIException(
        ["RATELIMIT", "Error message", None], "Optional string",
    )
    assert_test(mock_reddit)

    mock_reddit.redditor.side_effect = RedditAPIException(
        ["RATELIMIT", "Please try again after 9 minutes", None], "Optional string",
    )
    assert_test(mock_reddit)

    mock_reddit.redditor.side_effect = Exception()
    assert_test(mock_reddit)


@patch("praw.Reddit")
@patch("praw.models.Subreddit")
@mark.usefixtures("get_patch_notes_file")
def test_init_submissions(
    mock_reddit: Mock, mock_subreddit: Mock, get_patch_notes_file
):
    database = Database(db_path=database_path)
    submission_content_path = f"./tests/{SUBMISSION_CONTENT_PATH}"
    community_submission_content_path = f"./tests/{COMMUNITY_SUBMISSION_CONTENT_PATH}"

    assert (
        communications.init_submissions(
            mock_reddit,
            mock_subreddit,
            database,
            get_patch_notes_file,
            submission_content_path,
            community_submission_content_path,
        )
        is not None
    )

