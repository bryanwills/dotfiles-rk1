#!/bin/zsh

# --- 1. Select the wallpaper (Gallery Mode) ---
SELECTED_WALL=$(find ~/Pictures/Wallpapers -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.webp" \) | while read -r line; do
    echo -en "$line\0icon\x1f$line\n"
done | rofi -dmenu -i -p "Select Wallpaper" \
    -show-icons \
    -theme-str 'window { location: north; anchor: 2; width: 580; height: 300px; background-color: rgba(0, 0, 0, 0.2); border: 2px; }' \
    -theme-str 'mainbox { children: [ listview ]; spacing: 0px; margin: 0px; }' \
    -theme-str 'listview { columns: 4; lines: 2; spacing: 5px; padding: 0px; }' \
    -theme-str 'inputbar { enabled: false; }' \
    -theme-str 'element { orientation: horizontal; padding: 0px; margin: 0px; }' \
    -theme-str 'element-icon { size: 140px; }' \
    -theme-str 'element-text { enabled: false; }' \
    -theme-str 'element selected { border: 0px 0px 2px 0px; border-color: #98fb98; margin: 0px; padding: 0px; }
   ')

[ -z "$SELECTED_WALL" ] && exit 0

# --- 2. Set the Wallpaper ---
swww img "$SELECTED_WALL" --transition-type grow --transition-pos top-right

# --- 3. Generate Colors (FIXED: Added Variable) ---
# We use the selected wallpaper variable here. 
# The -n flag guarantees Kitty is NOT touched.
wal -n -s -t -e -q -i "$SELECTED_WALL" > /dev/null 2>&1

# --- 4. Update Hyprland Borders ---
source "$HOME/.cache/wal/hyprland.conf"
hyprctl keyword general:col.active_border "0xEE${color1:1}"
hyprctl keyword general:col.inactive_border "0xAA${color0:1}"

# --- 5. Update Waybar (FIXED: Removed wal -R) ---
wal -R

pkill waybar
# Signal Waybar to reload its style
pkill -USR2 waybar
while pgrep -u $USER -x waybar >/dev/null; do sleep 0.1; done

# Assuming you want to launch your specific Waybar config:
# (I kept your original double-launch logic if you use dual bars, 
# but usually you only need one of these lines).
waybar & disown
waybar -c ~/.config/waybar/config-pod -s ~/.config/waybar/style-pod.css & disown 

# --- 6. Swaync client restart
swaync-client -rs

# --- 7. Fastfetch Logo Processing ---
BG_COLOR=$(jq -r '.special.background' ~/.cache/wal/colors.json)

notify-send "Wallpaper Changed" "Colors synchronized (Kitty untouched)."
