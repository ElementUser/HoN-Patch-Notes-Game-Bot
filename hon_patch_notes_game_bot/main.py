#!/usr/bin/python
import praw
import time

from hon_patch_notes_game_bot.core import Core
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile
from hon_patch_notes_game_bot.config.config import (
    submission_title,
    MIN_COMMENT_KARMA,
    SLEEP_INTERVAL_SECONDS,
    SUBREDDIT_NAME,
    MAX_NUM_GUESSES,
)

# ============
# Constants
# ============
BOT_USERNAME = "hon-bot"
USER_AGENT = "HoN Patch Notes Game Bot by /u/hon-bot"
PATCH_NOTES_PATH = "config/patch_notes.txt"
SUBMISSION_CONTENT_PATH = "config/submission_content.md"

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
            min_comment_karma=MIN_COMMENT_KARMA,
            max_num_guesses=MAX_NUM_GUESSES,
            patch_notes_file=patch_notes_file,
        )
        core.loop()

        # TODO: Stop script if current time is greater than the closing time.

        # Time to wait before calling the Reddit API again (in seconds)
        time.sleep(SLEEP_INTERVAL_SECONDS)

    print("Bot script ended via time deadline")


if __name__ == "__main__":
    main()
