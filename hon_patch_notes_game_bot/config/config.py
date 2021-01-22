"""
This file will contain the bot script configuration that are most likely to change
"""


# ==========
# Variables
# ==========

# [GAME] 4.8.X - Patch Notes Guessing Game
submission_title = "[GAME] 4.9.1 - Patch Notes Guessing Game"
community_submission_title = "4.9.1 - Community-revealed Patch Notes"
game_end_time = "January 28, 2021, 4:00 am UTC"
gold_coin_reward = 300

# ================
# Other constants
# ================
SUBREDDIT_NAME = "heroesofnewerth"  # testingground4bots / heroesofnewerth
MAX_PERCENT_OF_LINES_REVEALED = 70  # Safety-oriented variable to ensure that the entire patch notes will not be revealed
MAX_NUM_GUESSES = 2
MIN_COMMENT_KARMA = 4
MIN_LINK_KARMA = 4
MIN_ACCOUNT_AGE_DAYS = 7
NUM_WINNERS = 15
SLEEP_INTERVAL_SECONDS = 10
STAFF_MEMBER_THAT_HANDS_OUT_REWARDS = "FB-Saphirez"

# ================
# Lists
# ================

# Disallowed users: use a set for the O(1) access time
disallowed_users_set = {
    "the_timezone_bot",
    "timee_bot",
    "generic_reddit_bot_2",
    "-koy",
    "rrreeddiitt",
}

# Recipients user list (for Private Messages) for the winners list
staff_recipients = ["ElementUser", "FB-Saphirez"]

# Invalid line strings (for guess validity in the game)
invalid_line_strings = ["_______", "-------"]
