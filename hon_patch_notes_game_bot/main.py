#!/usr/bin/python
import praw
import time

from hon_patch_notes_game_bot.core import Core
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile
from hon_patch_notes_game_bot.config.config import (
    BOT_USERNAME,
    COMMUNITY_SUBMISSION_CONTENT_PATH,
    COMMUNITY_SUBMISSION_TITLE,
    GAME_END_TIME,
    GOLD_COIN_REWARD,
    MAX_NUM_GUESSES,
    MAX_PERCENT_OF_LINES_REVEALED,
    NUM_WINNERS,
    PATCH_NOTES_PATH,
    SLEEP_INTERVAL_SECONDS,
    STAFF_RECIPIENTS_LIST,
    SUBMISSION_CONTENT_PATH,
    SUBMISSION_TITLE,
    SUBREDDIT_NAME,
    USER_AGENT,
    WINNERS_LIST_FILE_PATH,
)
from hon_patch_notes_game_bot.util import (
    is_game_expired,
    output_winners_list_to_file,
    generate_submission_compiled_patch_notes_template_line,
    convert_time_string_to_wolframalpha_query_url,
)
from hon_patch_notes_game_bot.communications import (
    send_message_to_staff,
    send_message_to_winners,
)

patch_notes_file = PatchNotesFile(PATCH_NOTES_PATH)
version_string = patch_notes_file.get_version_string()


def processed_submission_content(
    submission_content_path: str, patch_notes_file: PatchNotesFile
):
    """
    Reads the submission_content.md file, then uses data from a PatchNotesFile instance to further process it

    Returns:
        A processed string containing the submission content
    """
    with open(submission_content_path, "r") as file:
        submission_content = file.read()

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
):
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


def main():  # noqa: C901
    """
    Main method for the Reddit bot/script
    """

    # Initialize bot by creating reddit & subreddit instances
    reddit = praw.Reddit(BOT_USERNAME, user_agent=USER_AGENT)
    reddit.validate_on_submit = True
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    # Initialize database
    database = Database()

    # =========================
    # Process main submission
    # =========================
    submission_content = processed_submission_content(
        SUBMISSION_CONTENT_PATH, patch_notes_file
    )
    submission = None
    submission_url = database.get_submission_url(tag="main")

    # Get main thread Submission instance
    if submission_url is None:
        # Create thread if submission does not exist
        submission = subreddit.submit(
            title=SUBMISSION_TITLE, selftext=submission_content
        )
        database.insert_submission_url("main", submission.url)
        submission_url = submission.url
    else:
        # Obtain submission via URL
        submission = reddit.submission(url=submission_url)

    # =========================================
    # Process community patch notes submission
    # =========================================
    community_submission_content = processed_community_notes_thread_submission_content(
        COMMUNITY_SUBMISSION_CONTENT_PATH, patch_notes_file, submission_url
    )
    community_submission = None
    community_submission_url = database.get_submission_url(tag="community")

    # Get community thread Submission instance
    if community_submission_url is None:
        # Create thread if submission does not exist
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

    # ===============================================================
    # Core loop to listen to unread comment messages on Reddit
    # ===============================================================
    print("Reddit Bot's core loop started")
    while 1:
        core = Core(
            reddit=reddit,
            db=database,
            submission=submission,
            community_submission=community_submission,
            patch_notes_file=patch_notes_file,
        )
        if not core.loop():
            print("Reddit Bot script ended via core loop end conditions")
            break

        # Stop indefinite loop if current time is greater than the closing time.
        if is_game_expired(GAME_END_TIME):
            print("Reddit Bot script ended via time deadline")
            break

        # Time to wait before calling the Reddit API again (in seconds)
        time.sleep(SLEEP_INTERVAL_SECONDS)

    # ========================
    # Bot end script actions
    # ========================
    print("Performing actions after the game has ended...")
    core.perform_post_game_actions()
    print("Reddit bot script ended gracefully")


if __name__ == "__main__":
    main()
