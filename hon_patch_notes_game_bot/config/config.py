"""
This file will contain the bot script configuration that are most likely to change
"""

# ==========
# Variables
# ==========

# [GAME] 4.9.X - Patch Notes Guessing Game
submission_title = "[GAME] 4.9.3 - Patch Notes Guessing Game"
community_submission_title = "4.9.3 - Community-revealed Patch Notes"
game_end_time = "May 15, 2021, 4:00 am UTC"

# ================
# Reward settings
# ================

gold_coin_reward = 300
NUM_WINNERS = 25

# ================
# Other constants
# ================
SUBREDDIT_NAME = "heroesofnewerth"  # testingground4bots / heroesofnewerth
MAX_PERCENT_OF_LINES_REVEALED = 66  # Safety-oriented variable to ensure that the entire patch notes will not be revealed
MAX_NUM_GUESSES = 2
MIN_COMMENT_KARMA = 4
MIN_LINK_KARMA = 4
MIN_ACCOUNT_AGE_DAYS = 7
SLEEP_INTERVAL_SECONDS = 10
STAFF_MEMBER_THAT_HANDS_OUT_REWARDS = "FB-Saphirez"

# ================
# Data structures
# ================

# Disallowed users: use a set for the O(1) access time
disallowed_users_set = {
    "ElementUser",
    "FB-Saphirez",
    "the_timezone_bot",
    "timee_bot",
    "generic_reddit_bot_2",
    "-koy",
    "-koy888",
    "rrreeddiitt",
    "diabetis_",
    "Apejohn",
}

# Recipients user list (for Private Messages) for the winners list
staff_recipients = ["ElementUser", "FB-Saphirez"]

# Invalid line strings (for guess validity in the game)
invalid_line_strings = ["_______", "-------"]
