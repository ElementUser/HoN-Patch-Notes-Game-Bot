import pytest
import copy
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.user import RedditUser
from tinydb import Query

database_path = "./tests/cache/db_test.json"


@pytest.fixture
def database():
    """Initializes patch notes file object"""
    return Database(db_path=database_path)


# ============
# Unit tests
# ============
def test_insert_submission_url(database):
    url_string = "http://test_url.com"
    database.insert_submission_url(tag="test_entry", submission_url=url_string)
    assert database.db.table("submission").search(Query().url == url_string)
    # Remove entry from database afterwards
    database.db.table("submission").remove(Query().url == url_string)


def test_get_submission_url(database):
    url_string = "https://www.reddit.com/r/HeroesofNewerth/comments/in14hz/game_486_patch_notes_guessing_game/"
    assert database.get_submission_url(tag="main") == url_string


def test_user_exists(database):
    assert database.user_exists("S2Sliferjam")
    assert not database.user_exists(
        "random_user_that_doesnt_exist_89213u893u13u132u139u31983u13dasdadsadsa"
    )


def test_get_user(database):
    assert database.get_user("S2Sliferjam")


def test_add_user(database):
    username = "random_user_that_temporarily_exists_213123asd"
    user = RedditUser(name=username)
    database.add_user(user)
    assert database.user_exists(username)
    # Remove entry from database afterwards
    database.db.table("user").remove(Query().name == username)


def test_convert_db_user_to_RedditUser(database):
    db_user = database.get_user("S2Sliferjam")
    reddit_user = database.convert_db_user_to_RedditUser(db_user)

    # Cannot iterate over an object's attributes directly,
    # but can make a dictionary of their attributes via vars()
    reddit_user_attributes = vars(reddit_user)

    for key in db_user:
        assert db_user[key] == reddit_user_attributes[key]


def test_update_user(database):
    updated_num_guesses = 1000
    db_user = database.get_user("S2Sliferjam")
    reddit_user = database.convert_db_user_to_RedditUser(db_user)

    # Save original user data
    original_reddit_user = copy.deepcopy(reddit_user)

    # Change the num_guesses field & test that
    reddit_user.num_guesses = updated_num_guesses
    database.update_user(reddit_user)
    new_db_user = database.get_user("S2Sliferjam")
    assert new_db_user["num_guesses"] == updated_num_guesses

    # Reupdate user in database with original user data once the test is complete
    database.update_user(original_reddit_user)


def test_check_patch_notes_line_number(database):
    assert database.check_patch_notes_line_number(69)


def test_add_patch_notes_line_number(database):
    added_line_number = 77777
    database.add_patch_notes_line_number(added_line_number)
    assert database.check_patch_notes_line_number(added_line_number)
    database.db.table("patch_notes_line_tracker").remove(
        Query().id == added_line_number
    )


def test_get_entry_count_in_patch_notes_line_tracker(database):
    entry_count = database.get_entry_count_in_patch_notes_line_tracker()

    ## We know the number of lines in the test database
    assert entry_count == 102


def test_get_potential_winners_list(database):
    potential_winners_list = database.get_potential_winners_list()
    assert len(potential_winners_list) > 0


def test_get_random_winners_from_list(database):
    num_winners = 10
    potential_winners_list = database.get_potential_winners_list()
    random_winners_list = database.get_random_winners_from_list(
        num_winners=num_winners, potential_winners_list=potential_winners_list,
    )

    assert len(random_winners_list) == 10

    # Check for unique values in list. Reference: https://stackoverflow.com/a/5278167
    assert len(set(random_winners_list)) == len(random_winners_list)

    overly_large_num_winners = 7777777
    random_winners_list = database.get_random_winners_from_list(
        num_winners=overly_large_num_winners,
        potential_winners_list=potential_winners_list,
    )
    assert len(random_winners_list) < overly_large_num_winners

