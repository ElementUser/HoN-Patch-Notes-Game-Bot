#!/usr/bin/python
import praw
from hon_patch_notes_game_bot.database import get_submission_url, db

# Input variables for the program - change these when needed
submission_title = "[TEST] Thread 1"

# Submission content
with open("submission_content.md", "r") as file:
    submission_content = file.read()


def main():
    """
    Main method for the Reddit bot/script
    """

    # Initialize bot by creating reddit & subreddit instances
    reddit = praw.Reddit("hon-bot", user_agent="HoN Patch Notes Game Bot by /u/hon-bot")
    reddit.validate_on_submit = True
    subreddit = reddit.subreddit("testingground4bots")

    submission = None
    submission_url = get_submission_url()

    # Get Submission instance
    if submission_url is None:
        # Create thread if submission does not exist
        submission = subreddit.submit(
            title=submission_title, selftext=submission_content
        )
        db.table("submission").insert({"url": submission.url})
    else:
        # Obtain submission via URL
        submission = reddit.submission(url=submission_url)

    # Listen to unreads


if __name__ == "__main__":
    main()
