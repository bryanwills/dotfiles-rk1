#!/bin/zsh

# If an argument is passed, use it as the wallpaper. 
# Otherwise, do nothing (or run your old logic).
if [ -n "$1" ]; then
    WALL="$1"
    # Put your existing wallpaper setting logic here (swww, nitrogen, etc.)
    swww img "$WALL" --transition-type grow
    notify-send "Wallpaper Changed" "$WALL"
    exit 0
fi
# --- 1. Select the wallpaper ---
# We ensure the path is absolute and Rofi is told to show icons
WALL_DIR="$HOME/Pictures/Wallpapers"

SELECTED_WALL=$(find "$WALL_DIR" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.webp" \) | while read -r line; do
    # This format is vital: The path is the label, and icon is the metadata
    echo -en "$line\0icon\x1f$line\n"
done | rofi -dmenu -i -p "Select Wallpaper" \
    -show-icons \
    -theme-str 'window { location: north; anchor: 2; width: 1000; height: 255px; background-color: rgba(0, 0, 0, 0.2); border: 2px; }' \
    -theme-str 'mainbox { children: [ listview ]; spacing: 0px; margin: 0px; }' \
    -theme-str 'listview { columns: 4; lines: 1; spacing: 5px; padding: 0px; }' \
    -theme-str 'inputbar { enabled: false; }' \
    -theme-str 'element { orientation: horizontal; padding: 0px; margin: 0px; }' \
    -theme-str 'element-icon { size: 240px; }' \
    -theme-str 'element-text { enabled: false; }' \
    -theme-str 'element selected { border: 0px 0px 2px 0px; border-color: #98fb98; margin: 0px; padding: 0px; }
   ')

# Exit if nothing was selected
[ -z "$SELECTED_WALL" ] && exit 0

# --- 2. Set the Wallpaper ---
swww img "$SELECTED_WALL" --transition-type grow --transition-pos top-right

# --- 3. Refresh Hyprland ---
# This reloads your hard-coded borders, gaps, and rules from V1 or V2
hyprctl reload

# --- 4. Refresh SwayNC ---
# This will pick up whatever style.css is currently linked in ~/.config/swaync
swaync-client -rs

notify-send "Wallpaper Changed" "System borders and SwayNC refreshed."
