#!/usr/bin/env zsh
# Central background search routing script

QUERY="$1"
[[ -z "$QUERY" ]] && exit 0

# 1. Custom Actions / Widgets Mapping
case "${QUERY:l}" in
    "screenshot") hyprshot -m output; exit 0 ;;
    "unmount") /home/rk1/.local/bin/floating-yazi /run/media/rk1; exit 0 ;;
    "downloads") /home/rk1/.local/bin/floating-yazi ~/Downloads; exit 0 ;;
esac

# 2. Match desktop entries (Apps)
APP_MATCH=$(ls /usr/share/applications/ ~/.local/share/applications/ 2>/dev/null | grep -i "${QUERY}" | head -n 1)
if [[ -n "$APP_MATCH" ]]; then
    # Parse the Exec key out of the matched application entry file cleanly
    EXEC_CMD=$(awk -F= '/^Exec=/ {print $2; exit}' /usr/share/applications/$APP_MATCH ~/.local/share/applications/$APP_MATCH 2>/dev/null | sed 's/%[fFuU]//g')
    [[ -n "$EXEC_CMD" ]] && exec ${(z)EXEC_CMD} &!
    exit 0
fi

# 3. Fallback: Quick directory search
FILE_MATCH=$(fd --hidden --exclude .git . "$HOME" 2>/dev/null | grep -i "${QUERY}" | head -n 1)
if [[ -n "$FILE_MATCH" ]]; then
    if [[ -d "$FILE_MATCH" ]]; then
        exec /home/rk1/.local/bin/floating-yazi "$FILE_MATCH" &!
    else
        exec xdg-open "$FILE_MATCH" &!
    fi
    exit 0
fi
