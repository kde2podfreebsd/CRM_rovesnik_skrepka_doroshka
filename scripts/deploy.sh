#!/bin/bash

export PYTHONPATH=$PYTHONPATH:$(pwd)

source "venv/bin/activate"

programs=(
    "BackendApp/TelegramBots/Rovesnik/main.py"
    "BackendApp/TelegramBots/SupportBot/bot.py" 
    "BackendApp/TelegramBots/HeadBot/main.py"
    "BackendApp/API/app.py"
)
session_names=(
    "rovesnik"
    "support_bot"
    "head_bot"
    "api"
)

for i in "${!programs[@]}"; do
    screen -dmS "${session_names[$i]}"
    screen -S "${session_names[$i]}" -X stuff "${programs[$i]}\n"
done