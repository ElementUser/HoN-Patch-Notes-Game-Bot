# HoN Patch Notes Guessing Game (Bot)

![Build](https://github.com/ElementUser/HoN-Patch-Notes-Game-Bot/workflows/.github/workflows/.github_ci.yml/badge.svg)

This application is intended to automate (or semi-automate) the process of HoN's Patch Notes Guessing Game that is hosted in a Reddit thread.

Reddit users post their guess according to the rules of the game. The rules of the game are the following:

# Rules of the game

- Pick a number between 1 and `max_line_count` (this is dynamically determined at runtime), and post that number to the main thread or the comment that /u/hon-bot responds to you with.
- Guesses for lines that actually have content in the patch notes will be entered into the pool of potential winners for a prize! See the [Rewards](#Rewards) section for more information.
- Each person gets 1 (ONE) guess. If your guess has a number in it in your first line of your comment, it WILL be parsed by the bot and will count as a guess (whether you want it to or not). For simplicity's sake, please only include a number in your guess.
- Guesses for line numbers that don't exist in the patch notes count as an invalid guess. You have been warned!
- There are blank lines in the patch notes. If you guess a blank line, you will receive a `Whiffed!` comment. You have 1 (ONE) more additional guess.
- PLEASE USE CTRL+F or the search feature IF YOUR NUMBER HAS BEEN GUESSED. They will not count as a valid entry, and you will instantly be disqualified if you choose a number that has already been guessed.

# The bot

The bot enforces these rules and outputs various text lines from a given `patch_notes.txt` file, depending on if a user guesses a line with the appropriate number of content or not. Some features/behaviours that the bot will encompass:

- Keep track of each unique user that posts in the thread, as well as their guess count
- Validate users to see if they are new accounts or not

# Using Poetry

`cd python patch_notes_game_bot`
`poetry run main.py`
