#!/usr/bin/env zsh

# ----------------------------------------------------------------------------------------
# MINIMALIST EPHEMERAL SCHEDULER WIDGET
# Absolute Runtime Path Fix
# May 2026 v0.1.2
# ----------------------------------------------------------------------------------------

# Capture the absolute directory path where this script resides
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
SCRIPT_PATH="$SCRIPT_DIR/$(basename "$0")"

if [[ "$1" == "--trigger-alert" ]];
then
    clear
    echo -e "\n\n  󰵅  REMINDER ALERT"
    echo -e "  ----------------------------------------"
    echo -e "  ${@:2}\n"
    echo -e "  ----------------------------------------"
    read -rs "?  Press [ENTER] to dismiss..."
    exit 0
fi

print -n "󱎫  Duration (e.g., 10m, 2h, 45s): "
read duration

if [[ ! "$duration" =~ ^[0-9]+[smhd]$ ]]; then
    echo "Error: Invalid format. Use s, m, h, or d."
    exit 1
fi

print -n "󰔳  Message: "
read message
[[ -z "$message" ]] && message="Timer for $duration has expired."

case ${duration: -1} in
    s) seconds=${duration%s} ;;
    m) seconds=$(( ${duration%m} * 60 )) ;;
    h) seconds=$(( ${duration%h} * 3600 )) ;;
    d) seconds=$(( ${duration%d} * 86400 )) ;;
esac

echo "󰄬  Reminder scheduled."

# Capture the exact Wayland session environmental variables from the current active context
local current_wayland="$WAYLAND_DISPLAY"
local current_runtime="$XDG_RUNTIME_DIR"

# Explicitly inject the display variables into the detached subshell environment
(
    sleep $seconds
    export WAYLAND_DISPLAY="$current_wayland"
    export XDG_RUNTIME_DIR="$current_runtime"
    /usr/bin/kitty --class schedule-alert -e "$SCRIPT_PATH" --trigger-alert "$message"
) <&- >&- 2>&- &!
