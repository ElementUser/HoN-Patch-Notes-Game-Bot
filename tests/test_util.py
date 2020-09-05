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
    potential_winners_list = ["a", "b", "c", "d", "e"]
    winners_list = ["a", "b", "c"]
    output_file_path = "./tests/cache/winners_list.txt"

    util.output_winners_list_to_file(
        potential_winners_list=potential_winners_list,
        winners_list=winners_list,
        output_file_path=output_file_path,
    )
    assert os.path.exists(output_file_path)
    # Remove existing file after running test
    os.remove(output_file_path)


def test_generate_submission_compiled_patch_notes_template_line():
    line_number = 123
    expected_string = f">{line_number} |\n\n"
    assert (
        util.generate_submission_compiled_patch_notes_template_line(
            line_number=line_number
        )
        == expected_string
    )


def test_convert_time_string_to_wolframalpha_query_url():
    time_string = "September 14, 2020, 04:00:00 am UTC"
    expected_url = (
        "https://www.wolframalpha.com/input/?i=September+14,+2020,+04:00:00+am+UTC"
    )
    assert (
        util.convert_time_string_to_wolframalpha_query_url(time_string) == expected_url
    )

