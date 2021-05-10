from unittest.mock import patch, Mock
from unittest import TestCase
from pytest import mark

from datetime import datetime
from praw.exceptions import RedditAPIException
from requests.models import Response
from praw.models import Comment, Submission
from prawcore.exceptions import ServerError

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
        self.mock_author = patch("praw.models.Redditor")
        self.mock_comment = patch("praw.models.Comment")
        self.dummy_user = RedditUser("User1")

        # Configure mocks
        self.mock_submission.selftext = "Test string"
        self.mock_submission.edit = Mock()
        self.mock_community_submission.selftext = "Test string"
        self.mock_community_submission.edit = Mock()
        self.mock_community_submission.url = "Community Submission URL"
        self.mock_author.name = "User2"

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
                    self.dummy_user, self.mock_author, self.mock_comment, first_line
                )
                is None
            )

        first_line = ""

        # Regular case
        assert_test()

        # Cannot guess case
        self.dummy_user.can_submit_guess = False
        assert_test()

        # User is potential winner
        self.dummy_user.is_potential_winner = True
        assert_test()

    def test_get_user_from_database(self):
        # Existing user
        self.mock_author.name = "Tehnubzor"
        assert self.core.get_user_from_database(self.mock_author)

        # Non-existing user
        self.mock_author.name = "I_do_not_exist_asjdoiajsdiodwjowjdwq"
        assert self.core.get_user_from_database(self.mock_author)

    def test_is_account_too_new(self):
        # "Old" user (passes the check)
        self.mock_author.created_utc = 1609390800  # December 31, 2020 at 00:00:00
        assert not self.core.is_account_too_new(self.mock_author, MIN_ACCOUNT_AGE_DAYS)

        # "New" user (fails the check)
        self.mock_author.created_utc = datetime.utcnow().timestamp()
        assert self.core.is_account_too_new(self.mock_author, MIN_ACCOUNT_AGE_DAYS)

    def test_safe_comment_reply(self):
        # Regular use case
        assert self.core.safe_comment_reply(self.mock_comment, "Test Body") is None

        # Exceptions
        self.mock_comment.reply = Mock()
        self.mock_comment.reply.side_effect = RedditAPIException(
            ["RATELIMIT", "Error message", None], "Optional string",
        )
        assert self.core.safe_comment_reply(self.mock_comment, "Test Body") is None

    def test_update_community_compiled_patch_notes_in_submission(self):
        assert (
            self.core.update_community_compiled_patch_notes_in_submission(
                1, "Test content line"
            )
            is None
        )

    def test_is_disallowed_to_post(self):
        # Disallowed users set condition
        self.mock_author.name = "ElementUser"
        assert self.core.is_disallowed_to_post(self.mock_author, self.mock_comment)
        self.mock_author.name = "Some_username"

        # No verified email
        self.mock_author.has_verified_email = False
        assert self.core.is_disallowed_to_post(self.mock_author, self.mock_comment)
        self.mock_author.has_verified_email = True

        # Comment karma is 0
        self.mock_author.comment_karma = 0
        self.mock_author.link_karma = 0
        assert self.core.is_disallowed_to_post(self.mock_author, self.mock_comment)
        self.mock_author.comment_karma = 9999
        self.mock_author.link_karma = 9999

        # is_account_too_new() condition is True
        self.mock_author.created_utc = datetime.utcnow().timestamp()
        assert self.core.is_disallowed_to_post(self.mock_author, self.mock_comment)
        self.mock_author.created_utc = 1609390800  # December 31, 2020 at 00:00:00

        # Function should return False now
        assert not self.core.is_disallowed_to_post(self.mock_author, self.mock_comment)

    def test_fix_corrupted_community_submission_edit(self):
        assert self.core.fix_corrupted_community_submission_edit() is None

    def test_perform_post_game_actions(self):
        assert self.core.perform_post_game_actions() is None

    def test_update_patch_notes_table_in_db(self):
        patch_notes_line_number = 1

        assert self.core.update_patch_notes_table_in_db(
            self.dummy_user,
            self.mock_author,
            self.mock_comment,
            patch_notes_line_number,
        )

        # If patch notes line number is already guessed (which it will be after the above test)
        assert not self.core.update_patch_notes_table_in_db(
            self.dummy_user,
            self.mock_author,
            self.mock_comment,
            patch_notes_line_number,
        )

        # Teardown step
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)

    def test_process_guess_for_user(self):
        def assert_test(patch_notes_line_number):
            assert self.core.process_guess_for_user(
                self.dummy_user,
                self.mock_author,
                self.mock_comment,
                patch_notes_line_number,
            )

        # Valid line number
        patch_notes_line_number = 1
        assert_test(patch_notes_line_number)
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)

        # Line number with invalid string sequence
        patch_notes_line_number = 2
        assert_test(patch_notes_line_number)
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)

        # Blank line number
        patch_notes_line_number = 4
        assert_test(patch_notes_line_number)
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)

        # User cannot submit guess case
        patch_notes_line_number = 1
        self.dummy_user.can_submit_guess = False
        assert_test(patch_notes_line_number)
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)

    def test_process_game_rules_for_user(self):
        def assert_test(patch_notes_line_number):
            assert self.core.process_game_rules_for_user(
                self.dummy_user,
                self.mock_author,
                self.mock_comment,
                patch_notes_line_number,
            )

        # Regular usage
        patch_notes_line_number = 1
        assert_test(patch_notes_line_number)
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)

        # User cannot submit a guess
        self.dummy_user.can_submit_guess = False
        assert_test(patch_notes_line_number)
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)

        # User's guesses exceed the max
        self.dummy_user.can_submit_guess = True
        self.dummy_user.num_guesses = 9001
        assert_test(patch_notes_line_number)
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)

    @patch("hon_patch_notes_game_bot.core.Core")
    @patch("time.sleep")
    def test_loop(self, mock_core, sleep_func=Mock()):
        patch_notes_line_number = 1

        # Perform mock configurations
        self.mock_reddit.inbox = Mock()
        self.mock_comment = Mock(spec=Comment)
        self.mock_comment.submission = Mock(spec=Submission)

        # Set submission.id fields to be the same on both mocks
        self.mock_comment.submission.id = 694201
        self.mock_submission.id = 694201
        self.mock_comment.author = self.mock_author
        self.mock_comment.body = f"Patch notes line number: {patch_notes_line_number}"
        self.mock_comment.reply = Mock()
        self.mock_author.has_verified_email = True
        self.mock_author.comment_karma = 9001
        self.mock_author.created_utc = 1609390800  # December 31, 2020 at 00:00:00
        self.mock_reddit.inbox.unread = Mock(return_value=[self.mock_comment])
        assert not self.core.loop()
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)  # Teardown

        # Exception tests
        mock_response = Mock(spec=Response)
        mock_response.status_code = 503
        mock_response.json.return_value = {}
        self.mock_reddit.inbox.unread.side_effect = ServerError(mock_response)
        assert not self.core.loop()
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)  # Teardown

        self.mock_reddit.inbox.unread.side_effect = Exception("General Exception")
        assert not self.core.loop()
        self.core.db.delete_patch_notes_line_number(patch_notes_line_number)  # Teardown
