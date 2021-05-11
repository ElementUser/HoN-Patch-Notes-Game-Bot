from unittest.mock import patch, Mock
from unittest import TestCase
from pytest import mark

from hon_patch_notes_game_bot import main
from hon_patch_notes_game_bot.user import RedditUser


@mark.usefixtures(
    "get_patch_notes_file_class_fixture", "setup_and_teardown_test_database"
)
class TestMain(TestCase):
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

    # TODO: implement this some time in the future (low priority)
    # def test_main(self, mock_init_submissions):
    #     assert main.main()
