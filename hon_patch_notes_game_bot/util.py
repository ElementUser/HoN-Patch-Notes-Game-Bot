import praw


def safe_comment_reply(comment, message):
    try:
        comment.reply(message)
    except praw.RedditAPIException:
        pass
