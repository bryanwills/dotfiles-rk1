#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  notifications.sh — Dunst History for Rofi
# ─────────────────────────────────────────────

LOG_FILE="/home/rk1/.cache/notification_history.log"
# Path to your Rofi theme
THEME="/home/rk1/.config/rofi/notifications.rasi"

# 1. Get the history from the log (Newest at the top)
build_entries() {
    if [[ -f "$LOG_FILE" ]]; then
        tac "$LOG_FILE"
    fi
}

# 2. Function to clear the log
clear_history() {
    # Simple confirmation menu
    local choice
    choice=$(printf "󰆴 Clear All\n󰜺 Cancel" | rofi -dmenu -p "Confirm" -theme "$THEME" -i)
    
    if [[ "$choice" == *"Clear All"* ]]; then
        printf "" > "$LOG_FILE"
        notify-send "System" "Notification history cleared"
    fi
}

# 3. Main Loop
main() {
    local entries selected
    entries=$(build_entries)

    if [[ -z "$entries" ]]; then
        rofi -e "No notifications in history" -theme "$THEME"
        exit 0
    fi

    # Show the list with a 'Clear' option at the bottom
    selected=$(echo -e "$entries\n󰎟 Clear History" | \
        rofi -dmenu -i \
        -theme "$THEME" \
        -p "History")

    [[ -z "$selected" ]] && exit 0

    if [[ "$selected" == *"Clear History"* ]]; then
        clear_history
    else
        # Copy the text to clipboard (strips the [HH:MM] timestamp)
        echo "$selected" | sed 's/^\[[0-9]\{2\}:[0-9]\{2\}\] //' | wl-copy
        notify-send "Copied" "Notification text saved to clipboard"
    fi
}

main
