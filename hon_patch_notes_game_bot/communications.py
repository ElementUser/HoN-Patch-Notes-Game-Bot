"""
This module contains functions related to communications across the Reddit platform
"""
import time
from praw.exceptions import RedditAPIException


def send_message_to_staff(
    reddit, winners_list_path, staff_recipients, version_string, gold_coin_reward
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
            f"Please send /u/FB-Saphirez a Private Message (PM) to request a code for {str(gold_coin_reward)} Gold Coins.\n\n"
            "Thank you for participating in the game! =)"
        )
        try:
            reddit.redditor(recipient).message(subject=subject_line, message=message)

        # Reddit API Exception
        except RedditAPIException as redditException:
            print(
                f"{redditException}\n{recipient} was not sent a message, continuing to next recipient"
            )

            # Rate limit error handling
            # Reference: https://github.com/GrafeasGroup/tor/blob/5ee21af7cc752abc6e7ae6aa47228105e6ec2e05/tor/core/helpers.py#L160-L171
            if redditException.error_type == "RATELIMIT":
                # Sleep for the rate limit duration
                totalLength = str(redditException.items[0].message).split(
                    "you are doing that too much. try again in ", 1
                )[1]
                minutesToSleep = totalLength[0].partition("minutes.")[0]
                secondsToSleep = int(minutesToSleep) * 60
                print("Sleeping for " + str(secondsToSleep) + " seconds")
                time.sleep(secondsToSleep)

            continue

        except Exception as error:
            print(
                f"{error}\n{recipient} was not sent a message, continuing to next recipient"
            )
            continue
