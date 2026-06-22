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

# 2. Match desktop entries (Apps) via native Zsh glob paths
local app_paths=(
    /usr/share/applications/*(N)
    ~/.local/share/applications/*(N)
)

local app_match=""
for f in "${app_paths[@]}"; do
    if [[ "${f:t:l}" == *"${QUERY:l}"* ]]; then
        app_match="$f"
        break
    fi
done

if [[ -n "$app_match" ]]; then
    # Parse the Exec key cleanly from the confirmed absolute path location
    local exec_cmd=$(awk -F= '/^Exec=/ {print $2; exit}' "$app_match" 2>/dev/null | sed 's/%[fFuU]//g')
    [[ -n "$exec_cmd" ]] && exec ${(z)exec_cmd} &!
    exit 0
fi

# 3. Fallback: Optimized direct path search using native fd filtering
local file_match=$(fd --hidden --exclude .git --type d --type f "${QUERY}" "$HOME" 2>/dev/null | head -n 1)
if [[ -n "$file_match" ]]; then
    if [[ -d "$file_match" ]]; then
        exec /home/rk1/.local/bin/floating-yazi "$file_match" &!
    else
        exec xdg-open "$file_match" &!
    fi
    exit 0
fi
