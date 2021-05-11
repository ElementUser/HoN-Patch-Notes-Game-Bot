"""
This file will contain the bot script configuration that are most likely to change
"""
from typing import List, Set

# ==========
# Variables
# ==========

# [GAME] 4.9.X - Patch Notes Guessing Game
submission_title: str = "[GAME] 4.9.3 - Patch Notes Guessing Game"
community_submission_title: str = "4.9.3 - Community-revealed Patch Notes"
game_end_time: str = "May 10, 2021, 4:00 am UTC"

# ================
# Reward settings
# ================

gold_coin_reward: int = 300
NUM_WINNERS: int = 25

# ================
# Other constants
# ================
SUBREDDIT_NAME: str = "heroesofnewerth"  # testingground4bots / heroesofnewerth
MAX_PERCENT_OF_LINES_REVEALED: int = 66  # Safety-oriented variable to ensure that the entire patch notes will not be revealed
MAX_NUM_GUESSES: int = 2
MIN_COMMENT_KARMA: int = 4
MIN_LINK_KARMA: int = 4
MIN_ACCOUNT_AGE_DAYS: int = 7
SLEEP_INTERVAL_SECONDS: int = 10
STAFF_MEMBER_THAT_HANDS_OUT_REWARDS: str = "FB-Saphirez"

# ================
# Data structures
# ================

# Disallowed users: use a set for the O(1) access time
disallowed_users_set: Set[str] = {
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
staff_recipients: List[str] = ["ElementUser", "FB-Saphirez"]

# Invalid line strings (for guess validity in the game)
invalid_line_strings: List[str] = ["_______", "-------"]
