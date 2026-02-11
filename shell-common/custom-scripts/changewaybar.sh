#!/bin/bash

# Define paths
THEME_DIR="$HOME/.config/waybar/themes"
CONFIG_DIR="$HOME/.config/waybar"

# 1. Rofi Command with Custom Styling
# - location: west (Locks it to the left edge, vertically centered)
# - width/height: Fixed pixel size
# - padding: Internal padding
CHOICE=$(ls "$THEME_DIR" | rofi -dmenu -p "Theme" \
    -theme-str 'window { location: northwest; anchor: west; width: 300px; height: 350px; padding: 2px; margin: 5px 8px; }' \
    -theme-str 'listview { lines: 6; }' \
    -theme-str 'entry { placeholder: "Search..."; }')

# 2. If the user selected something (didn't press Esc)
if [[ -n "$CHOICE" ]]; then
    # Validate that the folder actually exists
    if [[ -d "$THEME_DIR/$CHOICE" ]]; then
        
        # Remove current symlinks
        rm -f "$CONFIG_DIR/config"
        rm -f "$CONFIG_DIR/style.css"

        # Create new symlinks
        ln -s "$THEME_DIR/$CHOICE/config" "$CONFIG_DIR/config"
        ln -s "$THEME_DIR/$CHOICE/style.css" "$CONFIG_DIR/style.css"

        # Restart Waybar
        killall waybar
        waybar & disown
        waybar -c ~/.config/waybar/config-pod -s ~/.config/waybar/style-pod.css & disown 
        
        # Send a notification
        notify-send "Waybar" "Theme switched to $CHOICE"
    else
        notify-send "Waybar" "Error: Theme not found"
    fi
fi
