from unittest.mock import Mock, patch
from praw.exceptions import RedditAPIException

from hon_patch_notes_game_bot import communications
from hon_patch_notes_game_bot.config.config import staff_recipients, gold_coin_reward


@patch("praw.Reddit")
def test_send_message_to_staff(mock_reddit: Mock):
    # Inner test function that is called multiple times
    def assert_test(mock_reddit):
        assert (
            communications.send_message_to_staff(
                mock_reddit,
                winners_list_path="./tests/cache/winners_list.txt",
                staff_recipients=staff_recipients,
                version_string="4.9.3",
                gold_coin_reward=gold_coin_reward,
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
def test_send_message_to_winners(mock_reddit: Mock):
    # Inner test function that is called multiple times
    def assert_test(mock_reddit):
        assert (
            communications.send_message_to_winners(
                mock_reddit,
                # 1 user so that we only sleep one time in exception testing
                winners_list=["User1"],
                version_string="4.9.3",
                gold_coin_reward=gold_coin_reward,
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
        ["RATELIMIT", "Please try again after 0.01 minutes", None], "Optional string",
    )
    assert_test(mock_reddit)

    mock_reddit.redditor.side_effect = Exception()
    assert_test(mock_reddit)