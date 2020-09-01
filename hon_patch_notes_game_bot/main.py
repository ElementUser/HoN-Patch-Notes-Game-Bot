#!/usr/bin/python
import praw, time
from praw.models import Comment
import database
from comment_parser import get_patch_notes_line_number
from patch_notes_file_handler import PatchNotesFile
from user import RedditUser
from util import safe_comment_reply

# ===========================================================
# Input variables for the program - change these when needed
# ===========================================================
patch_version = "4.8.5"
submission_title = "[TEST] Thread 3"

# ============
# Constants
# ============
BOT_USERNAME = "hon-bot"
USER_AGENT = "HoN Patch Notes Game Bot by /u/hon-bot"
SUBREDDIT_NAME = "testingground4bots"
MAX_NUM_GUESSES = 2
MIN_COMMENT_KARMA = 5
PATCH_NOTES_PATH = "patch_notes.txt"
SLEEP_INTERVAL_SECONDS = 5

patch_notes_file = PatchNotesFile(PATCH_NOTES_PATH)

# Submission content
with open("submission_content.md", "r") as file:
    # Replace variables in submission_content before posting it
    submission_content = file.read()
    submission_content = submission_content.replace("`patch_version`", patch_version)
    submission_content = submission_content.replace(
        "`max_line_count`", str(patch_notes_file.getTotalLineCount())
    )


def main():
    """
    Main method for the Reddit bot/script
    """

    # Initialize bot by creating reddit & subreddit instances
    reddit = praw.Reddit(BOT_USERNAME, user_agent=USER_AGENT)

    reddit.validate_on_submit = True
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    submission = None
    submission_url = database.get_submission_url()

    # Get Submission instance
    if submission_url is None:
        # Create thread if submission does not exist
        submission = subreddit.submit(
            title=submission_title, selftext=submission_content
        )
        database.db.table("submission").insert({"url": submission.url})
    else:
        # Obtain submission via URL
        submission = reddit.submission(url=submission_url)

    # Listen to unread messages from comments made in this submission thread
    inbox = reddit.inbox

    # =====================================================
    # Indefinite loop to listen to unread comment messages
    # =====================================================
    while True:
        # Check unread replies
        for unread_item in reddit.inbox.unread(limit=None):
            # Only proceed with processing the unread item if it is a comment & if the comment's submission.id matches the current submission.id
            if isinstance(unread_item, Comment):
                unread_item.mark_read()
                if unread_item.submission.id == submission.id:
                    author = unread_item.author

                    # Deter Reddit throwaway accounts from participating
                    if author.comment_karma < MIN_COMMENT_KARMA:
                        continue

                    # Get number from patch notes
                    patch_notes_line_number = get_patch_notes_line_number(
                        unread_item.body
                    )
                    if patch_notes_line_number is None:
                        continue

                    # Get author user id & search for it in the Database
                    user_id = author.id
                    user = None

                    # Get user
                    if database.user_exists(user_id):
                        db_user = database.get_user(user_id)
                        user = RedditUser(
                            id=db_user["id"],
                            name=db_user["name"],
                            can_submit_guess=db_user["can_submit_guess"],
                            is_potential_winner=db_user["is_potential_winner"],
                            num_guesses=db_user["num_guesses"],
                        )
                    else:
                        # Make a user with default attributes and add it to the database
                        user = RedditUser(id=author.id, name=author.name)
                        database.add_user(user)

                    # Now that we have the user, run the game rules
                    if not user.can_submit_guess:
                        continue

                    else:
                        user.num_guesses = user.num_guesses + 1
                        if user.num_guesses >= MAX_NUM_GUESSES:
                            user.can_submit_guess = False

                        # Check if entry was already guessed
                        if database.check_patch_notes_line_number(
                            patch_notes_line_number
                        ):
                            user.can_submit_guess = False
                            safe_comment_reply(
                                unread_item,
                                f"Sorry {author.name}, you didn't use Ctrl+F like the rules told you to & you guessed a patch line number that already exists. \n\nYou are now disqualified from this thread. Better luck next time!",
                            )
                            # Update user in DB
                            database.db.table("user").update(vars(user))
                            continue

                        else:
                            database.add_patch_notes_line_number(
                                patch_notes_line_number
                            )
                            line_content = patch_notes_file.getContentFromLineNumber(
                                patch_notes_line_number
                            )

                            if line_content is None:
                                if user.can_submit_guess:
                                    safe_comment_reply(
                                        unread_item,
                                        f"Whiffed! \n\n{author.name}, you have {MAX_NUM_GUESSES - user.num_guesses} guess(es) left! Try guessing another line number.",
                                    )
                                else:
                                    safe_comment_reply(
                                        unread_item,
                                        f"Sorry {author.name}, you have used all of your guesses. Better luck next time!",
                                    )
                            else:
                                user.can_submit_guess = False
                                user.is_potential_winner = True
                                unread_item.reply(
                                    f">{line_content} \n\nCongratulations for correctly guessing a patch note line, {author.name}!\n\nYou can now potentially receive a prize once this contest is over (see the main post for more details)!"
                                )

                            # Update user in DB
                            database.db.table("user").update(vars(user))

        # Time to wait before calling the Reddit API again (in seconds)
        time.sleep(SLEEP_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
