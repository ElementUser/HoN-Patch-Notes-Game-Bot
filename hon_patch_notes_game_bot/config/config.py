"""
This file will contain the bot script configuration that are most likely to change
"""


# ==========
# Variables
# ==========

# [GAME] 4.8.X - Patch Notes Guessing Game
submission_title = "[GAME] 4.8.7 - Patch Notes Guessing Game"
community_submission_title = "4.8.7: community-revealed Patch Notes"
game_end_time = "November 22, 2020, 4:00 am UTC"
gold_coin_reward = 400

# ================
# Other constants
# ================
SUBREDDIT_NAME = "heroesofnewerth"  # testingground4bots / heroesofnewerth
MAX_PERCENT_OF_LINES_REVEALED = 70  # Safety-oriented variable to ensure that the entire patch notes will not be revealed
MAX_NUM_GUESSES = 2
MIN_COMMENT_KARMA = 4
MIN_ACCOUNT_AGE_DAYS = 7
NUM_WINNERS = 20
SLEEP_INTERVAL_SECONDS = 10

# ================
# Lists
# ================

# Disallowed users: use a set for the O(1) access time
disallowed_users_set = {"the_timezone_bot", "timee_bot", "-koy", "rrreeddiitt"}

# Recipients user list (for Private Messages) for the winners list
staff_recipients = ["ElementUser", "S2Sliferjam"]

# Invalid line strings (for guess validity in the game)
invalid_line_strings = ["_______", "-------"]
