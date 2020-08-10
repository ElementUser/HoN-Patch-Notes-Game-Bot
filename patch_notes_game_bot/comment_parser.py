#!/usr/bin/python
import re

"""
This module contains functions that will parse through a Reddit comment data

PRAW Comment API: https://praw.readthedocs.io/en/latest/code_overview/models/comment.html
"""


def get_patch_notes_line_number(comment):
    """
    Returns the first integer from the comment
    """
    return re.search(r"\d+", comment).group()
