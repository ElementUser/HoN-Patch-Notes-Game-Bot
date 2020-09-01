import pytest
from hon_patch_notes_game_bot.user import RedditUser


@pytest.fixture
def reddit_user():
    """Initializes RedditUser object"""
    return RedditUser(
        id="1",
        name="Test Name",
        can_submit_guess=True,
        is_potential_winner=False,
        num_guesses=0,
    )


# ============
# Unit tests
# ============
def get_patch_notes_line_number(reddit_user):
    assert reddit_user.id == "1"


def test_user_name(reddit_user):
    assert reddit_user.name == "Test Name"


def test_user_can_submit_guess(reddit_user):
    assert reddit_user.can_submit_guess == True


def test_user_is_potential_winner(reddit_user):
    assert reddit_user.is_potential_winner == False


def test_user_num_guesses(reddit_user):
    assert reddit_user.num_guesses == 0
