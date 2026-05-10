#!/usr/bin/env bash

# change-audio - a script for changing audio using fzf and wpctl
# Originally created by zyuzya1984; modified for local naming and fzf logic.
# ---------------------------------------------------------------------------

# Improved menu logic to act as a standard picker
menu() {
    local prompt="$1"
    # Removed --print-query to prevent accidental triggers on ESC or empty searches
    fzf --prompt="$prompt" --reverse --height=20% --border
}

# Parsing outputs (sinks) and inputs (sources) using wpctl
# Added sed rules to strip generic hardware controller strings for a cleaner UI
outputs=$(wpctl status | awk '/Sinks:/,/Sources:/' | \
    grep -E '[0-9]+\.' | \
    sed -E 's/^[^0-9]*//; s/\[vol: [0-9.]+\]//; s/Family 17h\/19h HD Audio Controller //g')

inputs=$(wpctl status | awk '/Sources:/,/Filters:/' | \
    grep -E '[0-9]+\.' | \
    sed -E 's/^[^0-9]*//; s/\[vol: [0-9.]+\]//; s/Family 17h\/19h HD Audio Controller //g')

# Function to change default sound device
change_device() {
    local list="$1"
    local prompt="$2"
    local selection
    selection=$(echo "$list" | menu "$prompt") || exit 0

    if [[ -z "$selection" ]]; then
        return 1
    fi

    local sound_id
    sound_id=$(echo "$selection" | grep -oP '^\d+')

    if [[ -n "$sound_id" ]]; then
        wpctl set-default "$sound_id"
        # Notification using UK English spelling
        notify-send "Default audio was switched successfully!"
    fi
}

# Main logic
choice=$(echo -e "Output\nInput" | menu "Choose type: ") || exit 0

case $choice in
    Output) change_device "$outputs" "Choose output: " ;;
    Input)  change_device "$inputs"  "Choose input: "  ;;
    *)      exit ;;
esac
