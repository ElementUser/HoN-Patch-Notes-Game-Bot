"""
This file will contain the bot script configuration that are most likely to change
"""
from typing import List, Set

# ==========
# Variables
# ==========

# [GAME] 4.9.X - Patch Notes Guessing Game
SUBMISSION_TITLE: str = "[GAME] 4.9.3 - Patch Notes Guessing Game"
COMMUNITY_SUBMISSION_TITLE: str = "4.9.3 - Community-revealed Patch Notes"
GAME_END_TIME: str = "May 10, 2021, 4:00 am UTC"

# ================
# Reward settings
# ================

GOLD_COIN_REWARD: int = 300
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

BOT_USERNAME: str = "hon-bot"
USER_AGENT: str = "HoN Patch Notes Game Bot by /u/hon-bot"
PATCH_NOTES_PATH: str = "config/patch_notes.txt"
SUBMISSION_CONTENT_PATH: str = "config/submission_content.md"
COMMUNITY_SUBMISSION_CONTENT_PATH: str = "config/community_patch_notes_compilation.md"
WINNERS_LIST_FILE_PATH: str = "cache/winners_list.txt"
REWARD_CODES_FILE_PATH: str = "cache/reward_codes.txt"
BLANK_LINE_REPLACEMENT: str = "..."

# ================
# Data structures
# ================

# Disallowed users: use a set for the O(1) access time
DISALLOWED_USERS_SET: Set[str] = {
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
STAFF_RECIPIENTS_LIST: List[str] = ["ElementUser", "FB-Saphirez"]

# Invalid line strings (for guess validity in the game)
INVALID_LINE_STRINGS: List[str] = ["_______", "-------"]
