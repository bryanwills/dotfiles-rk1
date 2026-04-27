#!/bin/bash

CONFIG="$HOME/.config/hypr/configs/keybinds.conf"

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
    fzf --header "󰌌 Keybinds" --reverse
