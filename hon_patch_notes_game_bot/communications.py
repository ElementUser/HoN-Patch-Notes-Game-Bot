"""
This module contains functions related to communications across the Reddit platform
"""


def send_message_to_staff(reddit, winners_list_path, staff_recipients, version_string):
    """
    Sends the winners list results to a list of recipients via Private Message (PM)

    This function must be called only after the winners_list_path file exists!

    Attributes:
        reddit: the PRAW Reddit instance
        winners_list_path: the file path to read from for the winners list + potential winners list
        staff_recipients: a list of staff member recipients for the PM
        version_string: the version of the patch notes
    """
    with open(winners_list_path, "r") as winners_list_file:
        winners_list_text = winners_list_file.read()
        subject_line = (
            f"{version_string} - Winners for the HoN Patch Notes Guessing Game"
        )

        for recipient in staff_recipients:
            reddit.redditor(recipient).message(
                subject=subject_line, message=winners_list_text
            )


def send_message_to_winners(reddit, winners_list, version_string, gold_coin_reward):
    """
    Sends the winners list results to a list of recipients via Private Message (PM)

    Attributes:
        reddit: the PRAW Reddit instance
        winners_list: a list of winning recipients for the PM
        version_string: the version of the patch notes
        gold_coin_reward: the number of Gold Coins intended for the reward
    """

    subject_line = f"Winner for the {version_string} Patch Notes Guessing Game"

    for recipient in winners_list:
        message = (
            f"Congratulations {recipient}!\n\n"
            f"You have been chosen by the bot as a winner for the {version_string} Patch Notes Guessing Game!\n\n"
            f"Please send /u/S2Sliferjam a Private Message (PM) to request a code for {str(gold_coin_reward)} Gold Coins.\n\n"
            "Thank you for participating in the game! =)"
        )
        reddit.redditor(recipient).message(subject=subject_line, message=message)
