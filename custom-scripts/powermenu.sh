#!/bin/zsh

# 1. Define the options with Nerd Font icons
OPTIONS="󰐥 Shutdown\n󰜉 Reboot\n󰍃 Logout\n󰤄 Suspend\n Lock"

# 2. Use the $OPTIONS variable instead of a hardcoded list
# -theme-str: Forces width/height
# -dmenu: Tells Rofi to act as a menu
chosen=$(echo -e "$OPTIONS" | rofi -dmenu -i -p "Power Menu:" \
    -location 3 \
    -yoffset 50 \
    -xoffset -20 \
    -theme-str 'window {width: 250px; height: 300px;}')

# 3. Match the selection (using wildcards * to ignore the icon)
case "$chosen" in
    *Lock) hyprlock ;;
    *Suspend) systemctl suspend ;;
    *Logout) hyprctl dispatch exit ;;
    *Reboot) systemctl reboot ;;
    *Shutdown) systemctl poweroff ;;
esac
