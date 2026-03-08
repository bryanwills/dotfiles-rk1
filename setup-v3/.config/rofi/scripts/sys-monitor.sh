#!/usr/bin/env bash

# 1. Get CPU usage (Calculating delta over 0.2s)
cpu_stats_1=$(grep 'cpu ' /proc/stat)
read -r _ user1 nice1 system1 idle1 iowait1 irq1 softirq1 steal1 guest1 guest_nice1 <<< "$cpu_stats_1"

sleep 0.2

cpu_stats_2=$(grep 'cpu ' /proc/stat)
read -r _ user2 nice2 system2 idle2 iowait2 irq2 softirq2 steal2 guest2 guest_nice2 <<< "$cpu_stats_2"

# Calculate totals
prev_idle=$((idle1 + iowait1))
idle=$((idle2 + iowait2))

prev_total=$((user1 + nice1 + system1 + idle1 + iowait1 + irq1 + softirq1 + steal1))
total=$((user2 + nice2 + system2 + idle2 + iowait2 + irq2 + softirq2 + steal2))

# Math: (Total Diff - Idle Diff) / Total Diff
total_diff=$((total - prev_total))
idle_diff=$((idle - prev_idle))

if [[ $total_diff -gt 0 ]]; then
    cpu_usage=$((100 * (total_diff - idle_diff) / total_diff))
else
    cpu_usage=0
fi

# 2. Get RAM usage percentage
# We pull 'used' and 'total' from free -m to ensure math works
mem_stats=$(free -m | grep Mem)
mem_used=$(echo "$mem_stats" | awk '{print $3}')
mem_total=$(echo "$mem_stats" | awk '{print $2}')
mem_perc=$(( 100 * mem_used / mem_total ))

# 3. Format Message
info_msg="󰻠 CPU: $cpu_usage%   󰍛 RAM: $mem_perc%"

# 4. Launch Rofi
chosen=$(echo -e "󰑓 Monitor" | rofi -dmenu -i \
    -mesg "$info_msg" \
    -theme ~/.config/rofi/applets.rasi \
    -p "System")

# 5. Actions
case "$chosen" in
    *"Monitor"*) kitty -e btop ;;
esac

