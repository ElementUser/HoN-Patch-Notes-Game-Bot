from unittest.mock import patch, Mock
from unittest import TestCase
from pytest import mark

from hon_patch_notes_game_bot import core
from hon_patch_notes_game_bot.database import Database
from tests.test_patch_notes_file_handler import patch_notes_file
from tests.test_database import database_path


class TestCore(TestCase):
    @mark.usefixtures("patch_notes_file")
    def setup_class(self):
        self.mock_reddit = patch("praw.Reddit")
        self.mock_submission = patch("praw.models.Submission")
        self.mock_community_submission = patch("praw.models.Submission")
        self.database = Database(db_path=database_path)
        self.core = core.Core(
            reddit=self.mock_reddit,
            db=self.database,
            submission=self.mock_submission,
            community_submission=self.mock_community_submission,
            patch_notes_file=patch_notes_file,
        )

    def test_empty(self):
        pass
