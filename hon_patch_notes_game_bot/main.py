#!/usr/bin/python
import praw
import time

from hon_patch_notes_game_bot.core import Core
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile
from hon_patch_notes_game_bot.config.config import (
    submission_title,
    community_submission_title,
    SLEEP_INTERVAL_SECONDS,
    SUBREDDIT_NAME,
    game_end_time,
    NUM_WINNERS,
)
from hon_patch_notes_game_bot.util import (
    is_game_expired,
    output_winners_list_to_file,
    generate_submission_compiled_patch_notes_template_line,
)


# ============
# Constants
# ============
BOT_USERNAME = "hon-bot"
USER_AGENT = "HoN Patch Notes Game Bot by /u/hon-bot"
PATCH_NOTES_PATH = "config/patch_notes.txt"
SUBMISSION_CONTENT_PATH = "config/submission_content.md"
COMMUNITY_SUBMISSION_CONTENT_PATH = "config/community_patch_notes_compilation.md"
OUTPUT_FILE_PATH = "cache/winners_list.txt"

patch_notes_file = PatchNotesFile(PATCH_NOTES_PATH)


def processed_submission_content(submission_content_path, patch_notes_file):
    """
    Reads the submission_content.md file, then uses data from a PatchNotesFile instance to further process it

    Returns:
        A processed string containing the submission content
    """
    with open(submission_content_path, "r") as file:
        submission_content = file.read()
        submission_content = submission_content.replace(
            "`patch_version`", patch_notes_file.get_version_string()
        )
        submission_content = submission_content.replace(
            "`max_line_count`", str(patch_notes_file.get_total_line_count())
        )

        return submission_content


def processed_community_notes_thread_submission_content(
    submission_content_path, patch_notes_file, main_submission_url
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

        submission_content += "\n\n# Community-compiled Patch Notes\n\nThe patch notes compiled by the community will automatically be updated below:\n\n"  # noqa: E501
        for line_number in range(1, patch_notes_file.get_total_line_count() + 1):
            submission_content += generate_submission_compiled_patch_notes_template_line(
                line_number=line_number
            )

        submission_content += f"\n\n**Guesses in this thread will not be responded to by the bot. [Visit the main thread instead!]({main_submission_url})**"
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
            title=submission_title, selftext=submission_content
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
            title=community_submission_title, selftext=community_submission_content,
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
    # Indefinite loop to listen to unread comment messages on Reddit
    # ===============================================================
    print("Reddit Bot's core loop started")
    while True:
        core = Core(
            reddit=reddit,
            db=database,
            submission=submission,
            community_submission=community_submission,
            patch_notes_file=patch_notes_file,
        )
        core.loop()

        # Stop indefinite loop if current time is greater than the closing time.
        if is_game_expired(game_end_time):
            break

        # Time to wait before calling the Reddit API again (in seconds)
        time.sleep(SLEEP_INTERVAL_SECONDS)

    # ========================
    # Bot end script actions
    # ========================
    print("Reddit Bot script ended via time deadline")
    output_winners_list_to_file(
        db_path=database.db_path,
        output_file_path=OUTPUT_FILE_PATH,
        num_winners=NUM_WINNERS,
    )
    print(f"Winners list successfully output to: {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    main()
