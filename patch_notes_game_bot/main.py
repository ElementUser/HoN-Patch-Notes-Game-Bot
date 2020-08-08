#!/usr/bin/python
import praw

def main():
    reddit = praw.Reddit('hon-bot', user_agent="HoN Patch Notes Game Bot by /u/hon-bot")

    subreddit = reddit.subreddit("HeroesofNewerth")

    for submission in subreddit.hot(limit=5):
        print("Title: ", submission.title)
        print("Text: ", submission.selftext)
        print("Score: ", submission.score)
        print("---------------------------------\n")

if __name__ == "__main__":
    main()



