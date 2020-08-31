#!/usr/bin/python

"""
This module will keep track of all users that have posted in the allocated patch notes thread
Data will be saved in some form of database (to prevent loss of data, e.g. if Reddit or the bot crashes)
"""

from tinydb import TinyDB, Query
from hon_patch_notes_game_bot.user import RedditUser

db = TinyDB("db.json")
User = Query()


def get_submission_url():
    """
    Gets the currently saved submission's URL, if it exists

    It is assumed that this database will only have one "url" key-value pair object at all times!

    Returns:
        The submission's URL, if it exists
        None if no data is found
    """

    data = db.table("submission").all()
    if len(data) == 0:
        return None

    return data[0]["url"]


def user_exists(id: int):
    return db.table("user").search(User.id.exists())


def get_user(id: int):
    return db.table("user").get(User.id == id)


def add_user(RedditUser) -> None:
    if not user_exists(RedditUser["id"]):
        db.table("user").insert(vars(RedditUser))
