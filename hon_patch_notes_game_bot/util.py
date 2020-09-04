"""
This module contains standalone utility functions
"""
import re
import sys
from dateutil import tz
from dateutil.parser import parse
from datetime import datetime

from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.config.config import NUM_WINNERS


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
    game_end_datetime = parse(time_string, fuzzy=True)
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


def generate_submission_compiled_patch_notes_template_line(line_number):
    """
    For a given line number, construct the template line for the community-compiled patch notes.
    """
    return f">{str(line_number)} |\n\n"


def convert_time_string_to_wolframalpha_query_url(time_string):
    """
    Converts a time string to a Wolframalpha URL

    Returns:
        - The converted URL that links to the Wolframalpha query results
    """
    formatted_query = time_string.replace(" ", "+")
    return f"https://www.wolframalpha.com/input/?i={formatted_query}"


# Only run if util function is ran directly from command line
if __name__ == "__main__":
    """
    Runs output_winners_list_to_file() with num_winners being taken from the command line args
    """
    if len(sys.argv) > 2:
        sys.exit(
            "Please use 0 arguments or 1 arguments (where the 1st argument is a number)"
        )

    if len(sys.argv) == 2:
        num_winners = int(sys.argv[1])
    else:
        num_winners = NUM_WINNERS

    output_winners_list_to_file(
        db_path="cache/db.json",
        output_file_path="cache/winners_list.txt",
        num_winners=num_winners,
    )
