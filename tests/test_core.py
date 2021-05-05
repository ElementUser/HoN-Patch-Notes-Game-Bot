from unittest.mock import patch
from unittest import TestCase
from pytest import mark

from hon_patch_notes_game_bot import core
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.user import RedditUser
from tests.test_database import database_path


@mark.usefixtures("get_patch_notes_file_class_fixture")
class TestCore(TestCase):
    def setUp(self):
        self.mock_reddit = patch("praw.Reddit")
        self.mock_submission = patch("praw.models.Submission")
        self.mock_community_submission = patch("praw.models.Submission")
        self.database = Database(db_path=database_path)
        self.core = core.Core(
            reddit=self.mock_reddit,
            db=self.database,
            submission=self.mock_submission,
            community_submission=self.mock_community_submission,
            patch_notes_file=self._patch_notes_file,
        )

    def test_has_exceeded_revealed_line_count(self):
        assert not self.core.has_exceeded_revealed_line_count()

    def test_reply_with_bad_guess_feedback(self):
        def assert_test():
            assert (
                self.core.reply_with_bad_guess_feedback(
                    mock_user, mock_author, mock_comment, first_line
                )
                is None
            )

        mock_user = RedditUser("User1")
        mock_author = patch("praw.models.Redditor")
        mock_author.name = "User2"
        mock_comment = patch("praw.models.Comment")
        first_line = ""

        # Regular case
        assert_test()

        # Cannot guess case
        mock_user.can_submit_guess = False
        assert_test()

        # User is potential winner
        mock_user.is_potential_winner = True
        assert_test()
