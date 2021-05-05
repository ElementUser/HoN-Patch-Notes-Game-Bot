from unittest.mock import patch, Mock
from unittest import TestCase
from pytest import mark

from datetime import datetime
from praw.exceptions import RedditAPIException

from tests.test_database import database_path
from hon_patch_notes_game_bot import core
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.user import RedditUser
from hon_patch_notes_game_bot.config.config import MIN_ACCOUNT_AGE_DAYS


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

    def test_get_user_from_database(self):
        mock_author = patch("praw.models.Redditor")

        # Existing user
        mock_author.name = "Tehnubzor"
        assert self.core.get_user_from_database(mock_author)

        # Non-existing user
        # TODO: Reset DB state
        mock_author.name = "I_do_not_exist_asjdoiajsdiodwjowjdwq"
        assert self.core.get_user_from_database(mock_author)

    def test_is_account_too_new(self):
        mock_author = patch("praw.models.Redditor")

        # "Old" user (passes the check)
        mock_author.created_utc = 1609390800  # December 31, 2020 at 00:00:00
        assert not self.core.is_account_too_new(mock_author, MIN_ACCOUNT_AGE_DAYS)

        # "New" user (fails the check)
        mock_author.created_utc = datetime.utcnow().timestamp()
        assert self.core.is_account_too_new(mock_author, MIN_ACCOUNT_AGE_DAYS)

    def test_safe_comment_reply(self):
        # Regular use case
        mock_comment = patch("praw.models.Comment")
        assert self.core.safe_comment_reply(mock_comment, "Test Body") is None

        # Exceptions
        mock_comment.reply = Mock()
        mock_comment.reply.side_effect = RedditAPIException(
            ["RATELIMIT", "Error message", None], "Optional string",
        )
        assert self.core.safe_comment_reply(mock_comment, "Test Body") is None

    def test_update_community_compiled_patch_notes_in_submission(self):
        self.core.community_submission.selftext = "Test string"
        self.core.community_submission.edit = Mock()
        assert (
            self.core.update_community_compiled_patch_notes_in_submission(
                1, "Test content line"
            )
            is None
        )
