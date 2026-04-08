#!/bin/bash

VAULT_FILE="$HOME/.local/share/cmd_vault.txt"

# 1. Pipe file to rofi
# -dmenu: list mode
# -i: case insensitive
# -p: prompt name
SELECTED=$(cat "$VAULT_FILE" | rofi -dmenu -i -p "Cmd Vault" -width 250 center)

# 2. Process selection
if [ -n "$SELECTED" ]; then
    # Extract just the command part (everything before " ###")
    CMD=$(echo "$SELECTED" | awk -F ' -> ' '{print $1}')
    
    # Copy to Wayland clipboard (use xclip -selection clipboard for X11)
    echo -n "$CMD" | wl-copy
    
    # Optional: Send a notification confirmation
    notify-send "Vault" "Copied: $CMD"
fi
