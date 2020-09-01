import pytest
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile

patch_notes_file_path = "./tests/cache/patch_notes_test.txt"


@pytest.fixture
def patch_notes_file():
    """Initializes patch notes file object"""
    return PatchNotesFile(patch_notes_file_path)


# Unit tests
def test_get_valid_line_number_func(patch_notes_file):
    # Since the test file is static, we know that line 1 has actual content
    assert patch_notes_file.get_content_from_line_number(1) is not None


def test_get_invalid_line_number_func(patch_notes_file):
    # Since the test file is static, we know that line 5 has no content
    assert patch_notes_file.get_content_from_line_number(5) is None


def test_get_total_line_count(patch_notes_file):
    # Since the test file is static, we know it has 730 lines
    assert patch_notes_file.get_total_line_count() == 730


def test_get_version_string(patch_notes_file):
    # Since the test file is static, we know it has 730 lines
    assert patch_notes_file.get_version_string == "4.8.5"
