# HoN Patch Notes Guessing Game (Bot)

![Build](https://github.com/ElementUser/HoN-Patch-Notes-Game-Bot/workflows/.github/workflows/.github_ci.yml/badge.svg)

This application is intended to automate (or semi-automate) the process of HoN's Patch Notes Guessing Game that is hosted in a Reddit thread.

Reddit users post their guess according to the rules of the game. The rules of the game are the following: 

```
- Pick a number between 1 and (# of lines in patch_notes.txt)

- Each person gets 1 (ONE) guess. As the bot sees each reply in the thread, the bot will look up that line on the notes and let you know exactly what it says.
*Use your collective knowledge and put together the patch notes early!

- Don't ruin the fun for others. Don't be rude or a jerk.

- There are lines that are [blank] (Whiff). If you receive a [blank] (whiff) response, you have 1 (ONE) more additional guess, [blank] or (whiff) again and you're out!

- 10 lucky users who guess a line that contains actual content will be randomly selected for a gold giveaway!

- PLEASE USE CTRL+F, or the search feature IF YOUR NUMBER HAS BEEN ASKED. They will not count as a valid entry and it will be ignored!
```


# The bot

The bot enforces these rules and outputs various text lines from a given `patch_notes.txt` file, depending on if a user guesses a line with the appropriate number of content or not. Some features/behaviours that the bot will encompass:

- Keep track of each unique user that posts in the thread, as well as their guess count
- Validate users to see if they are new accounts or not

# Using Poetry

`cd python patch_notes_game_bot`
`poetry run main.py`