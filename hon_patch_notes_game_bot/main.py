#!/usr/bin/python
import praw

# Input variables for the program - change these when needed
patch_notes_url = "https://www.reddit.com/r/HeroesofNewerth/comments/huocgd/game_time_patch_version_485/"


def main():
    """
    Main method for the Reddit bot/script
    """

    reddit = praw.Reddit("hon-bot", user_agent="HoN Patch Notes Game Bot by /u/hon-bot")
    subreddit = reddit.subreddit("HeroesofNewerth")

    patch_notes_thread = reddit.submission(url=patch_notes_url)

    # Get comments from the Reddit thread
    patch_notes_thread.comments.replace_more(limit=None)

    #========================================================
    # Scan through comments that already exist in the thread
    #========================================================

    # This code block iterates through each topLevelComment, and then iterates through each topLevelComment's comment tree
    for topLevelComment in patch_notes_thread.comments:
        print(topLevelComment.author)

        # Dive into the topLevelComment's comment tree
        comment_queue = topLevelComment.replies[:]  # Seed with top-level comment
        while comment_queue:
            comment = comment_queue.pop(0)
            print(comment.author)
            comment_queue.extend(comment.replies)

    # for topLevelComment in patch_notes_thread.comments:
    #     # Save top level comment to compare potential deeper comments in the tree with
    #     topLevelAuthor = topLevelComment.author
    #     print(topLevelAuthor)

        # TODO: Check if the top level comment can still guess. This will be a DB check of some kind.

        # If they can't, then continue to the next topLevelComment in the list. Otherwise, parse their comment for a number.

            # If no integer can be found, then continue to the next topLevelComment

            # Otherwise, if an integer is found:
            # Check to see if the commenter is the same as the topLevelAuthor and is a response to one of this bot's messages. If it is, then proceed with parsing (but otherwise, continue to the next top level comment)

            # Check to see if the line number has been guessed already & the 

                # If the line number has been guessed already, immediately mark the player as unable to guess. Do not give them another chance to guess in this thread.

                # Otherwise, check to see if the line gets valid content from the patch notes file.

                    # If it does get valid content, then mark the user as a potential winner
                        # After marking their scoring status, respond to the comment with the user's scoring status
                        # Then continue to the next topLevelComment

                    # Otherwise, mark it as a failed attempt & update the user's scoring status appropriately.
                        # After marking their scoring status, respond to the comment with the user's scoring status
                        # Then continue to the next topLevelComment
                    


if __name__ == "__main__":
    main()
