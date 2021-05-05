"""
This module contains functions related to communications across the Reddit platform
"""
import time
import re
from typing import List

from praw.exceptions import RedditAPIException
from praw import Reddit
from hon_patch_notes_game_bot.config.config import STAFF_MEMBER_THAT_HANDS_OUT_REWARDS


def send_message_to_staff(
    reddit: Reddit,
    winners_list_path: str,
    staff_recipients: List[str],
    version_string: str,
    gold_coin_reward: int,
):
    """
    Sends the winners list results to a list of recipients via Private Message (PM)

    This function must be called only after the winners_list_path file exists!

    Attributes:
        reddit: the PRAW Reddit instance
        winners_list_path: the file path to read from for the winners list + potential winners list
        staff_recipients: a list of staff member recipients for the PM
        version_string: the version of the patch notes
        gold_coin_reward: the number of Gold Coins intended for the reward
    """
    with open(winners_list_path, "r") as winners_list_file:
        winners_list_text = (
            f"Give {str(gold_coin_reward)} Gold Coins to each winner.\n\n"
            + winners_list_file.read()
        )
        subject_line = (
            f"{version_string} - Winners for the HoN Patch Notes Guessing Game"
        )

        for recipient in staff_recipients:
            try:
                reddit.redditor(recipient).message(
                    subject=subject_line, message=winners_list_text
                )
            except RedditAPIException as redditError:
                print(
                    f"{redditError}\n{recipient} was not sent a message, continuing to next recipient"
                )
                continue
            except Exception as error:
                print(
                    f"{error}\n{recipient} was not sent a message, continuing to next recipient"
                )
                continue


def send_message_to_winners(
    reddit: Reddit, winners_list: List[str], version_string: str, gold_coin_reward: int
):
    """
    Sends the winners list results to a list of recipients via Private Message (PM).

    This function uses recursion to send messages to failed recipients.

    Attributes:
        reddit: the PRAW Reddit instance
        winners_list: a list of winning recipients for the PM
        version_string: the version of the patch notes
        gold_coin_reward: the number of Gold Coins intended for the reward
    """

    subject_line = f"Winner for the {version_string} Patch Notes Guessing Game"

    failed_recipients_list = []

    for recipient in winners_list:
        message = (
            f"Congratulations {recipient}!\n\n"
            f"You have been chosen by the bot as a winner for the {version_string} Patch Notes Guessing Game!\n\n"
            f"Please send /u/{STAFF_MEMBER_THAT_HANDS_OUT_REWARDS} a Private Message (PM) to request a code"
            f" for {str(gold_coin_reward)} Gold Coins.\n\n"
            "Thank you for participating in the game! =)"
        )
        try:
            reddit.redditor(recipient).message(subject=subject_line, message=message)
            print(f"Winner message sent to {recipient}")

        # Reddit API Exception
        except RedditAPIException as redditException:
            print(f"Full Reddit Exception: {redditException}\n\n")

            for subException in redditException.items:
                # Rate limit error handling
                if subException.error_type == "RATELIMIT":
                    failed_recipients_list.append(recipient)
                    print(
                        f"{redditException}\n{recipient} was not sent a message (added to retry list), continuing to next recipient"
                    )
                    print(f"Subexception: {subException}\n\n")

                    # Sleep for the rate limit duration by parsing the minute count from exception message
                    regex_capture = re.search(
                        r"(0?\.?\d+) minutes?", subException.message
                    )
                    if regex_capture is None:
                        print("Invalid regex detected. Sleeping for 10 seconds...")
                        time.sleep(10)
                        break
                    else:
                        minutesToSleep = regex_capture.group(1)
                        secondsToSleep = int(float(minutesToSleep) * 60)
                        print("Sleeping for " + str(secondsToSleep) + " seconds")
                        time.sleep(secondsToSleep)
                        break

            continue

        except Exception as error:
            print(
                f"{error}\n{recipient} was not sent a message (will not retry), continuing to next recipient"
            )
            continue

    # At the end of the function, recurse this function to re-send messages to failed recipients
    # Recurse only if failed_recipients_list has content in it
    # Prevents infinite loops by ensuring that the failed recipients count
    #   gradually progresses towards the end condition.
    failed_recipients = len(failed_recipients_list)
    if failed_recipients > 0 and failed_recipients < len(winners_list):
        send_message_to_winners(
            reddit, failed_recipients_list, version_string, gold_coin_reward
        )
