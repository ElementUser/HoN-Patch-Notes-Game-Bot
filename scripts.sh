#!/bin/bash

# Author(s): William Lam
# This .sh file helps map a sequence of commands/long commands to much shorter commands.

if [[ $# -ne 1 ]]; then
    echo "Invalid number of parameters. Running this script only requires 1 parameter."
    exit 2
fi

case $1 in
    "start")
        cd hon_patch_notes_game_bot
        poetry install
        poetry run python main.py
        ;;

    "reset")
        rm -r hon_patch_notes_game_bot/cache/
        ;;

    "test")
        poetry run flake8 ./hon_patch_notes_game_bot --count --select=E9,F63,F7,F82 --show-source --statistics
        poetry run flake8 ./hon_patch_notes_game_bot --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
        poetry run pytest --cov-report term-missing --cov=hon_patch_notes_game_bot tests/
        ;;

    "winners")
        # TODO: implement proper file/argument line combination to run
        ;;

    *)
        echo -e "Invalid option.\n"
        echo "Current command list: "
        echo "
            start: runs the program after navigating to its source code directory (to ensure it runs properly with Poetry's venv)
            reset: removes files in the 'hon_patch_notes_game_bot/cache/' folder
            test: runs flake8 linting tests & pytest unit tests
            winners: gets a list of winners & list of total potential winners
        "
        ;;
esac
