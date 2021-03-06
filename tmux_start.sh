#!/bin/bash

# Author(s): William Lam
# This .sh file starts a new hon-bot tmux session, resets the cache, and starts the patch notes script in that session.
# Useful for using the `at` command to schedule this to run ahead of time.

# To schedule this file to be run, navigate to this project's directory and then execute this command:
# echo "./tmux_start.sh" | at 9:00 AM 01/22/2021

# Change the date & time as needed

tmux kill-session -t hon-bot
tmux new-session -d -s hon-bot
tmux send-keys -t hon-bot './scripts.sh reset' Enter && sleep 3
tmux send-keys -t hon-bot './scripts.sh start' Enter && sleep 0.1
