#!/bin/zsh

# --- 1. Select the wallpaper (Gallery Mode) ---
SELECTED_WALL=$(find ~/Pictures/Wallpapers -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.webp" \) | while read -r line; do
    echo -en "$line\x00icon\x1f$line\n"
done | rofi -dmenu -i -p "Select Wallpaper" \
    -theme-str 'window { location: 2; width: 800px; height: 150px; border: 0px; border-color: #ffffff; background-color: rgba(0, 0, 0, 0.4); border-radius: 0px; }' \
    -theme-str 'mainbox { children: [listview]; background-color: transparent; }' \
    -theme-str 'listview { columns: 6; lines: 1; spacing: 5px; scrollbar: false; background-color: transparent; }' \
    -theme-str 'element { orientation: vertical; padding: 5px; background-color: transparent; border-radius: 0px; }' \
    -theme-str 'element-icon { size: 120px; horizontal-align: 0.5; vertical-align: 0.5; }' \
    -theme-str 'element-text { enabled: false; }' \
    -theme-str 'element selected.normal { background-color: rgba(255, 255, 255, 0.1); border: 0px 0px 4px 0px; border-color: #800080; }')

[ -z "$SELECTED_WALL" ] && exit 0

# --- 2. Set the Wallpaper ---
swww img "$SELECTED_WALL" --transition-type grow --transition-pos top-right

# --- 3. Generate Colors (FIXED: Added Variable) ---
# We use the selected wallpaper variable here. 
# The -n flag guarantees Kitty is NOT touched.
wal -n -s -t -e -q -i "$SELECTED_WALL" > /dev/null 2>&1

# --- 4. Update Hyprland Borders ---
source "$HOME/.cache/wal/colors.sh"
hyprctl keyword general:col.active_border "0xEE${color1:1}"
hyprctl keyword general:col.inactive_border "0xAA${color0:1}"

# --- 5. Update Waybar (FIXED: Removed wal -R) ---
# Removed 'wal -R' because it forces colors onto Kitty.
pkill waybar
# Signal Waybar to reload its style
pkill -USR2 waybar
while pgrep -u $USER -x waybar >/dev/null; do sleep 0.1; done

# Assuming you want to launch your specific Waybar config:
# (I kept your original double-launch logic if you use dual bars, 
# but usually you only need one of these lines).
waybar &
waybar -c ~/.config/waybar/config-pod -s ~/.config/waybar/style-pod.css & disown 
#G_APPLICATION_ID=org.waybar.desktop waybar -c ~/.config/waybar/config-desktop -s ~/.config/waybar/style-desktop.css &

# --- 6. Swaync client restart
swaync-client -rs

# --- 7. Fastfetch Logo Processing ---
BG_COLOR=$(jq -r '.special.background' ~/.cache/wal/colors.json)
magick ~/Pictures/Fastfetch/anime-manga-fc.png -background "$BG_COLOR" -flatten ~/Pictures/Fastfetch/fastfetch_logo.png

notify-send "Wallpaper Changed" "Colors synchronized (Kitty untouched)."
