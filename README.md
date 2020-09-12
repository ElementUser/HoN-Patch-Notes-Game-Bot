# HoN Patch Notes Guessing Game (Bot)

![Build](https://img.shields.io/github/workflow/status/ElementUser/HoN-Patch-Notes-Game-Bot/Github%20CI?label=Build%3A%20Github%20CI)

This application automates the process of HoN's Patch Notes Guessing Game that is hosted in a thread on the Reddit platform.

Specifically, the bot is intended to create a thread in the [/r/heroesofnewerth subreddit](https://www.reddit.com/r/HeroesofNewerth/).

Reddit users post their guess according to the [Rules of the game](#Rules-of-the-game).

To skip to Bot Usage directly, go to the [Requirements section](#Requirements).

## Rules of the game

- Pick a number between 1 and `max_line_count` (this is dynamically determined at runtime), and post that number to the main thread or the comment that /u/hon-bot responds to you with.
- Guesses for lines that actually have content in the patch notes will be entered into the pool of potential winners for a prize!
- Each person gets 1 (ONE) guess. If your guess has a number in it in your first line of your comment, it WILL be parsed by the bot and will count as a guess (whether you want it to or not). For simplicity's sake, please only include a number in your guess.
- Guesses for line numbers that don't exist in the patch notes count as an invalid guess. You have been warned!
- There are blank lines in the patch notes. If you guess a blank line, you will receive a `Whiffed!` comment response. You have 1 (ONE) more additional guess.
- PLEASE USE CTRL+F or the search feature IF YOUR NUMBER HAS BEEN GUESSED. A guess with a number that has already been guessed will count as an invalid guess.

## The Bot

The bot enforces these rules and outputs various text lines from a given `patch_notes.txt` file, depending on if a user guesses a line with the appropriate number of content or not. Some features/behaviours that the bot will encompass:

- Log into Reddit (credentials are configured in `hon_patch_notes_game_bot/praw.ini`) and communicate with its API at fixed time intervals
- Keep track of each unique user that responds to the bot in the thread and/or to a comment that the bot made in the thread
- Keep track of these user's statistics pertaining to the current game instance
- Prevent Reddit accounts that are too new or below a certain comment karma from commenting
- Creates a second Reddit thread where it keeps track of the correctly guessed patch note lines & fills in the content for the public to view

---

# Requirements

- [Python 3.8](https://www.python.org/downloads/release/python-380/) or higher must be installed on the host system.
  - If installing Python 3.8 on Linux, follow the directions [here](https://tecadmin.net/install-python-3-8-ubuntu/)

# Setup

- Log onto the bot's Reddit account at: https://www.reddit.com/login/
- Set up a Reddit app by following the instructions [here](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example), and obtain your app's `client_id` and `client_secret` (required for next step)
- Create a `praw.ini` file in this directory: `hon_patch_notes_game_bot/praw.ini`.

Configure `praw.ini` with your bot credentials so it looks like this:

```
[insertBotNameHere]
client_id=insert_client_id_here
client_secret=insert_client_secret_here
password=insert_bot_password_here
username=insert_bot_username_here
```

Using a `praw.ini` file is a secure way to provide the login credentials for PRAW in the bot script. `.ini` files are not committed to source control (as defined in `.gitignore`). [praw.ini reference](https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html)

- Install Poetry by following the installation steps [from their official documents](https://python-poetry.org/docs/). Do not use `pip install` to install Poetry.
- `Mac/Linux`: After installation, on Mac/Linux you must run this command to enable the poetry command in your terminal: `source $HOME/.poetry/env`
- Update Poetry to the latest version by running this command: `poetry self update --preview`
  - Poetry is required to handle dependencies in a virtualenv & run the script in a consistent environment regardless of the host system.

## Mac/Linux - Additional Setup

- Navigate to the project root directory in your terminal and run `stat scripts.sh` to check its permissions. This file must have execute permissions (the "x" flag set) to run properly.
- If required, use `chmod 744 scripts.sh` (assuming the current account is the owner of the file) to set file permissions properly.

# Usage

Navigate to the project root directory in your terminal.

- To run the script, use `./scripts.sh start`
- To run unit tests, use `./scripts.sh test`
- To reset the cache & database, use `./scripts.sh reset` before running `./scripts.sh start`
- To pick a list of winners from the existing local database, use `./scripts.sh winners 10`, where the "10" can be replaced with an integer to specify the number of winners picked

## More Usage Notes

For unreleased patch notes, **do not commit and push the branch to source control before their official release**.

To change up some commonly changed configuration before starting a new run, go to `hon_patch_notes_game_bot/config/config.py` and edit them.

## Extra Documentation

Feel free to browse the [docs](/docs) folder in the repository and browse the documentation there for more details on some of the tools, resources & references used for this project & the reason why they were included in this project.
