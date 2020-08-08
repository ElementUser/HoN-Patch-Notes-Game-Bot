#!/usr/bin/python
import praw

def main():
    reddit = praw.Reddit('hon-bot', user_agent="HoN Patch Notes Game Bot by /u/hon-bot")
    subreddit = reddit.subreddit("HeroesofNewerth")

    patch_notes_url = "https://www.reddit.com/r/HeroesofNewerth/comments/huocgd/game_time_patch_version_485/"
    patch_notes_thread = reddit.submission(url=patch_notes_url)
    
if __name__ == "__main__":
    main()



