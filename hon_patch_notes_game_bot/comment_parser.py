#!/usr/bin/python
import re

"""
This module contains functions that will parse through a Reddit comment data

PRAW Comment API: https://praw.readthedocs.io/en/latest/code_overview/models/comment.html
"""


def get_patch_notes_line_number(commentBody: str) -> int:
    """
    Returns the first integer from the comment body

    Returns None if no valid integer can be found
    """

    try:
        comment_first_line = commentBody.partition("\n")[0]
        return int(re.search(r"\d+", comment_first_line).group())
    except AttributeError:
        return None
