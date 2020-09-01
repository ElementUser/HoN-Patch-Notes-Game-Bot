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
        poetry run python main.py
        ;;

    "reset")
        rm hon_patch_notes_game_bot/cache/
        ;;

    "test")
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
            reset: resets the files in the 'hon_patch_notes_game_bot/cache/' folder
            test: runs a pytest command to output a test report with the help of the pytest-cov library
            winners: gets a list of winners & list of total potential winners
        "
        ;;
esac
