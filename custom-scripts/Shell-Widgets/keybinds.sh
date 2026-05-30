#!/bin/bash

#----------------------------------------------------------------------------------
# HYPRLAND KEYBINDS
# Author: Lukas Grumlik - Rakosn1cek
# Created: 2026-01
# Version: 0.1.0
# Descriptions: 
# Minimalist Hyprland keybinds zsh+fzf widget for Hyprland.
#----------------------------------------------------------------------------------


CONFIG="$HOME/.config/hypr/configs/keybinds.conf"

HEADER_TEXT="
		     󰢭  HYPRLAND KEYBINDS v0.1.0
		 Minimalist Hyprland keybinds view widget
"


# 1. Fetch bind and bindd
# 2. Convert $mainMod to SUPER
# 3. Use sed to remove the 'bindd =' part
grep -E '^bind[a-z]*' "$CONFIG" | \
    sed "s/\$mainMod/SUPER/g" | \
    sed -E 's/^bind[a-z]* *= *//g' | \
    awk -F, '{
        # Field 1: Modifier
        mod = $1; gsub(/^[ \t]+|[ \t]+$/, "", mod);
        if (mod == "") mod = "NONE";

        # Field 2: Key
        key = $2; gsub(/^[ \t]+|[ \t]+$/, "", key);

        # Field 3: Description (for bindd) or Command (for bind)
        desc = $3; gsub(/^[ \t]+|[ \t]+$/, "", desc);

        if (mod != "" && key != "")
            printf "%-10s | %-10s | ➜  %s\n", mod, key, desc
    }' | \
    column -t -s '|' | \
    fzf --header "$HEADER_TEXT" --header-first --reverse
