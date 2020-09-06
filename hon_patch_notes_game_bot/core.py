"""
This module contains the bot's core loop

PRAW Comment API: https://praw.readthedocs.io/en/latest/code_overview/models/comment.html
"""
from prawcore.exceptions import ServerError
from praw.exceptions import RedditAPIException
from praw.models import Comment
import time
from hon_patch_notes_game_bot.user import RedditUser
from hon_patch_notes_game_bot.util import (
    get_patch_notes_line_number,
    generate_submission_compiled_patch_notes_template_line,
)
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.config.config import (
    MIN_COMMENT_KARMA,
    MAX_NUM_GUESSES,
    MIN_ACCOUNT_AGE_DAYS,
    disallowed_users_set,
)


class Core:
    def __init__(
        self,
        db: Database,
        reddit,
        submission,
        community_submission,
        patch_notes_file: str,
    ) -> None:
        """
        Parametrized constructor
        """

        self.reddit = reddit
        self.db = db
        self.submission = submission
        self.community_submission = community_submission
        self.patch_notes_file = patch_notes_file

    def reply_with_bad_guess_feedback(
        self, user, author, comment, first_line: str
    ) -> None:
        """
        Replies to a comment with feedback for a bad guess

        Attributes:
            user: the RedditUser instance that owns the comment
            comment: the praw Comment model instance to respond to
            first_line: the first line in the reply content
        """
        if user.can_submit_guess:
            self.safe_comment_reply(
                comment,
                f"{first_line}\n\n"
                f"{author.name}, you have {MAX_NUM_GUESSES - user.num_guesses} guess(es) left!\n\n"
                "Try guessing another line number.",
            )
        else:
            self.safe_comment_reply(
                comment,
                f"{first_line} \n\n"
                f"Sorry {author.name}, you have used all of your guesses.\n\n"
                "Better luck next time!",
            )

    def get_user_from_database(self, author):
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

    def safe_comment_reply(self, comment, text_body: str):
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

    def is_account_too_new(self, Redditor, days):
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
        return Redditor.created_utc > (time.time() - (days * DAYS_TO_SECONDS))

    def update_community_compiled_patch_notes_in_submission(
        self, patch_notes_line_number, line_content
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

    def is_disallowed_to_post(self, Redditor):
        """
        Checks if a Redditor is disallowed to post based on their account stats

        Returns:
            True if they are disallowed to post
            False if their post should be examined further
        """

        # Do not process posts from disallowed users
        if Redditor.name in disallowed_users_set:
            return True

        # Deter Reddit throwaway accounts from participating
        if not Redditor.has_verified_email:
            return True

        if Redditor.comment_karma < MIN_COMMENT_KARMA:
            return True

        if self.is_account_too_new(Redditor=Redditor, days=MIN_ACCOUNT_AGE_DAYS):
            return True

        return False

    def loop(self):  # noqa: C901
        """
        Core loop of the bot
        """

        # Check unread replies
        try:
            for unread_item in self.reddit.inbox.unread(limit=None):
                # Only proceed with processing the unread item if it belongs to the current thread
                if isinstance(unread_item, Comment):
                    unread_item.mark_read()
                    if unread_item.submission.id == self.submission.id:
                        author = unread_item.author

                        # Exit loop early if the user does not meet the posting conditions
                        if self.is_disallowed_to_post(author):
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
                            user.num_guesses = user.num_guesses + 1
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
                                self.db.add_patch_notes_line_number(
                                    patch_notes_line_number
                                )
                                line_content = self.patch_notes_file.get_content_from_line_number(
                                    patch_notes_line_number
                                )

                                # Invalid guess by getting a blank line in the patch notes
                                if line_content is None:
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

                                # Valid guess!
                                else:
                                    user.can_submit_guess = False
                                    user.is_potential_winner = True

                                    # Update community compiled patch notes in submission
                                    self.update_community_compiled_patch_notes_in_submission(
                                        patch_notes_line_number=patch_notes_line_number,
                                        line_content=line_content,
                                    )

                                    self.safe_comment_reply(
                                        unread_item,
                                        f"Congratulations for correctly guessing a patch note line, {author.name}!\n\n"
                                        f"Line #{patch_notes_line_number} from the patch notes is the following:\n\n"
                                        f">{line_content}\n"
                                        "You have been added to the pool of potential winners & can win a prize once this contest is over!\n\n"  # noqa: E501
                                        "See the main post for more details for potential prizes.\n\n___\n\n"
                                        "The community-compiled patch notes have been updated with your valid entry.\n\n"
                                        f"[Click here to see the current status of the community-compiled patch notes!]({self.community_submission.url})",  # noqa: E501
                                    )

                                # Update user in DB
                                self.db.update_user(user)

        # Occasionally, Reddit may throw a 503 server error while under heavy load.
        # In that case, log the error & just wait and try again in the next loop cycle
        except ServerError as error:
            print(error)
            time.sleep(60)

