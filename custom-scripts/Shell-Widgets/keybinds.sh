#!/bin/bash

#----------------------------------------------------------------------------------
# HYPRLAND KEYBINDS
# Author: Lukas Grumlik - Rakosn1cek
# Created: 2026-01
# Version: 0.1.0
# Descriptions: 
# Minimalist Hyprland keybinds zsh+fzf widget for Hyprland.
#----------------------------------------------------------------------------------


CONFIG="$HOME/.config/hypr/configs/keybinds.lua"

HEADER_TEXT="
		      󰢭  HYPRLAND KEYBINDS v0.1.0
		 Minimalist Hyprland keybinds view widget
"


# 1. Filter lines containing the hl.bind function
# 2. Strip the initial function call characters
# 3. Parse the key combination and the command logic separately
grep 'hl.bind' "$CONFIG" | \
    sed -E 's/^[ \t]*hl\.bind\(//' | \
    awk -F, '{
        # Isolate the complete key binding definition (the first argument)
        key_part = $1;
        
        # Rebuild the remaining fields to capture the entire command payload
        cmd_part = "";
        for(i=2; i<=NF; i++) {
            cmd_part = (cmd_part == "") ? $i : cmd_part "," $i;
        }
        
        # Strip syntax characters, quotes, and clean up concatenation dots
        gsub(/"/, "", key_part);
        gsub(/[ \t]*\.\.[ \t]*/, " ", key_part);
        gsub(/^[ \t]+|[ \t]+$/, "", key_part);
        
        # Clean up trailing function characters from the payload definition
        gsub(/^[ \t]+|[ \t]+$/, "", cmd_part);
        sub(/\)[ \t]*$/, "", cmd_part);
        
        # Extract the inner raw command if wrapped in an executive helper call
        if (cmd_part ~ /^hl\.dsp\.exec_cmd\(.*\)$/) {
            sub(/^hl\.dsp\.exec_cmd\(/, "", cmd_part);
            sub(/\)$/, "", cmd_part);
        }
        gsub(/^"|"$/, "", cmd_part);

        if (key_part != "")
            printf "%-25s | ➜  %s\n", key_part, cmd_part
    }' | \
    column -t -s '|' | \
    fzf --header "$HEADER_TEXT" --header-first --reverse --color="header:#565f89,prompt:#565f89"
