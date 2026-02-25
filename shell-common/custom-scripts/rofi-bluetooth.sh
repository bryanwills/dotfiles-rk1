#!/bin/bash

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
        -theme ~/.config/rofi/themes/rk1-neon.rasi \
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
