import pytest
import os

import hon_patch_notes_game_bot.util as util
from hon_patch_notes_game_bot.database import Database

# ============
# Unit tests
# ============
def test_get_patch_notes_line_number():
    commentBody = "123\n\nf4gh56"
    assert util.get_patch_notes_line_number(commentBody) == 123
    assert util.get_patch_notes_line_number("") == None


def test_is_game_expired():
    past_time = "September 1, 1990, 00:00:00 am UTC"
    assert util.is_game_expired(past_time)
    future_time = "December 31, 9001, 00:00:00 am UTC"
    assert util.is_game_expired(future_time) is False


def test_output_winners_list_to_file():
    db_path = "./tests/cache/db_test.json"
    output_file_path = "./tests/cache/winners_list.txt"

    util.output_winners_list_to_file(
        db_path=db_path, output_file_path=output_file_path,
    )
    assert os.path.exists(output_file_path)
    # Remove existing file after running test
    os.remove(output_file_path)

