#!/bin/zsh

#----------------------------------------------------------------------------------
# SHOW ALIASES
# Author: Lukas Grumlik - Rakosn1cek
# Created: 2026-01
# Version: 0.1.4
# Descriptions: 
# Minimalist Aliases zsh+fzf widget for Hyprland.
#----------------------------------------------------------------------------------


# 1. Search both .zshrc and the new .zsh_aliases file
# -h ensures grep doesn't print the filename, keeping the list clean
alias_list=$(grep -h "^alias " ~/.zshrc ~/.zsh_aliases 2>/dev/null | sed -E "s/^alias ([^=]+)=['\"](.*)['\"]$/\1 ➜ \2/")

HEADER_TEXT="
		        SHOW ALIASES v0.1.4
		   Minimalist Alias view widget

ENTER: Copy to Clipboard | ESC: Quit
"

# 2. Interactive fzf
selected=$(echo "$alias_list" | column -t -s '➜' | fzf --ansi \
    --header "$HEADER_TEXT" \
    --header-first \
    --border \
    --margin=5% \
    --prompt="Alias > " \
    --color="header:#565f89,prompt:#565f89" \
    --reverse \
    --preview-window="bottom:5:wrap" \
    --preview="echo 'Full Command:'; echo {2..}")

# 4. Clipboard Logic
if [ -n "$selected" ]; then
    # Grab the first word as the alias name
    alias_name=$(echo "$selected" | awk '{print $1}')
    
    # Strip any trailing line breaks and copy the pure alias name to the clipboard
    echo -n "$alias_name" | wl-copy
    
    # Exit the script so the hosting terminal window drops immediately
    kill -15 $PPID
fi
