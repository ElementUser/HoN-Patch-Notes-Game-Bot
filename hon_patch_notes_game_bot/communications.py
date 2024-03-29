#!/usr/bin/python
"""
This module contains functions related to communications across the Reddit platform
"""
import time
import re
from typing import List, Tuple

from praw import Reddit
from praw.exceptions import RedditAPIException
from praw.models import Subreddit, Submission
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile
from hon_patch_notes_game_bot.utils import (
    processed_submission_content,
    processed_community_notes_thread_submission_content,
    tprint,
)
from hon_patch_notes_game_bot.config.config import (
    COMMUNITY_SUBMISSION_TITLE,
    STAFF_MEMBER_THAT_HANDS_OUT_REWARDS,
    SUBMISSION_TITLE,
)


def init_submissions(
    reddit: Reddit,
    subreddit: Subreddit,
    database: Database,
    patch_notes_file: PatchNotesFile,
    submission_content_path: str,
    community_submission_content_path: str,
) -> Tuple[Submission, Submission]:
    """
    Initializes the primary and community submission (i.e. "Reddit threads") objects.
    If they do not exist in the database, then this function creates them.
        Otherwise, it retrieves the submissions via their URL from the database.

    Returns:
        - A tuple containing the primary submission and community submission objects
    """
    # Main submission
    submission_content = processed_submission_content(
        submission_content_path, patch_notes_file
    )
    submission: Submission = None
    submission_url = database.get_submission_url(tag="main")

    # Get main submission if it does not exist
    if submission_url is None:
        submission = subreddit.submit(
            title=SUBMISSION_TITLE, selftext=submission_content
        )
        database.insert_submission_url("main", submission.url)
        submission_url = submission.url
    else:
        # Obtain submission via URL
        submission = reddit.submission(url=submission_url)

    # Community submission
    community_submission_content = processed_community_notes_thread_submission_content(
        community_submission_content_path, patch_notes_file, submission_url
    )
    community_submission: Submission = None
    community_submission_url = database.get_submission_url(tag="community")

    # Get community submission if it does not exist
    if community_submission_url is None:
        community_submission = subreddit.submit(
            title=COMMUNITY_SUBMISSION_TITLE, selftext=community_submission_content,
        )
        database.insert_submission_url("community", community_submission.url)

        # Update main Reddit Thread's in-line URL to connect to the community submission URL
        updated_text = submission.selftext.replace(
            "#community-patch-notes-thread-url", community_submission.url
        )
        submission.edit(body=updated_text)
    else:
        # Obtain submission via URL
        community_submission = reddit.submission(url=community_submission_url)

    return submission, community_submission


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
            f"The following Reddit users have won {str(gold_coin_reward)} Gold Coins from the Reddit Patch Notes game:\n\n"
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
                tprint(f"RedditAPIException encountered: {redditError}")
                tprint(
                    f"{recipient} was not sent a message, continuing to next recipient"
                )
                continue
            except Exception as error:
                tprint(f"General Exception encountered: {error}")
                tprint(
                    f"{recipient} was not sent a message, continuing to next recipient"
                )
                continue


