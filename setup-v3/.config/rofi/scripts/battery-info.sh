#!/usr/bin/env bash

BAT_PATH="/sys/class/power_supply/BAT0"

# 1. Get Capacity and Status
capacity=$(cat "$BAT_PATH/capacity")
status=$(cat "$BAT_PATH/status")

# 2. Determine if we use Energy (mWh) or Charge (mAh)
if [ -f "$BAT_PATH/energy_now" ]; then
    now=$(cat "$BAT_PATH/energy_now")
    diff=$(cat "$BAT_PATH/power_now")
else
    now=$(cat "$BAT_PATH/charge_now")
    diff=$(cat "$BAT_PATH/current_now")
fi

# 3. Calculate Time Remaining
if [[ "$status" == "Discharging" && "$diff" -gt 0 ]]; then
    total_minutes=$(( now * 60 / diff ))
    hours=$(( total_minutes / 60 ))
    minutes=$(( total_minutes % 60 ))
    time_info="($hours h $minutes m remaining)"
elif [[ "$status" == "Charging" && "$diff" -gt 0 ]]; then
    # Calculate time until full
    [ -f "$BAT_PATH/energy_full" ] && full=$(cat "$BAT_PATH/energy_full") || full=$(cat "$BAT_PATH/charge_full")
    needed=$(( full - now ))
    total_minutes=$(( needed * 60 / diff ))
    hours=$(( total_minutes / 60 ))
    minutes=$(( total_minutes % 60 ))
    time_info="($hours h $minutes m until full)"
else
    time_info="($status)"
fi

# 4. Icon and UI
[[ "$status" == "Charging" ]] && ICON="󰂄" || ICON="󰁹"
info_msg="$ICON  $capacity%  $time_info"

# 5. Launch Rofi
chosen=$(echo -e "󰒓 Settings" | rofi -dmenu -i \
    -mesg "$info_msg" \
    -theme ~/.config/rofi/applets.rasi \
    -p "Power")

case "$chosen" in
    *"Settings"*) kitty -e sudo powertop ;;
esac
