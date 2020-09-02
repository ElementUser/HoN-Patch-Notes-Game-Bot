#!/usr/bin/python

"""
This module will keep track of all users that have posted in the allocated patch notes thread
Data will be saved in some form of database (to prevent loss of data, e.g. if Reddit or the bot crashes)
"""
import os
from random import sample
from tinydb import TinyDB, Query

# Make cache folder if it does not exist
try:
    os.makedirs("cache")
except OSError:
    pass

db = TinyDB("cache/db.json")
User = Query()
LineNumber = Query()


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


def user_exists(name: str):
    """
    Determines whether the user exists based on search by username

    Returns:
        True if the user exists
        False otherwise
    """
    return db.table("user").search(User.name == name)


def get_user(name: str):
    """
    Retrieves a user object from the database by username
    """
    return db.table("user").get(User.name == name)


def add_user(RedditUser) -> None:
    """
    Adds the user to the database

    Takes in a RedditUser object to do so (since the user model & RedditUser class share the same fields)
    """
    if not user_exists(RedditUser.name):
        db.table("user").insert(vars(RedditUser))


def update_user(RedditUser) -> None:
    """
    Updates the user data in the database

    Takes in a RedditUser object to do so (since the user model & RedditUser class share the same fields)
    """
    db.table("user").update(vars(RedditUser), User.name == RedditUser.name)


def check_patch_notes_line_number(line_number: int):
    """
    Checks if a previously guessed patch notes line number already exists in the database

    Returns:
        A patch_notes_line_tracker object containing its id & line number value
        None if the entry does not exist
    """
    return db.table("patch_notes_line_tracker").get(LineNumber.id == line_number)


def add_patch_notes_line_number(line_number: int) -> None:
    """
    Adds the patch notes line number into the database.

    This is used to keep track of which line numbers have been guessed already.
    """
    db.table("patch_notes_line_tracker").insert({"id": line_number})


def get_potential_winners_list():
    """
    Returns:
        A list of usernames that are marked as potential winners
    """
    raw_user_list = db.table("user").search(User.is_potential_winner == True)
    potential_winners_list = [user["name"] for user in raw_user_list]
    return potential_winners_list


def get_random_winners_from_list(num_winners: int, potential_winners_list: list):
    """
    Picks a number of unique winners from the potential winners list.

    Attributes:
        num_winners: the number of winners to pick from the potential winners list
        potential_winners_list: a list containing the usernames, with each of them being a potential iwnner

    Returns:
        A list of usernames that are considered winners (returns the same list if 'num_winners' is the same size or bigger than the size of potential_winners_list)
    """

    if num_winners >= len(potential_winners_list):
        return potential_winners_list

    return sample(potential_winners_list, num_winners)
