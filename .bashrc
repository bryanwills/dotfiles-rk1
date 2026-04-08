# ── Colours ───────────────────────────────────────────────────────────────────
export LS_COLORS='di=1;34:ln=1;36:so=1;35:pi=33:ex=1;32:bd=1;33:cd=1;33:su=1;31:sg=1;31:tw=1;34:ow=1;34:'
alias ls='ls --color=auto'
alias grep='grep --color=auto'

export LESS_TERMCAP_mb=$'\e[1;31m'
export LESS_TERMCAP_md=$'\e[1;34m'
export LESS_TERMCAP_me=$'\e[0m'
export LESS_TERMCAP_so=$'\e[1;33m'
export LESS_TERMCAP_se=$'\e[0m'
export LESS_TERMCAP_us=$'\e[4;36m'
export LESS_TERMCAP_ue=$'\e[0m'
export MANPAGER='less -R'

# ── Completion ────────────────────────────────────────────────────────────────
if ! shopt -oq posix; then
    [[ -f /usr/share/bash-completion/bash_completion ]] && \
        source /usr/share/bash-completion/bash_completion
fi

# ── Prompt ────────────────────────────────────────────────────────────────────
_git_branch() {
    local branch
    branch=$(git symbolic-ref --short HEAD 2>/dev/null) || return
    local icon=$'\ue0a0'
    echo " \e[38;5;141m${icon} ${branch}\e[0m"
}

_separator() {
    printf "\e[38;5;238m%*s\e[0m\n" "${COLUMNS:-$(tput cols)}" '' | tr ' ' '─'
}

_prompt() {
    local exit_code=$?
    _separator
    # Path + git branch on first line
    PS1="\[\e[38;5;33m\]\w\[\e[0m\]$(_git_branch)\n"
    # Arrow on second line — green on success, red on failure
    if [[ $exit_code -eq 0 ]]; then
        PS1+="\[\e[38;5;141m\]❯\[\e[0m\] "
    else
        PS1+="\[\e[38;5;196m\]❯\[\e[0m\] "
    fi
}

PROMPT_COMMAND='_prompt'

# ── User Configuration ────────────────────────────────────────────────────────
export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8
export EDITOR='micro'
export VISUAL='geany'
export PATH="$HOME/custom-scripts:$HOME/.local/bin:$PATH"

# ── Aliases ───────────────────────────────────────────────────────────────────
alias la="lsd -a"
alias nal="nano -l"
alias ..="cd .."
alias rtm="$HOME/custom-scripts/RTM/rtm.py"
alias mc="micro"
alias update="sudo pacman -Syu"
alias install="sudo pacman -S"
alias cleanup='sudo pacman -Rns $(pacman -Qtdq); sudo paccache -rk2'
alias rice="micro ~/.config/hypr/hyprland.conf ~/.config/waybar/config ~/.config/waybar/style.css ~/.config/rofi/style.css"
alias reload="hyprctl reload && killall waybar && waybar &"
alias wall="~/custom-scripts/changewall.sh"
alias keys="~/custom-scripts/keybinds.sh"
alias dashboard="python3 ~/custom-scripts/Dashboard/dashboard.py"
alias hyprconf='micro -multiopen vsplit ~/.config/hypr/configs/keybinds.conf ~/.config/hypr/configs/windowrules.conf'
alias reclaim="python3 ~/arch-projects/Reclaim-Linux/reclaim-linux.py"
alias als="~/custom-scripts/Show-Aliases/show-aliases.sh"
alias vedit="$EDITOR ~/.local/share/cmd_vault.txt"
alias clip='cliphist list | rofi -dmenu -theme ~/.config/rofi/themes/rk1-dark.rasi | cliphist decode | wl-copy'
alias song='yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-thumbnail --embed-metadata -o "~/Music/%(title)s.%(ext)s"'
alias album='yt-dlp -x --audio-format mp3 --audio-quality 0 --yes-playlist --embed-thumbnail --embed-metadata --parse-metadata "playlist_index:%(track_number)s" -o "~/Music/%(album,playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"'
alias uprelease='~/arch-projects/arch-update-check/release.sh'
alias upcheck="/usr/bin/arch-update-check"
alias restore-list='timeshift --list'
alias restore-now='sudo timeshift --restore'
alias t='tt tui'
alias ts='tt stop'
alias orphaned="pacman -Qdt"

# ── Auto CD ───────────────────────────────────────────────────────────────────
shopt -s autocd

# ── Functions ─────────────────────────────────────────────────────────────────
y() {
    local tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
    yazi "$@" --cwd-file="$tmp"
    if cwd="$(cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
        builtin cd -- "$cwd"
    fi
    rm -f -- "$tmp"
}

dotsync() {
    pacman -Qqe > ~/dotfiles/pkglist.txt
    echo "󰒲 Copying live config to GitHub folder..."
    rsync -a --delete ~/.config/hypr ~/dotfiles/setup-v3/.config/
    rsync -a --delete ~/.config/waybar ~/dotfiles/setup-v3/.config/
    rsync -a --delete ~/.config/nwg-look ~/dotfiles/setup-v3/.config/
    rsync -a --delete ~/.config/wal ~/dotfiles/setup-v3/.config/
    rsync -a --delete ~/custom-scripts ~/dotfiles/shell-common
    rsync -a --delete ~/.zshrc ~/dotfiles/shell-common
    cd ~/dotfiles || return
    echo "󰚰 Changes detected in your dotfiles:"
    git status -sb
    echo -n "󰏖 Commit and push these changes? [y/N]: "
    read -r REPLY
    echo ""
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Sync: $(date +'%H:%M')" -m "$(git status --porcelain)"
        git push
        date +"%m/%d %H:%M" > ~/.cache/last_synced
        echo "󰄬 Everything is safe on GitHub."
    else
        echo "󰅙 Sync aborted."
    fi
}

# ── History ───────────────────────────────────────────────────────────────────
HISTFILE=~/.bash_history
HISTSIZE=10000
HISTFILESIZE=10000
shopt -s histappend
PROMPT_COMMAND="history -a; _prompt"

# ── Startup ───────────────────────────────────────────────────────────────────
echo "󱓞 System Version: Main (bash fallback)"
[[ -f ~/.zsh_aliases ]] && source ~/.zsh_aliases
