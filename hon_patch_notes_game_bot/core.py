"""
This module contains the bot's core loop

PRAW Comment API: https://praw.readthedocs.io/en/latest/code_overview/models/comment.html
"""

from praw.exceptions import RedditAPIException
from praw.models import Comment
from hon_patch_notes_game_bot.user import RedditUser
from hon_patch_notes_game_bot.util import get_patch_notes_line_number
from hon_patch_notes_game_bot.database import Database


class Core:
    def __init__(
        self,
        db: Database,
        reddit,
        submission,
        min_comment_karma: int,
        max_num_guesses: int,
        patch_notes_file: str,
    ) -> None:
        """
        Parametrized constructor
        """

        self.reddit = reddit
        self.db = db
        self.submission = submission
        self.min_comment_karma = min_comment_karma
        self.max_num_guesses = max_num_guesses
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
                f"{author.name}, you have {self.max_num_guesses - user.num_guesses} guess(es) left!\n\n"
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

    def loop(self):
        """
        Core loop of the bot
        """

        # Check unread replies
        for unread_item in self.reddit.inbox.unread(limit=None):
            # Only proceed with processing the unread item if it belongs to the current thread
            if isinstance(unread_item, Comment):
                unread_item.mark_read()
                if unread_item.submission.id == self.submission.id:
                    author = unread_item.author

                    # Prevent Reddit throwaway accounts from participating
                    if author.comment_karma < self.min_comment_karma:
                        continue

                    # Get number from patch notes
                    patch_notes_line_number = get_patch_notes_line_number(
                        unread_item.body
                    )
                    if patch_notes_line_number is None:
                        continue

                    # Get author user id & search for it in the Database
                    user = self.get_user_from_database(author)

                    # ===================
                    # Run the game rules
                    # ===================

                    # Prevent users who cannot make a guess from participating
                    if not user.can_submit_guess:
                        continue

                    else:
                        user.num_guesses = user.num_guesses + 1
                        if user.num_guesses >= self.max_num_guesses:
                            user.can_submit_guess = False

                        # Check if entry was already guessed
                        if self.db.check_patch_notes_line_number(
                            patch_notes_line_number
                        ):
                            self.reply_with_bad_guess_feedback(
                                user,
                                author,
                                unread_item,
                                "This line number has already been guessed.\n\n",
                            )

                            # Update user in DB
                            self.db.update_user(user)
                            continue

                        else:
                            self.db.add_patch_notes_line_number(patch_notes_line_number)
                            line_content = self.patch_notes_file.get_content_from_line_number(
                                patch_notes_line_number
                            )

                            if line_content is None:
                                self.reply_with_bad_guess_feedback(
                                    user, author, unread_item, "Whiffed!\n\n",
                                )

                            else:
                                user.can_submit_guess = False
                                user.is_potential_winner = True
                                self.safe_comment_reply(
                                    unread_item,
                                    f"Congratulations for correctly guessing a patch note line, {author.name}!\n\n"
                                    "The line from the patch notes is the following:\n\n"
                                    f">{line_content}\n"
                                    "You have been added to the pool of potential winners & can win a prize once this contest is over!\n\n"  # noqa: E501
                                    "See the main post for more details.",
                                )

                            # Update user in DB
                            self.db.update_user(user)
