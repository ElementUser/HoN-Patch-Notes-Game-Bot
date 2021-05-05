#!/usr/bin/python
"""
This module contains standalone utility functions
"""
import re
from dateutil import tz
from dateutil.parser import parse
from datetime import datetime
from typing import List, Optional

from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile
from hon_patch_notes_game_bot.config.config import (
    GAME_END_TIME,
    GOLD_COIN_REWARD,
    MAX_NUM_GUESSES,
    MAX_PERCENT_OF_LINES_REVEALED,
    NUM_WINNERS,
)


def get_patch_notes_line_number(commentBody: str) -> Optional[int]:
    """
        Returns the first integer from the comment body

        Returns None if no valid integer can be found
        """
    comment_first_line = commentBody.partition("\n")[0]
    number_line_match = re.search(r"\d+", comment_first_line)
    if number_line_match is None:
        return None

    return int(number_line_match.group())


def is_game_expired(time_string: str) -> bool:
    """
    Takes in a time string to determine if the game has expired

    Returns:
        True if the present time is later than the game end time
        False otherwise
    """
    game_end_datetime = parse(time_string, fuzzy=True)
    present_time = datetime.now(tz.UTC)
    return present_time > game_end_datetime


def output_winners_list_to_file(
    potential_winners_list: List[str], winners_list: List[str], output_file_path: str
):
    """
    Outputs the list of winners & potential winners to an output file

    Returns:
        String content that was written to the file

    Attributes:
        potential_winners_list: the list of potential winners
        winners_list: the list of actual winners
        output_file_path: the path to where the data will be output
    """
    with open(output_file_path, "a+") as output_file:
        # Reference for reading & overwriting a file: https://stackoverflow.com/a/2424410
        text = output_file.read()
        output_file.seek(0)
        output_file.write(text)
        output_file.truncate()

        # Winners subheading and content
        file_content = "## Winners\n\n```"

        for winner in winners_list:
            file_content += f"{winner}\n"
        file_content += "```"

        # Potential Winners subheading and content
        file_content += "\n## Potential Winners\n\n```"
        for user in potential_winners_list:
            file_content += f"{user}\n"
        file_content += "```"
        output_file.write(file_content)

        winners_submission_content = (
            "\n# Update\n___\n\nThe game has now ended. Thank you to everyone for playing!\n\n"
            + "The winners list & potential winners pool have been posted below (auto-generated by the bot).\n\n"
            + file_content
            + "\n___\n\n"
        )
        return winners_submission_content


def generate_submission_compiled_patch_notes_template_line(line_number: int):
    """
    For a given line number, construct the template line for the community-compiled patch notes.
    """
    return f">{str(line_number)} |\n\n"


def convert_time_string_to_wolframalpha_query_url(time_string: str) -> str:
    """
    Converts a time string to a Wolframalpha URL

    Returns:
        - The converted URL that links to the Wolframalpha query results
    """
    formatted_query = time_string.replace(" ", "+")
    return f"https://www.wolframalpha.com/input/?i={formatted_query}"


def processed_submission_content(
    submission_content_path: str, patch_notes_file: PatchNotesFile
) -> str:
    """
    Reads the submission_content.md file, then uses data from a PatchNotesFile instance to further process it.
    Iterates through a pre-set dictionary's key-value pairs to perform the string replacement processing.

    Returns:
        A processed string containing the modified submission content
    """
    with open(submission_content_path, "r") as file:
        submission_content = file.read()
        version_string = patch_notes_file.get_version_string()

        replacement_dict = {
            "PATCH_VERSION": version_string,
            "GAME_END_TIME": f"[{GAME_END_TIME}]({convert_time_string_to_wolframalpha_query_url(GAME_END_TIME)})",
            "GOLD_COIN_REWARD": str(GOLD_COIN_REWARD),
            "MAX_LINE_COUNT": str(patch_notes_file.get_total_line_count()),
            "MAX_NUM_GUESSES": str(MAX_NUM_GUESSES),
            "MAX_PERCENT_OF_LINES_REVEALED": str(MAX_PERCENT_OF_LINES_REVEALED),
            "NUM_WINNERS": str(NUM_WINNERS),
        }

        for source_str, target_str in replacement_dict.items():
            submission_content = submission_content.replace(
                f"`{source_str}`", target_str
            )

        return submission_content


def processed_community_notes_thread_submission_content(
    submission_content_path: str,
    patch_notes_file: PatchNotesFile,
    main_submission_url: str,
) -> str:
    """
    Reads the community_patch_notes_compilation.md file, then uses data from a PatchNotesFile instance to further process it

    Returns:
        A processed string containing the submission content
    """
    with open(submission_content_path, "r") as file:
        submission_content = file.read()
        submission_content = submission_content.replace(
            "#main-reddit-thread", main_submission_url
        )

        submission_content += "\n\n# Community-compiled Patch Notes\n\nThe patch notes compiled by the community will automatically be updated below (guessed lines that are blank will be marked with `...`):\n\n"  # noqa: E501
        for line_number in range(1, patch_notes_file.get_total_line_count() + 1):
            submission_content += generate_submission_compiled_patch_notes_template_line(
                line_number=line_number
            )

        submission_content += f"\n\n**Guesses in this thread will not be responded to by the bot. [Visit the main thread instead!]({main_submission_url})**\n\nFeel free to discuss patch changes here liberally (based on the currently revealed notes)! :)"  # noqa: E501
        return submission_content