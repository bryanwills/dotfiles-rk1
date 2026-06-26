#!/usr/bin/env zsh
# ─────────────────────────────────────────────────────────────────────────────
#  clipbox-widget — Clipboard Manager Center
#  Zsh + FZF driven native replacement widget
# ─────────────────────────────────────────────────────────────────────────────

PINS_FILE="${HOME}/.cache/clipbox-pins.json"

# Ensure the cache pin infrastructure index file exists with valid arrays
if [[ ! -f "$PINS_FILE" ]]; then
    echo '[]' > "$PINS_FILE"
fi

load_pins() {
    jq -r '.[]' "$PINS_FILE" 2>/dev/null
}

save_pin() {
    local text="$1"
    local tmp_json=$(mktemp)
    jq --arg text "$text" '. += [$text] | unique' "$PINS_FILE" > "$tmp_json" && mv "$tmp_json" "$PINS_FILE"
}

remove_pin() {
    local text="$1"
    local tmp_json=$(mktemp)
    jq --arg text "$text" 'del(.[] | select(. == $text))' "$PINS_FILE" > "$tmp_json" && mv "$tmp_json" "$PINS_FILE"
}

load_clipboard_entries() {
    local current_mode="$1"
    local raw_list=$(cliphist list 2>/dev/null)
    [[ -z "$raw_list" ]] && return

    local pinned_items=(${(f)"$(load_pins)"})

    echo "$raw_list" | while read -r line; do
        local cid="${line%%	*}"
        local text="${line#*	}"
        
        # Determine pin state structure matching the current mode context
        local is_pinned=false
        if (( ${pinned_items[(I)$text]} )); then
            is_pinned=true
        fi

        if [[ "$current_mode" == "pinned" ]]; then
            $is_pinned && echo "󰐃 $cid │ $text"
        else
            if $is_pinned; then
                echo "󰐃 $cid │ $text"
            else
                echo "   $cid │ $text"
            fi
        fi
    done
}

run_widget_loop() {
    local current_mode="all"
    
    while true; do
        local source_data=$(load_clipboard_entries "$current_mode")
        local count=$(echo "$source_data" | grep -v -c "^$" 2>/dev/null || echo "0")

        local cmd_menu=$'COMMANDS\n\n'
        cmd_menu+=$'[Enter]  \u2192 Copy Item\n'
        cmd_menu+=$'[Tab]    \u2192 Toggle Mode\n'
        cmd_menu+=$'[Ctrl+P] \u2192 Pin/Unpin\n'
        cmd_menu+=$'[Ctrl+D] \u2192 Delete Entry\n'
        cmd_menu+=$'[Ctrl+X] \u2192 Wipe History\n'
        cmd_menu+=$'[Esc, q} \u2192 Quit'

        local fzf_flags=(
            --layout=reverse
            --border=rounded
            --margin=1,2
            --height=22
            --color="header:#565f89,prompt:#565f89"
            --prompt="Clipboard ($current_mode) [$count] "
            --preview-window=left,24,border-right
            --preview="echo '$cmd_menu'"
            --expect="tab,ctrl-p,ctrl-d,ctrl-x,q"
        )

        local selection=$(echo "$source_data" | fzf "${fzf_flags[@]}")

        local key=$(echo "$selection" | sed -n '1p')
        local selected_row=$(echo "$selection" | sed -n '2p')

        if [[ "$key" == "q" || -z "$selection" ]]; then
            break
        fi

        if [[ "$key" == "tab" ]]; then
            if [[ "$current_mode" == "all" ]]; then
                current_mode="pinned"
            else
                current_mode="all"
            fi
            continue
        fi

        # Extract the precise cliphist keys out of our customized string boundaries
        local raw_content="${selected_row#* │ }"
        local clean_cid="${selected_row%% │ *}"
        clean_cid="${clean_cid##* }"

        if [[ "$key" == "ctrl-p" && -n "$raw_content" ]]; then
            local pinned_items=(${(f)"$(load_pins)"})
            if (( ${pinned_items[(I)$raw_content]} )); then
                remove_pin "$raw_content"
            else
                save_pin "$raw_content"
            fi
            continue
        fi

        if [[ "$key" == "ctrl-d" && -n "$clean_cid" ]]; then
            echo "$clean_cid	$raw_content" | cliphist delete 2>/dev/null
            remove_pin "$raw_content"
            continue
        fi

        if [[ "$key" == "ctrl-x" ]]; then
            clear
            print -n "Wipe all unpinned clipboard logs history? (y/N): "
            read confirm_wipe
            if [[ "${confirm_wipe:l}" == "y" ]]; then
                local pinned_items=(${(f)"$(load_pins)"})
                cliphist wipe 2>/dev/null
                # Re-seed pins data arrays straight back into cliphist engine buffers
                for text in "${pinned_items[@]}"; do
                    print -n "$text" | cliphist store 2>/dev/null
                done
            fi
            continue
        fi

        if [[ -z "$key" && -n "$selected_row" ]]; then
            # Decode payload cleanly through native binary tools prior to clipboard injection
            local decoded_data=$(echo "$clean_cid	$raw_content" | cliphist decode 2>/dev/null)
            print -n "$decoded_data" | wl-copy 2>/dev/null
            break
        fi
    done
}

run_widget_loop
