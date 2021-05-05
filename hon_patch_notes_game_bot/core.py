"""
This module contains the bot's core loop

PRAW Comment API: https://praw.readthedocs.io/en/latest/code_overview/models/comment.html
"""
import time

from prawcore.exceptions import ServerError
from praw import Reddit
from praw.exceptions import RedditAPIException
from praw.models import Comment, Redditor, Submission
import typing

from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile
from hon_patch_notes_game_bot.user import RedditUser
from hon_patch_notes_game_bot.util import (
    get_patch_notes_line_number,
    generate_submission_compiled_patch_notes_template_line,
)
from hon_patch_notes_game_bot.config.config import (
    MIN_COMMENT_KARMA,
    MIN_LINK_KARMA,
    MAX_NUM_GUESSES,
    MIN_ACCOUNT_AGE_DAYS,
    MAX_PERCENT_OF_LINES_REVEALED,
    DISALLOWED_USERS_SET,
    INVALID_LINE_STRINGS,
)


class Core:
    def __init__(
        self,
        db: Database,
        reddit: Reddit,
        submission: Submission,
        community_submission: Submission,
        patch_notes_file: PatchNotesFile,
    ):
        """
        Parametrized constructor
        """

        self.reddit = reddit
        self.db = db
        self.submission = submission
        self.community_submission = community_submission
        self.patch_notes_file = patch_notes_file

    def has_exceeded_revealed_line_count(self) -> bool:
        """
        Checks if the number of revealed lines exceeds the max allowed revealed line count

        Returns True if the line count has been exceeded
        Returns False otherwise
        """
        return self.db.get_entry_count_in_patch_notes_line_tracker() >= (
            (MAX_PERCENT_OF_LINES_REVEALED / 100)
            * self.patch_notes_file.get_total_line_count()
        )

    def reply_with_bad_guess_feedback(
        self, user: RedditUser, author: Redditor, comment: Comment, first_line: str,
    ):
        """
        Replies to a comment with feedback for a bad guess

        Attributes:
            user: the RedditUser instance that owns the comment
            comment: the praw Comment model instance to respond to
            first_line: the first line in the reply content
        """

        # User can still continue guessing
        if user.can_submit_guess:
            self.safe_comment_reply(
                comment,
                f"{first_line}\n\n"
                f"{author.name}, you have {MAX_NUM_GUESSES - user.num_guesses} guess(es) left!\n\n"
                "Try guessing another line number.",
            )

        # User cannot submit guesses anymore, but was a successful winner
        elif user.is_potential_winner:
            self.safe_comment_reply(
                comment,
                f"{first_line} \n\n"
                f"{author.name}, you have used all of your guesses.\n\n"
                "Based on one of your previous guesses, you are still entered into the pool of potential winners!",
            )
        else:
            self.safe_comment_reply(
                comment,
                f"{first_line} \n\n"
                f"Sorry {author.name}, you have used all of your guesses.\n\n"
                "Better luck next time!",
            )

    @typing.no_type_check  # Avoid this error: error: Value of type "Optional[Document]" is not indexable
    def get_user_from_database(self, author: Redditor) -> RedditUser:
        """
        Gets a RedditUser instance from the database if found

        If not found, creates the user and adds it to the database

        Attributes:
            author: a praw Author model instance

        Returns:
            A RedditUser instance
        """
        if self.db.user_exists(author.name):
            db_user = self.db.get_user(author.name)
            user = RedditUser(
                name=db_user["name"],
                can_submit_guess=db_user["can_submit_guess"],
                is_potential_winner=db_user["is_potential_winner"],
                num_guesses=db_user["num_guesses"],
            )
            return user
        else:
            # Make a user with default attributes and add it to the database
            user = RedditUser(name=author.name)
            self.db.add_user(user)
            return user

    def safe_comment_reply(self, comment: Comment, text_body: str):
        """
        Attempts to reply to a comment & safely handles a RedditAPIException
        (e.g. if that comment has been deleted & cannot be responded to)

        Attributes:
            comment: a praw Comment model instance
            text_body: the markdown text to include in the reply made
        """
        try:
            comment.reply(body=text_body)
        except RedditAPIException:
            pass
        except Exception:
            pass

    def is_account_too_new(self, redditor: Redditor, days: int) -> bool:
        """
        Checks if the Reddit account is too new to post

        Attributes:
            Redditor: a PRAW Redditor instance to check
            days: the number of days in the past to act as the threshold

        Returns:
            True if the account is too new to post
            False if the account is old enough to post
        """
        DAYS_TO_SECONDS = 86400
        return redditor.created_utc > (time.time() - (days * DAYS_TO_SECONDS))

    def update_community_compiled_patch_notes_in_submission(
        self, patch_notes_line_number: int, line_content: str
    ):
        """
        Edits the submission body & replaces the appropriate line number
        with the line content via string.rfind() & string slicing

        Attributes:
            patch_notes_line_number: the correct patch notes line number that has been guessed
            line_content: the content of the specified patch notes line number
        """
        submission_text = self.community_submission.selftext
        target_text = generate_submission_compiled_patch_notes_template_line(
            patch_notes_line_number
        )
        line_index = submission_text.rfind(target_text)

        # line_index is still the start index of target_text
        # To move to the end of line_index, increase index by len(target_text)
        line_index += len(target_text.rstrip())

        edited_submission_text = (
            submission_text[:line_index]
            + " "
            + line_content.rstrip()
            + submission_text[line_index:]
        )

        self.community_submission.edit(body=edited_submission_text)

    def is_disallowed_to_post(self, redditor: Redditor, comment: Comment) -> bool:
        """
        Checks if a Redditor is disallowed to post based on their account stats

        Attributes:
            redditor: a PRAW Redditor instance
            comment: a PRAW comment model instance to respond to

        Returns:
            True if they are disallowed to post
            False if their post should be examined further
        """

        # Do not process posts from disallowed users
        if redditor.name in DISALLOWED_USERS_SET:
            return True

        # Deter Reddit throwaway accounts from participating
        if not redditor.has_verified_email:
            self.safe_comment_reply(
                comment,
                f"Sorry {redditor.name}, your email is not verified on your account.\n\n"
                "Please try again after you have officially verified your email with Reddit!",
            )
            return True

        if (
            redditor.comment_karma < MIN_COMMENT_KARMA
            and redditor.link_karma < MIN_LINK_KARMA
        ):
            self.safe_comment_reply(
                comment,
                f"Sorry {redditor.name}, your link karma and your comment karma are too low.\n\n"
                "Please try again when you have legitimately raised your link and/or comment karma a bit!",
            )
            return True

        if self.is_account_too_new(redditor=redditor, days=MIN_ACCOUNT_AGE_DAYS):
            self.safe_comment_reply(
                comment,
                f"Sorry {redditor.name}, your account is too new.\n\n"
                "Please try again in the future!",
            )
            return True

        return False

    def fix_corrupted_community_submission_edit(self):
        """
        An emergency function in case editing the community submission ends up removing the corrupted data.

        This function searches for each template string line number in the submission,
        and then fills it with the line content according to the local database & current patch_notes.txt file
        """
        patch_notes_entries = self.db.get_all_entries_in_patch_notes_tracker()
        for entry in patch_notes_entries:
            line_number = entry["id"]
            line_content = self.patch_notes_file.get_content_from_line_number(
                line_number
            )
            if line_content is None:
                line_content = "..."

            self.update_community_compiled_patch_notes_in_submission(
                patch_notes_line_number=line_number, line_content=line_content
            )

    def loop(self):  # noqa: C901
        """
        Core loop of the bot

        Returns True if the loop should continue running, False otherwise
        """

        # Check unread replies
        try:
            should_continue_loop = True

            for unread_item in self.reddit.inbox.unread(limit=None):
                # Only proceed with processing the unread item if it belongs to the current thread
                if isinstance(unread_item, Comment):
                    unread_item.mark_read()
                    if unread_item.submission.id == self.submission.id:
                        author = unread_item.author

                        # Exit loop early if the user does not meet the posting conditions
                        if self.is_disallowed_to_post(author, unread_item):
                            continue

                        # Get patch notes line number from the user's post
                        patch_notes_line_number = get_patch_notes_line_number(
                            unread_item.body
                        )
                        if patch_notes_line_number is None:
                            continue

                        # Get author user id & search for it in the Database (add it if it doesn't exist)
                        user = self.get_user_from_database(author)

                        # ===================
                        # Run the game rules
                        # ===================

                        # Prevent users who cannot make a guess from participating
                        if not user.can_submit_guess:
                            continue

                        else:
                            user.num_guesses += 1
                            if user.num_guesses >= MAX_NUM_GUESSES:
                                user.can_submit_guess = False

                            # Invalid guess if the line number was already guessed
                            if self.db.check_patch_notes_line_number(
                                patch_notes_line_number
                            ):
                                self.reply_with_bad_guess_feedback(
                                    user,
                                    author,
                                    unread_item,
                                    f"Line #{patch_notes_line_number} has already been guessed.\n\n",
                                )

                                # Update user in DB
                                self.db.update_user(user)
                                continue

                            else:
                                # Add the guessed entry to the patch_notes_line_number table
                                self.db.add_patch_notes_line_number(
                                    patch_notes_line_number
                                )
                                line_content = self.patch_notes_file.get_content_from_line_number(
                                    patch_notes_line_number
                                )

                                # Boolean flag to check if the current guess is still considered valid
                                # Set to True initially & a series of checks to set it to False will occur right after this
                                is_valid_guess = True

                                # Invalid guess by getting a blank line in the patch notes
                                if line_content is None:
                                    is_valid_guess = False
                                    blank_line = "..."
                                    self.update_community_compiled_patch_notes_in_submission(
                                        patch_notes_line_number=patch_notes_line_number,
                                        line_content=blank_line,
                                    )
                                    self.reply_with_bad_guess_feedback(
                                        user,
                                        author,
                                        unread_item,
                                        f"Whiffed! Line #{patch_notes_line_number} is blank.\n\n",
                                    )
                                    should_continue_loop = (
                                        not self.has_exceeded_revealed_line_count()
                                    )

                                # Only check for invalid strings if line_content is not empty
                                else:
                                    # If the line content is correct, check other invalid strings for guessing
                                    for invalid_string in INVALID_LINE_STRINGS:
                                        if invalid_string in line_content:
                                            is_valid_guess = False
                                            self.update_community_compiled_patch_notes_in_submission(
                                                patch_notes_line_number=patch_notes_line_number,
                                                line_content=line_content,
                                            )
                                            self.reply_with_bad_guess_feedback(
                                                user,
                                                author,
                                                unread_item,
                                                f"Whiffed! Line #{patch_notes_line_number} contains an invalid string entry."
                                                "\n\nIt contains the following invalid string:\n\n"
                                                f">{invalid_string}\n\n",
                                            )
                                            should_continue_loop = (
                                                not self.has_exceeded_revealed_line_count()
                                            )
                                            break

                                # Valid guess!
                                if is_valid_guess:
                                    user.is_potential_winner = True

                                    # Update community compiled patch notes in submission
                                    self.update_community_compiled_patch_notes_in_submission(
                                        patch_notes_line_number=patch_notes_line_number,
                                        line_content=line_content,
                                    )

                                    if user.can_submit_guess:
                                        self.safe_comment_reply(
                                            unread_item,
                                            f"Congratulations for correctly guessing a patch note line, {author.name}!\n\n"
                                            f"Line #{patch_notes_line_number} from the patch notes is the following:\n\n"
                                            f">{line_content}\n"
                                            "You have been added to the pool of potential winners & can win a prize once this contest is over!\n\n"  # noqa: E501
                                            "See the main post for more details for potential prizes.\n\n___\n\n"
                                            f"You have {MAX_NUM_GUESSES - user.num_guesses} guess(es) left!\n\n"
                                            "The community-compiled patch notes have been updated with your valid entry.\n\n"
                                            f"[Click here to see the current status of the community-compiled patch notes!]({self.community_submission.url})",  # noqa: E501
                                        )
                                    else:
                                        self.safe_comment_reply(
                                            unread_item,
                                            f"Congratulations for correctly guessing a patch note line, {author.name}!\n\n"
                                            f"Line #{patch_notes_line_number} from the patch notes is the following:\n\n"
                                            f">{line_content}\n"
                                            "You have been added to the pool of potential winners & can win a prize once this contest is over!\n\n"  # noqa: E501
                                            "See the main post for more details for potential prizes.\n\n___\n\n"
                                            f"{author.name}, you have used all of your guesses.\n\n"
                                            "The community-compiled patch notes have been updated with your valid entry.\n\n"
                                            f"[Click here to see the current status of the community-compiled patch notes!]({self.community_submission.url})",  # noqa: E501
                                        )

                                    should_continue_loop = (
                                        not self.has_exceeded_revealed_line_count()
                                    )

                                # Update user in DB
                                self.db.update_user(user)

            # After going through the bot's inbox, return whether the loop should continue or not back to main.py
            return should_continue_loop

        # Occasionally, Reddit may throw a 503 server error while under heavy load.
        # In that case, log the error & just wait and try again in the next loop cycle
        except ServerError as serverError:
            print(serverError)
            sleep_time = 60
            print(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            return True  # main.py loop should continue after the sleep period

        # Handle remaining unforeseen exceptions and log the error
        except Exception as error:
            print(error)
            sleep_time = 60
            print(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            return True  # main.py loop should continue after the sleep period
