#!/usr/bin/python
import praw
import time

from hon_patch_notes_game_bot.core import Core
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile
from hon_patch_notes_game_bot.config.config import (
    submission_title,
    SLEEP_INTERVAL_SECONDS,
    SUBREDDIT_NAME,
    game_end_time,
    NUM_WINNERS,
)
from hon_patch_notes_game_bot.util import is_game_expired, output_winners_list_to_file


# ============
# Constants
# ============
BOT_USERNAME = "hon-bot"
USER_AGENT = "HoN Patch Notes Game Bot by /u/hon-bot"
PATCH_NOTES_PATH = "config/patch_notes.txt"
SUBMISSION_CONTENT_PATH = "config/submission_content.md"
OUTPUT_FILE_PATH = "cache/winners_list.txt"

patch_notes_file = PatchNotesFile(PATCH_NOTES_PATH)

# Process submission content
with open(SUBMISSION_CONTENT_PATH, "r") as file:
    submission_content = file.read()
    submission_content = submission_content.replace(
        "`patch_version`", patch_notes_file.get_version_string()
    )
    submission_content = submission_content.replace(
        "`max_line_count`", str(patch_notes_file.get_total_line_count())
    )


def main():
    """
    Main method for the Reddit bot/script
    """

    # Initialize bot by creating reddit & subreddit instances
    reddit = praw.Reddit(BOT_USERNAME, user_agent=USER_AGENT)
    reddit.validate_on_submit = True
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    # Initialize database
    database = Database()

    submission = None
    submission_url = database.get_submission_url()

    # Get Submission instance
    if submission_url is None:
        # Create thread if submission does not exist
        submission = subreddit.submit(
            title=submission_title, selftext=submission_content
        )
        database.insert_submission_url(submission.url)
    else:
        # Obtain submission via URL
        submission = reddit.submission(url=submission_url)

    # ===============================================================
    # Indefinite loop to listen to unread comment messages on Reddit
    # ===============================================================
    print("Bot's core loop started")
    while True:
        core = Core(
            reddit=reddit,
            db=database,
            submission=submission,
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
    print("Bot script ended via time deadline")
    output_winners_list_to_file(
        db_path=database.db_path,
        output_file_path=OUTPUT_FILE_PATH,
        num_winners=NUM_WINNERS,
    )
    print(f"Winners list successfully output to: {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    main()
