#!/usr/bin/python

"""
This module will keep track of all users that have posted in the allocated patch notes thread
Data will be saved in some form of database (to prevent loss of data, e.g. if Reddit or the bot crashes)
"""
import os
from random import sample
from tinydb import TinyDB, Query
from tinydb.table import Document
from typing import List, Optional

from hon_patch_notes_game_bot.user import RedditUser

User = Query()
LineNumber = Query()


class Database:
    def __init__(self, db_path: str = "cache/db.json"):
        """
        Parametrized constructor
        """

        # Make cache folder if it does not exist
        try:
            os.makedirs("cache")
        except OSError:
            print("Skipping creation of cache folder (already exists)...")

        self.db_path = db_path
        self.db = TinyDB(db_path)

    def insert_submission_url(self, tag: str, submission_url: str):
        """
        Inserts the submission url as an entry in the submission table

        Receives:
            - submission_url: the URL string of the Reddit submission

        This should be the only entry based on how the code has been designed in main.py
        """
        self.db.table("submission").insert({"tag": tag, "url": submission_url})

    def get_submission_url(self, tag) -> Optional[str]:
        """
        Gets the currently saved submission's URL, if it exists.

        Attributes:
            tag: tag of the item to search for

        Returns:
            The submission's URL, if it exists
            None if no data is found
        """
        submission_data = self.db.table("submission").get(Query().tag == tag)
        if submission_data is None:
            return None

        return submission_data["url"]

    def user_exists(self, name: str) -> bool:
        """
        Determines whether the user exists based on search by username

        Returns:
            True if the user exists
            False otherwise
        """
        return len(self.db.table("user").search(User.name == name)) > 0

    def get_user(self, name: str) -> Optional[Document]:
        """
        Retrieves a user object from the database by username
        """
        return self.db.table("user").get(User.name == name)

    def add_user(self, RedditUser: RedditUser):
        """
        Adds the user to the database

        Takes in a RedditUser object to do so (since the user model & RedditUser class share the same fields)
        """
        if not self.user_exists(RedditUser.name):
            self.db.table("user").insert(vars(RedditUser))

    def convert_db_user_to_RedditUser(self, db_user) -> RedditUser:
        """
        Converts a user object from the database to a new RedditUser instance

        Returns:
            A new RedditUser instance with the same properties as the db_user
        """
        user = RedditUser(
            name=db_user["name"],
            can_submit_guess=db_user["can_submit_guess"],
            is_potential_winner=db_user["is_potential_winner"],
            num_guesses=db_user["num_guesses"],
        )
        return user

    def update_user(self, RedditUser):
        """
        Updates the user data in the database

        Takes in a RedditUser object to do so (since the user model & RedditUser class share the same fields)
        """
        self.db.table("user").update(vars(RedditUser), User.name == RedditUser.name)

    def check_patch_notes_line_number(self, line_number: int) -> bool:
        """
        Checks if a previously guessed patch notes line number already exists in the database

        Returns:
            True if the patch notes line number exists in the database
            False otherwise
        """
        return (
            self.db.table("patch_notes_line_tracker").get(LineNumber.id == line_number)
            is not None
        )

    def delete_patch_notes_line_number(self, line_number: int) -> bool:
        """
        Deletes a patch notes line entry from the patch notes table database

        Returns:
            True if the patch notes line entry removal operation was successful
            False otherwise
        """
        if self.check_patch_notes_line_number(line_number):
            self.db.table("patch_notes_line_tracker").remove(
                LineNumber.id == line_number
            )
            return True
        return False

    def get_all_entries_in_patch_notes_tracker(self) -> List[Document]:
        """
        Returns all entries in the patch_notes_tracker table (as a list of Document objects)
        """
        return self.db.table("patch_notes_line_tracker").all()

    def add_patch_notes_line_number(self, line_number: int):
        """
        Adds the patch notes line number into the database.

        This is used to keep track of which line numbers have been guessed already.
        """
        self.db.table("patch_notes_line_tracker").insert({"id": line_number})

    def get_entry_count_in_patch_notes_line_tracker(self) -> int:
        """
        Returns the entry count (number of entries) in the patch_notes_line_tracker table
        """
        return len(self.get_all_entries_in_patch_notes_tracker())

    def get_potential_winners_list(self) -> List[str]:
        """
        Returns:
            A list of usernames that are marked as potential winners
        """
        # fmt: off
        raw_user_list = self.db.table("user").search(User.is_potential_winner == True)  # noqa: E712
        # fmt: on
        potential_winners_list = [user["name"] for user in raw_user_list]
        return potential_winners_list

    def get_random_winners_from_list(
        self, num_winners: int, potential_winners_list: list
    ) -> List[str]:
        """
        Picks a number of unique winners from the potential winners list.

        Attributes:
            num_winners: the number of winners to pick from the potential winners list
            potential_winners_list: a list containing the usernames, with each of them being a potential iwnner

        Returns:
            A list of usernames that are considered winners
            Returns the same list if 'num_winners' is the same size or bigger than the size of potential_winners_list
        """

        if num_winners >= len(potential_winners_list):
            return potential_winners_list

        return sample(potential_winners_list, num_winners)
