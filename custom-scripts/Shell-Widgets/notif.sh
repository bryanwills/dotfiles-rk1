#!/usr/bin/env zsh
# ─────────────────────────────────────────────────────────────────────────────
#  notif-widget — Notification History Centre
#  Zsh + FZF driven lightweight replacement widget
# ─────────────────────────────────────────────────────────────────────────────

LOG_FILE="${HOME}/.cache/notification_history.log"

load_notifications() {
    if [[ ! -f "$LOG_FILE" || ! -s "$LOG_FILE" ]]; then
        echo "No notifications"
        return
    fi

    # Read the file line by line into a local array
    local lines=("${(@f)$(<"$LOG_FILE")}")
    
    # Loop backwards to show the newest notifications at the top of the menu
    for i in {$#lines..1}; do
        local line="$lines[i]"
        
        # Trim whitespace using standard Zsh pattern matching instead of modifiers
        line="${line##[[:space:]]}"
        line="${line%%[[:space:]]}"
        [[ -z "$line" ]] && continue
        
        # Check if line matches a standard log timestamp [HH:MM]
        if [[ "$line" =~ '^\[([0-9]{2}:[0-9]{2})\][[:space:]]+(.*)$' ]]; then
            echo "${match[1]} │ ${match[2]}"
        else
            echo "--:-- │ $line"
        fi
    done
}

clear_notifications() {
    if [[ -f "$LOG_FILE" ]]; then
        true > "$LOG_FILE"
    fi
}

run_widget_loop() {
    while true; do
        local source_data=$(load_notifications)
        local count=0
        
        if [[ "$source_data" != "No notifications" ]]; then
            count=$(echo "$source_data" | wc -l)
        fi

        # Build a clean vertical list for the sidebar panel
        local cmd_menu=$'COMMANDS\n\n'
        cmd_menu+=$'[Enter]  \u2192 Copy Message\n'
        cmd_menu+=$'[Ctrl+R] \u2192 Refresh\n'
        cmd_menu+=$'[Ctrl+X] \u2192 Clear All\n'
        cmd_menu+=$'[Esc, q] \u2192 Quit'

        local fzf_flags=(
            --layout=reverse
            --border=rounded
            --margin=1,2
            --height=20
            --color="header:#565f89,prompt:#565f89" 09
            --prompt="Notifications [$count] → "
            --preview-window=left,22,border-right
            --preview="echo '$cmd_menu'"
            --expect="ctrl-r,ctrl-x,q"
        )

        local selection=$(echo "$source_data" | fzf "${fzf_flags[@]}")

        local key=$(echo "$selection" | sed -n '1p')
        local selected_row=$(echo "$selection" | sed -n '2p')

        if [[ "$key" == "q" || -z "$selection" ]]; then
            break
        elif [[ "$key" == "ctrl-r" ]]; then
            continue
        elif [[ "$key" == "ctrl-x" ]]; then
            clear_notifications
            continue
        elif [[ -z "$key" && -n "$selected_row" && "$selected_row" != "No notifications" ]]; then
            local raw_message="${selected_row#* │ }"
            printf '%s' "$raw_message" | wl-copy 2>/dev/null
            break
        fi
    done
}

run_widget_loop
