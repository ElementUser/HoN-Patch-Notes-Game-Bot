from unittest.mock import patch, Mock
from unittest import TestCase
from pytest import mark

from datetime import datetime
from praw.exceptions import RedditAPIException

from hon_patch_notes_game_bot import core
from hon_patch_notes_game_bot.user import RedditUser
from hon_patch_notes_game_bot.config.config import MIN_ACCOUNT_AGE_DAYS


@mark.usefixtures(
    "get_patch_notes_file_class_fixture", "setup_and_teardown_test_database"
)
class TestCore(TestCase):
    def setUp(self):
        self.mock_reddit = patch("praw.Reddit")
        self.mock_submission = patch("praw.models.Submission")
        self.mock_community_submission = patch("praw.models.Submission")

        # Configure mocks
        self.mock_submission.selftext = "Test string"
        self.mock_submission.edit = Mock()
        self.mock_community_submission.selftext = "Test string"
        self.mock_community_submission.edit = Mock()

        # Create a concrete Core object
        self.core = core.Core(
            reddit=self.mock_reddit,
            db=self._database,
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
        assert (
            self.core.update_community_compiled_patch_notes_in_submission(
                1, "Test content line"
            )
            is None
        )

    def test_is_disallowed_to_post(self):
        mock_redditor = patch("praw.models.Redditor")
        mock_comment = patch("praw.models.Comment")

        # Disallowed users set condition
        mock_redditor.name = "ElementUser"
        assert self.core.is_disallowed_to_post(mock_redditor, mock_comment)
        mock_redditor.name = "Some_username"

        # No verified email
        mock_redditor.has_verified_email = False
        assert self.core.is_disallowed_to_post(mock_redditor, mock_comment)
        mock_redditor.has_verified_email = True

        # Comment karma is 0
        mock_redditor.comment_karma = 0
        mock_redditor.link_karma = 0
        assert self.core.is_disallowed_to_post(mock_redditor, mock_comment)
        mock_redditor.comment_karma = 9999
        mock_redditor.link_karma = 9999

        # is_account_too_new() condition is True
        mock_redditor.created_utc = datetime.utcnow().timestamp()
        assert self.core.is_disallowed_to_post(mock_redditor, mock_comment)
        mock_redditor.created_utc = 1609390800  # December 31, 2020 at 00:00:00

        # Function should return False now
        assert not self.core.is_disallowed_to_post(mock_redditor, mock_comment)

    def test_fix_corrupted_community_submission_edit(self):
        assert self.core.fix_corrupted_community_submission_edit() is None

    def test_perform_post_game_actions(self):
        assert self.core.perform_post_game_actions() is None
