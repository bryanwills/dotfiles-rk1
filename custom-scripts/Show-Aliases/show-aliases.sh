#!/bin/zsh

# 1. Search both .zshrc and the new .zsh_aliases file
# -h ensures grep doesn't print the filename, keeping the list clean
alias_list=$(grep -h "^alias " ~/.zshrc ~/.zsh_aliases 2>/dev/null | sed -E "s/^alias ([^=]+)=['\"](.*)['\"]$/\1 ➜ \2/")

# 3. Interactive fzf
selected=$(echo "$alias_list" | column -t -s '➜' | fzf --ansi \
    --header "ENTER: Run | ESC: Quit" \
    --border="rounded" \
    --margin=5% \
    --prompt="Alias > " \
    --color="border:yellow,header:cyan" \
    --preview-window="top:5:wrap" \
    --preview="echo 'Full Command:'; echo {2..}")

# 4. Execution Logic
if [ -n "$selected" ]; then
    # Grab the first word as the alias name
    alias_name=$(echo "$selected" | awk '{print $1}')
    
    clear
    echo -e "\033[1;33m>> Running Alias:\033[0m $alias_name\n"
    
    # Use 'zsh -i' to ensure the shell knows aliases before running
    zsh -ic "$alias_name"
fi
