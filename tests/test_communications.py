from unittest import mock
from hon_patch_notes_game_bot import communications
from hon_patch_notes_game_bot.config.config import staff_recipients, gold_coin_reward

# This file currently has no tests,
#   as the 'communications' module largely relies on API calls from other libraries (e.g. praw).


@mock.patch("praw.Reddit")
def test_send_message_to_staff(mock_reddit: mock.Mock):
    mock_reddit.redditor = mock.Mock()
    mock_reddit.redditor.message.return_value = None

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
