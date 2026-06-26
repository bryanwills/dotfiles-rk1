#!/usr/bin/env zsh

CONFIG_PATH="${HOME}/.config/project-spaces.json"

if [[ ! -d "$(dirname "$CONFIG_PATH")" ]]; then
    mkdir -p "$(dirname "$CONFIG_PATH")"
fi
if [[ ! -f "$CONFIG_PATH" ]]; then
    echo '{}' > "$CONFIG_PATH"
fi

load_profiles() {
    jq -r 'keys[]' "$CONFIG_PATH" 2>/dev/null
}

launch_space() {
    local name="$1"
    local data=$(jq -r --arg name "$name" '.[$name]' "$CONFIG_PATH")
    local directory=$(echo "$data" | jq -r '.directory')
    
    local project_dir="${directory/#\~/$HOME}"
    local socket_name="${name// /_}"
    local socket_path="/tmp/kitty-${socket_name}.sock"
    
    if [[ -S "$socket_path" ]]; then
        rm -f "$socket_path"
    fi

    KITTY_ALLOW_REMOTE_CONTROL=yes kitty \
        --listen-on "unix:${socket_path}" \
        --directory "$project_dir" \
        --title "$name" >/dev/null 2>&1 &
        
    for i in {1..40}; do
        [[ -S "$socket_path" ]] && break
        sleep 0.1
    done

    if [[ ! -S "$socket_path" ]]; then
        return
    fi
    sleep 0.2

    local first=true
    echo "$data" | jq -c '.targets[]' | while read -r target; do
        local target_file=$(echo "$target" | jq -r '.file')
        local target_type=$(echo "$target" | jq -r '.type')
        local resolved_path="$target_file"
        
        if [[ "$target_type" == "editor" && ! "$target_file" = /* ]]; then
            local base_name=$(basename "$target_file")
            local found_path=$(find "$project_dir" -type f -name "$base_name" -print -quit 2>/dev/null)
            if [[ -n "$found_path" ]]; then
                resolved_path=$(realpath --relative-to="$project_dir" "$found_path")
            fi
        fi

        local cmd_args=()
        if [[ "$target_type" == "editor" ]]; then
            cmd_args=("/usr/bin/micro" "$resolved_path")
        else
            cmd_args=("/usr/bin/yazi")
        fi

        if $first; then
            kitty @ --to "unix:${socket_path}" send-text "clear && ${cmd_args[*]}\n"
            kitty @ --to "unix:${socket_path}" set-tab-title "$(basename "$target_file")"
            first=false
        else
            kitty @ --to "unix:${socket_path}" launch --type=tab --cwd "$project_dir" --tab-title "$(basename "$target_file")" "${cmd_args[@]}"
        fi
    done
}

create_or_edit_profile() {
    local edit_name="$1"
    local default_dir=""
    local default_files=""
    
    if [[ -n "$edit_name" ]]; then
        default_dir=$(jq -r --arg name "$edit_name" '.[$name].directory' "$CONFIG_PATH")
        default_files=$(jq -r --arg name "$edit_name" '.[$name].targets | map(.file) | join(", ")' "$CONFIG_PATH")
        echo "=== Editing Profile: $edit_name ==="
    else
        echo "=== Create New Profile ==="
    fi

    local p_name="$edit_name"
    if [[ -z "$p_name" ]]; then
        print -n "Profile Name (Leave empty to abort): "
        read p_name
        [[ -z "$p_name" ]] && return
    fi

    print -n "Project Directory Path [$default_dir] (Leave empty to abort): "
    read p_dir
    p_dir="${p_dir:-$default_dir}"
    [[ -z "$p_dir" ]] && return

    print -n "Files (comma separated) [$default_files] (Leave empty to abort): "
    read p_files
    p_files="${p_files:-$default_files}"
    [[ -z "$p_files" ]] && return

    local targets_json="[]"
    IFS=',' read -rA files_array <<< "$p_files"
    for f in "${files_array[@]}"; do
        local f_clean="${f## }"
        f_clean="${f_clean%% }"
        if [[ -n "$f_clean" ]]; then
            local t_type="manager"
            if [[ "${f_clean:l}" != "yazi" ]]; then
                local ext="${f_clean:e}"
                if [[ -z "$ext" || "$ext" =~ ^(py|lua|conf|sh|txt|json|toml|lock|md|bash|fish|zsh|yaml|yml|ini|theme|rules|desktop|service|awk|sed)$ ]]; then
                    t_type="editor"
                fi
            fi
            targets_json=$(echo "$targets_json" | jq --arg type "$t_type" --arg file "$f_clean" '. += [{"type": $type, "file": $file}]')
        fi
    done

    if [[ "$targets_json" == "[]" ]]; then
        targets_json='[{"type":"manager","file":"yazi"}]'
    fi

    local tmp_json=$(mktemp)
    jq --arg name "$p_name" --arg dir "$p_dir" --argjson targets "$targets_json" \
        '.[$name] = {"directory": $dir, "targets": $targets}' "$CONFIG_PATH" > "$tmp_json" && mv "$tmp_json" "$CONFIG_PATH"
}

delete_profile() {
    local name="$1"
    [[ -z "$name" ]] && return
    local tmp_json=$(mktemp)
    jq --arg name "$name" 'del(.[$name])' "$CONFIG_PATH" > "$tmp_json" && mv "$tmp_json" "$CONFIG_PATH"
}

run_tui() {
    while true; do
        # Fixed mapping logic using an explicit array string split boundary flag
        local profiles=("${(@f)$(load_profiles)}")
        
        # Build out the left hand panel content string
        local cmd_menu=$'COMMANDS\n\n[Enter] \u2192 Launch\n[n]     \u2192 New\n[e]     \u2192 Edit\n[x]     \u2192 Delete\n[q]     \u2192 Quit'

        # Render layout splits via fzf preview windows and custom boundary mappings
        local selection=$(printf '%s\n' "${profiles[@]}" | fzf \
            --ansi \
            --layout=reverse \
            --border=rounded \
            --margin=1,2 \
            --height=15 \
            --prompt="Select Workspace" \
            --color="header:#565f89,prompt:#565f89" \
            --preview-window=left,18,border-right \
            --preview="echo '$cmd_menu'" \
            --expect="n,e,x,q")

        local key=$(echo "$selection" | sed -n '1p')
        local target_name=$(echo "$selection" | sed -n '2p')

        if [[ "$key" == "q" || -z "$selection" ]]; then
            break
        elif [[ "$key" == "n" ]]; then
            clear
            create_or_edit_profile
        elif [[ "$key" == "e" && -n "$target_name" ]]; then
            clear
            create_or_edit_profile "$target_name"
        elif [[ "$key" == "x" && -n "$target_name" ]]; then
            delete_profile "$target_name"
        elif [[ -z "$key" && -n "$target_name" ]]; then
            launch_space "$target_name"
            break
        fi
    done
}

run_tui
