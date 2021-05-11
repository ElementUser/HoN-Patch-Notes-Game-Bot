#!/usr/bin/python
import praw
import time

from hon_patch_notes_game_bot.core import Core
from hon_patch_notes_game_bot.communications import init_submissions
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile
from hon_patch_notes_game_bot.config.config import (
    BOT_USERNAME,
    COMMUNITY_SUBMISSION_CONTENT_PATH,
    PATCH_NOTES_PATH,
    SLEEP_INTERVAL_SECONDS,
    SUBREDDIT_NAME,
    SUBMISSION_CONTENT_PATH,
    USER_AGENT,
)


def main():
    """
    Main method for the Reddit bot/script
    """

    # Initialize bot by creating reddit & subreddit instances
    reddit = praw.Reddit(BOT_USERNAME, user_agent=USER_AGENT)
    reddit.validate_on_submit = True
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    # Initialize other variables
    database = Database()
    patch_notes_file = PatchNotesFile(PATCH_NOTES_PATH)

    # Initialize submissions (i.e. Reddit threads)
    submission, community_submission = init_submissions(
        reddit,
        subreddit,
        database,
        patch_notes_file,
        SUBMISSION_CONTENT_PATH,
        COMMUNITY_SUBMISSION_CONTENT_PATH,
    )

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
