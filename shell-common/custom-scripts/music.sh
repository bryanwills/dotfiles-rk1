#!/bin/bash

# 1. Launch Kew (tagged as "musicbox")
kitty --class="musicbox" --title="Kew Player" kew &

# 2. Wait 0.5 seconds for the window to actually appear
sleep 0.5

# 3. Force Hyprland to grab that specific window and move it
# We search for the window with class "musicbox" and get its Address ID
ADDR=$(hyprctl clients -j | jq -r '.[] | select(.class=="musicbox") | .address')

# 4. Apply the position rules manually
hyprctl dispatch setfloating address:$ADDR
hyprctl dispatch resizewindowpixel exact 650 450,address:$ADDR
# "1480" is roughly Top-Right on a 1080p screen (1920 - 400 - 40)
#hyprctl dispatch movewindowpixel exact 1230 50,address:$ADDR
