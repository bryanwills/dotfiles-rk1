#!/bin/zsh

# --- 1. Select the wallpaper ---
# We ensure the path is absolute and Rofi is told to show icons
WALL_DIR="$HOME/Pictures/Wallpapers"

SELECTED_WALL=$(find "$WALL_DIR" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.webp" \) | while read -r line; do
    # This format is vital: The path is the label, and icon is the metadata
    echo -en "$line\0icon\x1f$line\n"
done | rofi -dmenu -i -p "Select Wallpaper" \
    -theme-str 'window { location: 2; width: 800px; height: 150px; border: 0px; border-radius: 0px; }' \
    -theme-str 'mainbox { children: [listview]; background-color: rgba(211, 211, 211, 0.8); }' \
    -theme-str 'listview { columns: 6; lines: 1; spacing: 5px; scrollbar: false; background-color: transparent; }' \
    -theme-str 'element { orientation: vertical; padding: 5px; background-color: transparent; border-radius: 0px; }' \
    -theme-str 'element-icon { size: 120px; horizontal-align: 0.5; vertical-align: 0.5; }' \
    -theme-str 'element-text { enabled: false; }' \
    -theme-str 'element selected.normal {border: 0px 0px 4px 0px; border-color: #800080; }')

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