def send_message_to_winners(  # noqa: C901
    reddit: Reddit,
    winners_list: List[str],
    reward_codes_list: List[str],
    version_string: str,
    gold_coin_reward: int,
):
    """
    Sends the winners list results to a list of recipients via Private Message (PM).

    This function uses recursion to send messages to failed recipients.

    This function also frequently encounters Reddit API Exceptions due to rate limits.
        To sleep for the appropriate duration without wasting time, the rate limit error is parsed:

    Test strings for regex capture:
    RATELIMIT: "Looks like you've been doing that a lot. Take a break for 4 minutes before trying again." on field 'ratelimit'
    RATELIMIT: "Looks like you've been doing that a lot. Take a break for 47 seconds before trying again." on field 'ratelimit'
    RATELIMIT: "Looks like you've been doing that a lot. Take a break for 4 minutes 47 seconds before trying again."
        on field 'ratelimit'
    RATELIMIT: "Looks like you've been doing that a lot. Take a break for 1 minute before trying again." on field 'ratelimit'

    Attributes:
        reddit: the PRAW Reddit instance
        winners_list: a list of winning recipients for the PM
        reward_codes_list: a list of reward codes for each winner
        version_string: the version of the patch notes
        gold_coin_reward: the number of Gold Coins intended for the reward
    """

    subject_line = f"Winner for the {version_string} Patch Notes Guessing Game"

    failed_recipients_list = []

    for recipient in winners_list:
        reward_code = (
            "N/A - all possible reward codes have been used up.\n\n"
            f"Please contact {STAFF_MEMBER_THAT_HANDS_OUT_REWARDS} for a code to be issued manually."
        )
        if len(reward_codes_list) > 0:
            reward_code = reward_codes_list[0]

        # TODO: Add this back if reward codes generator works again
        # message = (
        #     f"Congratulations {recipient}!\n\n"
        #     f"You have been chosen by the bot as a winner for the {version_string} Patch Notes Guessing Game!\n\n"
        #     f"Your reward code for {str(gold_coin_reward)} Gold Coins is: **{reward_code}**\n\n"
        #     "You can redeem your reward code here: https://www.heroesofnewerth.com/redeem/\n\n"
        #     f"Please contact {STAFF_MEMBER_THAT_HANDS_OUT_REWARDS} if any issues arise.\n\n"
        #     "Thank you for participating in the game! =)"
        # )

        message = (
            f"Congratulations {recipient}!\n\n"
            f"You have been chosen by the bot as a winner for the {version_string} Patch Notes Guessing Game!\n\n"
            f"Please contact /u/{STAFF_MEMBER_THAT_HANDS_OUT_REWARDS} via the Reddit Messaging system to obtain your code.\n\n"
            "Please include your In-Game Username in your message.\n\n"
            "Thank you for participating in the game! =)"
        )
        try:
            reddit.redditor(recipient).message(subject=subject_line, message=message)
            tprint(f"Winner message sent to {recipient}, with code: {reward_code}")

            # Pop reward code from list only if the message was sent successfully
            if len(reward_codes_list) > 0:
                reward_codes_list.pop(0)

        # Reddit API Exception
        except RedditAPIException as redditException:
            tprint(f"Full Reddit Exception: {redditException}\n\n")

            for subException in redditException.items:
                # Rate limit error handling
                if subException.error_type == "RATELIMIT":
                    failed_recipients_list.append(recipient)
                    tprint(
                        f"{redditException}\n{recipient} was not sent a message (added to retry list), "
                        "continuing to next recipient"
                    )
                    tprint(f"Subexception: {subException}\n\n")

                    # Sleep for the rate limit duration by parsing the minute and seconds count from
                    #   the message into named groups
                    regex_capture = re.search(
                        r"\s+((?P<minutes>\d+) minutes?)?\s?((?P<seconds>\d+) seconds)?\s+",
                        subException.message,
                    )
                    if regex_capture is None:
                        print("Invalid regex detected. Sleeping for 60 seconds...")
                        time.sleep(60)
                        break
                    else:
                        # Use named groups from regex capture and assign them to a dictionary
                        sleep_time_regex_groups = regex_capture.groupdict(default=0)

                        # Add 1 extra second to account for millisecond-precision checking
                        secondsToSleep = (
                            60
                            * int(
                                sleep_time_regex_groups.get("minutes")  # type: ignore
                            )
                            + int(
                                sleep_time_regex_groups.get("seconds")  # type: ignore
                            )
                            + 1
                        )  # type: ignore

                        print(f"Sleeping for {str(secondsToSleep)} seconds")
                        time.sleep(secondsToSleep)
                        break

            continue

        except Exception as error:
            tprint(
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
            reddit,
            failed_recipients_list,
            reward_codes_list,
            version_string,
            gold_coin_reward,
        )
