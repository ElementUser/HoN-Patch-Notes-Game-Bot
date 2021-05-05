import pytest
from pytest import mark
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile

patch_notes_file_path = "./tests/config/patch_notes_test.txt"


# Fixtures (to also be re-used in other testing modules)
@pytest.fixture(scope="module")
def get_patch_notes_file():
    """Initializes patch notes file object"""
    return PatchNotesFile(patch_notes_file_path)


@pytest.fixture(scope="class")
def get_patch_notes_file_class_fixture(request, get_patch_notes_file):
    request.cls._patch_notes_file = get_patch_notes_file


@mark.usefixtures("get_patch_notes_file_class_fixture")
class TestPatchNotesFileHandler:
    def test_get_valid_line_number_func(self):
        # Since the test file is static, we know that line 1 has actual content
        assert self._patch_notes_file.get_content_from_line_number(1) is not None

    def test_get_invalid_line_number_func(self):
        # Since the test file is static, we know that line 5 has no content
        assert self._patch_notes_file.get_content_from_line_number(5) is None

    def test_get_total_line_count(self):
        # Since the test file is static, we know it has 730 lines
        assert self._patch_notes_file.get_total_line_count() == 730

    def test_get_list_of_blank_line_numbers(self):
        # Since the test file is static, we know it has 322 blank lines in it
        assert len(self._patch_notes_file.get_list_of_blank_line_numbers()) == 322

    def test_get_version_string(self):
        # Since the test file is static, we know it has 730 lines
        assert self._patch_notes_file.get_version_string() == "4.8.5"
