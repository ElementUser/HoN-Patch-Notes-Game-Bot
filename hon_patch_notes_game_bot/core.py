#!/usr/bin/python
"""
This module contains the bot's core loop and most of the logic in its "engine".

PRAW Comment API: https://praw.readthedocs.io/en/latest/code_overview/models/comment.html
"""
import time

from prawcore.exceptions import ServerError
from praw import Reddit
from praw.exceptions import RedditAPIException
from praw.models import Comment, Redditor, Submission
import typing

from hon_patch_notes_game_bot.communications import (
    send_message_to_staff,
    send_message_to_winners,
)
from hon_patch_notes_game_bot.database import Database
from hon_patch_notes_game_bot.patch_notes_file_handler import PatchNotesFile
from hon_patch_notes_game_bot.user import RedditUser
from hon_patch_notes_game_bot.utils import (
    get_patch_notes_line_number,
    generate_submission_compiled_patch_notes_template_line,
    get_reward_codes_list,
    is_game_expired,
    output_winners_list_to_file,
    tprint,
)
from hon_patch_notes_game_bot.config.config import (
    BLANK_LINE_REPLACEMENT,
    DISALLOWED_USERS_SET,
    GAME_END_TIME,
    GOLD_COIN_REWARD,
    INVALID_LINE_STRINGS,
    MAX_NUM_GUESSES,
    MAX_PERCENT_OF_LINES_REVEALED,
    MIN_COMMENT_KARMA,
    MIN_LINK_KARMA,
    MIN_ACCOUNT_AGE_DAYS,
    NUM_WINNERS,
    STAFF_RECIPIENTS_LIST,
    WINNERS_LIST_FILE_PATH,
    REWARD_CODES_FILE_PATH,
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
        self.reward_codes_filepath = REWARD_CODES_FILE_PATH
        self.game_end_time = GAME_END_TIME

    def has_exceeded_revealed_line_count(self) -> bool:
        """
        Checks if the number of revealed lines exceeds the max allowed revealed line count

        Returns True if the line count has been exceeded
        Returns False otherwise
        """

        b_line_count_exceeded = self.db.get_entry_count_in_patch_notes_line_tracker() >= (
            (MAX_PERCENT_OF_LINES_REVEALED / 100)
            * self.patch_notes_file.get_total_line_count()
        )
        if b_line_count_exceeded:
            tprint(
                "Number of revealed lines exceeds the max allowed revealed line count."
            )

        return b_line_count_exceeded

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
        except RedditAPIException as redditErr:
            tprint(f"Unable to reply (RedditAPIException): {redditErr}")
            return None
        except Exception as err:
            tprint(f"Unable to reply (general Exception): {err}")
            return None

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

    def perform_post_game_actions(self):
        """
        After the game ends, performs a series of operations.

        These operations currently include:
        - Generating the winners list
        - Saving the winners list to a file
        - Updating the main submission with the winners list content
        - Sending Private Messages to staff members & winners
        """
        # Save winners list in memory
        potential_winners_list = self.db.get_potential_winners_list()
        winners_list = self.db.get_random_winners_from_list(
            num_winners=NUM_WINNERS, potential_winners_list=potential_winners_list
        )

        # Save winners submission content to file
        winners_submission_content = output_winners_list_to_file(
            potential_winners_list=potential_winners_list,
            winners_list=winners_list,
            output_file_path=WINNERS_LIST_FILE_PATH,
        )
        tprint(f"Winners list successfully output to: {WINNERS_LIST_FILE_PATH}")

        # Update main submission with winner submission content at the top
        self.submission.edit(winners_submission_content + self.submission.selftext)
        tprint("Reddit submission successfully updated with the winners list info!")

        # Private messages
        version_string = self.patch_notes_file.get_version_string()
        send_message_to_staff(
            reddit=self.reddit,
            winners_list_path=WINNERS_LIST_FILE_PATH,
            staff_recipients=STAFF_RECIPIENTS_LIST,
            version_string=version_string,
            gold_coin_reward=GOLD_COIN_REWARD,
        )

        send_message_to_winners(
            reddit=self.reddit,
            winners_list=winners_list,
            reward_codes_list=get_reward_codes_list(self.reward_codes_filepath),
            version_string=version_string,
            gold_coin_reward=GOLD_COIN_REWARD,
        )

    def update_patch_notes_table_in_db(self, patch_notes_line_number: int) -> bool:
        """
        Attempts to update the patch notes table in the database

        Returns:
        - True, if the patch notes table was successfully updated
        - False, if the line number was already guessed & the patch notes table was not updated
        """
        # Invalid guess if the line number was already guessed
        if self.db.check_patch_notes_line_number(patch_notes_line_number):
            return False

        # Valid entry: add the guessed entry to the patch_notes_line_number table
        self.db.add_patch_notes_line_number(patch_notes_line_number)
        return True

    def process_guess_for_user(
        self,
        user: RedditUser,
        author: Redditor,
        unread_item: Comment,
        patch_notes_line_number: int,
    ) -> bool:
        """
        Processes the user's guess and performs the appropriate updates to various data sources
            (database, user and patch notes community thread) based on the validity of the guess.

        Returns:
        - True, if the game should continue
        - False, if the game's end condition is met.
        """
        line_content = self.patch_notes_file.get_content_from_line_number(
            patch_notes_line_number
        )

        # Invalid guess by getting a blank line in the patch notes
        if line_content is None:
            self.update_community_compiled_patch_notes_in_submission(
                patch_notes_line_number=patch_notes_line_number,
                line_content=BLANK_LINE_REPLACEMENT,
            )
            self.reply_with_bad_guess_feedback(
                user,
                author,
                unread_item,
                f"Whiffed! Line #{patch_notes_line_number} is blank.\n\n",
            )

            # Early exit checks/conditions
            if self.has_exceeded_revealed_line_count():
                return False
            return True

        # Only check for invalid strings if line_content is not empty
        # If the line content is correct, check other invalid strings for guessing
        for invalid_string in INVALID_LINE_STRINGS:
            if invalid_string in line_content:
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

                # Early exit checks/conditions
                if self.has_exceeded_revealed_line_count():
                    return False
                return True

        # If this code is reached, then the guess is valid!
        user.is_potential_winner = True
        self.update_community_compiled_patch_notes_in_submission(
            patch_notes_line_number=patch_notes_line_number, line_content=line_content,
        )

        # Reply to comment
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

        # Update user in DB
        self.db.update_user(user)

        # Early exit checks/conditions
        if self.has_exceeded_revealed_line_count():
            return False

        # All checks have been passed if this point is reached
        return True

    def process_game_rules_for_user(
        self,
        user: RedditUser,
        author: Redditor,
        unread_item: Comment,
        patch_notes_line_number: int,
    ) -> bool:
        """
        Processes the game's rules for a player.

        Returns:
        - True, if the game should continue
        - False, if the game's end condition is met.
        """

        # Prevent users who cannot make a guess from participating
        if not user.can_submit_guess:
            return True

        # Update user in DB after guess
        user.num_guesses += 1
        if user.num_guesses >= MAX_NUM_GUESSES:
            user.can_submit_guess = False
        self.db.update_user(user)

        # Update patch notes in DB
        if not self.update_patch_notes_table_in_db(patch_notes_line_number):
            # If update is unsuccessful, then respond and exit early (prevents 2x replies to the user)
            self.reply_with_bad_guess_feedback(
                user,
                author,
                unread_item,
                f"Line #{patch_notes_line_number} has already been guessed.\n\n",
            )
            return True

        if not self.process_guess_for_user(
            user, author, unread_item, patch_notes_line_number
        ):
            return False

        return True

    def loop(self):  # noqa: C901
        """
        Core loop of the bot

        Returns:
        - True, if the loop should continue running
        - False, if the loop should stop running
        """

        # Check unread replies
        try:
            # Stop indefinite loop if current time is greater than the closing time.
            if is_game_expired(self.game_end_time):
                return False

            for unread_item in self.reddit.inbox.unread(limit=None):
                unread_item.mark_read()

                # Only proceed with processing the unread item if it belongs to the current thread
                if (
                    isinstance(unread_item, Comment)
                    and unread_item.submission.id == self.submission.id
                ):
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

                    # Run the game rules, and exit early if game-ending conditions are met
                    if not self.process_game_rules_for_user(
                        user, author, unread_item, patch_notes_line_number
                    ):
                        return False

                    # Stop indefinite loop if current time is greater than the closing time.
                    if is_game_expired(self.game_end_time):
                        return False

            # After going through the bot's inbox, return True if inner loop stop functions are not met
            return True

        # Occasionally, Reddit may throw a 503 server error while under heavy load.
        # In that case, log the error & just wait and try again in the next loop cycle
        except ServerError as serverError:
            tprint(f"Server error encountered in core loop: {serverError}")
            sleep_time = 60
            tprint(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            return True  # main.py loop should continue after the sleep period

        # Handle remaining unforeseen exceptions and log the error
        except Exception as error:
            tprint(f"General exception encountered in core loop: {error}")
            sleep_time = 60
            tprint(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            return True  # main.py loop should continue after the sleep period
