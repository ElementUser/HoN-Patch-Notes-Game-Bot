from praw.models import Comment
from hon_patch_notes_game_bot.core import get_patch_notes_line_number


# ============
# Unit tests
# ============
def test_get_patch_notes_line_number():
    commentBody = "123\n\nf4gh56"
    assert get_patch_notes_line_number(commentBody) == 123
