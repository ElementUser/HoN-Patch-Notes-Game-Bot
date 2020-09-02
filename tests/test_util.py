import pytest
import hon_patch_notes_game_bot.util as util

# ============
# Unit tests
# ============
def test_get_patch_notes_line_number():
    commentBody = "123\n\nf4gh56"
    assert util.get_patch_notes_line_number(commentBody) == 123
    assert util.get_patch_notes_line_number("") == None
