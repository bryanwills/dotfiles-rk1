#!/bin/bash

THEME_NAME=$(cat ~/.current_theme 2>/dev/null || echo "rk1-dark.rasi")
# Function to get status
get_status() {
    if rfkill list bluetooth | grep -q "Soft blocked: no"; then
        echo "on"
    else
        echo "off"
    fi
}

while true; do
    status=$(get_status)
    
    if [ "$status" == "on" ]; then
        options="󰂱 Connect Device\n󰂯 Turn Off\n󰈆 Exit"
    else
        options="󰂲 Turn On\n󰈆 Exit"
    fi

    # Launch Rofi with temporary theme overrides for size and position
    chosen=$(echo -e "$options" | rofi -dmenu \
        -p "Bluetooth ($status)" \
        -theme ~/.config/rofi/themes/"$THEME_NAME" \
        -theme-str 'window { location: northeast; anchor: northeast; width: 300px; height: 250px; x-offset: -20px; y-offset: 2px; }' \
        -theme-str 'listview { lines: 5; }')
        
    case "$chosen" in
        *"Turn On"*)
            rfkill unblock bluetooth
            sleep 0.5
            bluetoothctl power on
            ;;
        *"Turn Off"*)
            bluetoothctl power off
            rfkill block bluetooth
            ;;
        *"Connect"*)
            overskride &
            exit 0 # Exit Rofi after launching the manager
            ;;
        *"Exit"*)
            exit 0
            ;;
        "") # If user hits Escape
            exit 0
            ;;
    esac
done
