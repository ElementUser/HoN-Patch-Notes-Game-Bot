"""
This module contains standalone utility functions
"""
import re
from dateutil import tz
from dateutil.parser import parse
from datetime import datetime

from hon_patch_notes_game_bot.database import Database


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


def is_game_expired(time_string: str):
    """
    Takes in a time string to determine if the game has expired

    Returns:
        True if the present time is later than the game end time
        False otherwise
    """
    game_end_datetime = parse(time_string)
    present_time = datetime.now(tz.UTC)
    return present_time > game_end_datetime


def output_winners_list_to_file(db_path, output_file_path, num_winners=10):
    """
    Outputs the list of winners & potential winners to an output file

    Attributes:
        db_path: the path to the local TinyDB database file
        output_file_path: the path to where the data will be output
    """
    database = Database(db_path)
    # Process winners
    with open(output_file_path, "a+") as output_file:
        # Reference for reading & overwriting a file: https://stackoverflow.com/a/2424410
        text = output_file.read()
        output_file.seek(0)
        output_file.write(text)
        output_file.truncate()

        potential_winners_list = database.get_potential_winners_list()
        winners_list = database.get_random_winners_from_list(
            num_winners=num_winners, potential_winners_list=potential_winners_list
        )
        output_file.write("========\n")
        output_file.write("Winners\n")
        output_file.write("========\n\n")
        for winner in winners_list:
            output_file.write(f"{winner}\n")

        output_file.write("\n==================\n")
        output_file.write("Potential Winners\n")
        output_file.write("==================\n\n")
        for user in potential_winners_list:
            output_file.write(f"{user}\n")


# Only run if util function is ran directly from command line
if __name__ == "__main__":
    output_winners_list_to_file(
        db_path="cache/db.json", output_file_path="cache/winners_list.txt"
    )
