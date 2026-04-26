#!/usr/bin/env bash

# chaudio - a script for changing audio using fzf and wpctl (aka WirePlumber)
# created by zyuzya1984
# ---------------------------------------------------------------------------


# menu look (test)
menu() {
    local prompt="$1"
    fzf --prompt="$prompt" --print-query | tail -1
}

# parsing outputs (sinks) and inputs (sources) using wpctl
outputs=$(wpctl status | awk '/Sinks:/,/Sources:/' | \
grep -E '[0-9]+\.' | \
sed -E 's/^[^0-9]*//; s/\[vol: [0-9.]+\]//')
inputs=$(wpctl status | awk '/Sources:/,/Filters:/' | \
grep -E '[0-9]+\.' | \
sed -E 's/^[^0-9]*//; s/\[vol: [0-9.]+\]//')

# function to change default sound device
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
        notify-send "Default audio was switched!"
    fi
}

# main logic
choice=$(echo -e "Output\nInput" | menu "Choose type: ") || exit 0

case $choice in
    Output) change_device "$outputs" "Choose output: " ;;
    Input)  change_device "$inputs"  "Choose input: "  ;;
    *)      exit ;;
esac
