"""
This file will contain the bot script configuration that are most likely to change
"""


# ==========
# Variables
# ==========

# [GAME] 4.8.X - Patch Notes Guessing Game
submission_title = "[GAME] 4.8.6 - Patch Notes Guessing Game"
community_submission_title = "4.8.6: community-revealed Patch Notes"
game_end_time = "September 14, 2020, 4:00 am UTC"
gold_coin_reward = 200

# ================
# Other constants
# ================
SUBREDDIT_NAME = "heroesofnewerth"  # testingground4bots / heroesofnewerth
MAX_NUM_GUESSES = 2
MIN_COMMENT_KARMA = 4
MIN_ACCOUNT_AGE_DAYS = 7
NUM_WINNERS = 10
SLEEP_INTERVAL_SECONDS = 10

# ================
# User lists
# ================

# Disallowed users: use a set for the O(1) access time
disallowed_users_set = {"the_timezone_bot", "timee_bot"}

# Recipients list (for Private Messages) for the winners list
staff_recipients = ["ElementUser", "S2Sliferjam"]
