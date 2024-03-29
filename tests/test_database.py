import os
import shutil
import pytest
from pytest import mark

from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.user import RedditUser
from tinydb import Query


@pytest.fixture(scope="class")
def setup_and_teardown_test_database(request):
    # Setup
    database_path = "./tests/cache/db_test.json"
    database_backup_path = "./tests/cache/db_test_backup.json"

    # Store backup database file to be restored later
    shutil.copy2(database_path, database_backup_path)
    request.cls._database = Database(db_path=database_path)

    # Perform tests in the class that uses this fixture
    yield

    # Teardown
    shutil.copy2(database_backup_path, database_path)
    os.remove(database_backup_path)


@mark.usefixtures("setup_and_teardown_test_database")
class TestDataBase:
    def test_insert_submission_url(self):
        url_string = "http://test_url.com"
        self._database.insert_submission_url(
            tag="test_entry", submission_url=url_string
        )
        assert self._database.db.table("submission").search(Query().url == url_string)
        # Remove entry from database afterwards
        self._database.db.table("submission").remove(Query().url == url_string)

    def test_get_submission_url(self):
        url_string = "https://www.reddit.com/r/HeroesofNewerth/comments/in14hz/game_486_patch_notes_guessing_game/"
        assert self._database.get_submission_url(tag="main") == url_string

    def test_get_unfound_submission_url(self):
        assert self._database.get_submission_url(tag="unfound_url_tag") is None

    def test_user_exists(self):
        assert self._database.user_exists("S2Sliferjam")
        assert not self._database.user_exists(
            "random_user_that_doesnt_exist_89213u893u13u132u139u31983u13dasdadsadsa"
        )

    def test_get_user(self):
        assert self._database.get_user("S2Sliferjam")

    def test_add_user(self):
        username = "random_user_that_temporarily_exists_213123asd"
        user = RedditUser(name=username)
        self._database.add_user(user)
        assert self._database.user_exists(username)

    def test_convert_db_user_to_RedditUser(self):
        db_user = self._database.get_user("S2Sliferjam")
        reddit_user = self._database.convert_db_user_to_RedditUser(db_user)

        # Cannot iterate over an object's attributes directly,
        # but can make a dictionary of their attributes via vars()
        reddit_user_attributes = vars(reddit_user)

        for key in db_user:
            assert db_user[key] == reddit_user_attributes[key]

    def test_update_user(self):
        updated_num_guesses = 1000
        db_user = self._database.get_user("S2Sliferjam")
        reddit_user = self._database.convert_db_user_to_RedditUser(db_user)

        # Change the num_guesses field & test that
        reddit_user.num_guesses = updated_num_guesses
        self._database.update_user(reddit_user)
        new_db_user = self._database.get_user("S2Sliferjam")
        assert new_db_user["num_guesses"] == updated_num_guesses

    def test_check_patch_notes_line_number(self):
        assert self._database.check_patch_notes_line_number(69)

    def test_check_unfound_patch_notes_line_number(self):
        assert not self._database.check_patch_notes_line_number(69420)

    def test_add_patch_notes_line_number(self):
        added_line_number = 77777
        self._database.add_patch_notes_line_number(added_line_number)
        assert self._database.check_patch_notes_line_number(added_line_number)
        self._database.db.table("patch_notes_line_tracker").remove(
            Query().id == added_line_number
        )

    def test_get_entry_count_in_patch_notes_line_tracker(self):
        entry_count = self._database.get_entry_count_in_patch_notes_line_tracker()

        ## We know the number of lines in the test database
        assert entry_count == 102

    def test_get_potential_winners_list(self):
        potential_winners_list = self._database.get_potential_winners_list()
        assert len(potential_winners_list) > 0

    def test_get_random_winners_from_list(self):
        num_winners = 10
        potential_winners_list = self._database.get_potential_winners_list()
        random_winners_list = self._database.get_random_winners_from_list(
            num_winners=num_winners, potential_winners_list=potential_winners_list,
        )

        assert len(random_winners_list) == 10

        # Check for unique values in list. Reference: https://stackoverflow.com/a/5278167
        assert len(set(random_winners_list)) == len(random_winners_list)

        overly_large_num_winners = 7777777
        random_winners_list = self._database.get_random_winners_from_list(
            num_winners=overly_large_num_winners,
            potential_winners_list=potential_winners_list,
        )
        assert len(random_winners_list) < overly_large_num_winners

