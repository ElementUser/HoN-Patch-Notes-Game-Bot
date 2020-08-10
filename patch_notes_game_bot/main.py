#!/usr/bin/python
import praw


def main():
    """
    Main method for the Reddit bot/script
    """

    reddit = praw.Reddit("hon-bot", user_agent="HoN Patch Notes Game Bot by /u/hon-bot")
    subreddit = reddit.subreddit("HeroesofNewerth")

    patch_notes_url = "https://www.reddit.com/r/HeroesofNewerth/comments/huocgd/game_time_patch_version_485/"
    patch_notes_thread = reddit.submission(url=patch_notes_url)

    forest_comments = patch_notes_thread.comments

    for comment in forest_comments:
        print(comment.body)


if __name__ == "__main__":
    main()
