# --- Colours ---
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

# --- Completion ---
autoload -Uz compinit && compinit
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu select

# --- Prompt (replaces p10k) ---
autoload -Uz vcs_info
precmd() { vcs_info }
local _git_icon=$'\ue0a0'
zstyle ':vcs_info:git:*' formats " %F{141}${_git_icon} %b%f"
zstyle ':vcs_info:git:*' actionformats " %F{141}${_git_icon} %b%f %F{red}(%a)%f"
zstyle ':vcs_info:*' enable git
setopt PROMPT_SUBST

PROMPT='%F{33}%~%f${vcs_info_msg_0_}
%(?.%F{141}❯%f.%F{196}❯%f) '
RPROMPT='%F{240}%D{%H:%M}%f %(?.%F{green}✓.%F{196}✗ %?)%f'

fastfetch

# --- User Configuration ---
export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8
export EDITOR='micro'
export VISUAL='geany'
export PATH="$HOME/custom-scripts:$PATH"

# --- Aliases ---
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

# Edit cmd_vault commands
alias vedit="$EDITOR ~/.local/share/cmd_vault.txt"

# Cliphist (Rofi Clipboard)
alias clip='cliphist list | rofi -dmenu -theme ~/.config/rofi/themes/rk1-dark.rasi | cliphist decode | wl-copy'

# --- YouTube Download Aliases ---
alias song='yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-thumbnail --embed-metadata -o "~/Music/%(title)s.%(ext)s"'
alias album='yt-dlp -x --audio-format mp3 --audio-quality 0 --yes-playlist --embed-thumbnail --embed-metadata --parse-metadata "playlist_index:%(track_number)s" -o "~/Music/%(album,playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"'

# Alias to run the AUR/GitHub release automator
alias uprelease='~/arch-projects/arch-update-check/release.sh'

# Arch Update Check before updating system
alias upcheck="/usr/bin/arch-update-check"

# Timeshift aliases
alias restore-list='timeshift --list'
alias restore-now='sudo timeshift --restore'

# Project Time Tracker
alias t='tt tui'
alias ts='tt stop'

# Added by XC-Manager
alias orphaned="pacman -Qdt"
 
# --- Functions ---
function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
	yazi "$@" --cwd-file="$tmp"
	if cwd="$(cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
		builtin cd -- "$cwd"
	fi
	rm -f -- "$tmp"
}

dotsync() {
    # Update your package list (Original Step)
    pacman -Qqe > ~/dotfiles/pkglist.txt

    # Only include the apps I want to track (the "curtain" folders).
    echo "󰒲 Copying live config to GitHub folder..."
    rsync -a --delete ~/.config/hypr ~/dotfiles/setup-v3/.config/
    rsync -a --delete ~/.config/waybar ~/dotfiles/setup-v3/.config/
    rsync -a --delete ~/.config/nwg-look ~/dotfiles/setup-v3/.config/
    rsync -a --delete ~/.config/wal ~/dotfiles/setup-v3/.config/
    rsync -a --delete ~/custom-scripts ~/dotfiles/shell-common
    rsync -a --delete ~/.zshrc ~/dotfiles/shell-common
    # GitHub Upload (Original Code starts here)
    cd ~/dotfiles || return
    echo "󰚰 Changes detected in your dotfiles:"
    git status -sb
    echo -n "󰏖 Commit and push these changes? [y/N]: "
    read -q "REPLY"
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

# --- zsh-autosuggestions (sourced directly, no plugin manager) ---
source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

# --- XC-Manager Settings ---
# 1. Add the autoload folder to your function path
fpath=(~/arch-projects/XC-Manager/autoload $fpath)
# 2. Tell Zsh to "lazy-load" these functions (no code is run yet)
autoload -Uz xc fzf-vault-widget
# 3. Register the widget with Zsh's Line Editor (ZLE)
zle -N fzf-vault-widget
# 4. Bind the shortcut
bindkey '^G' fzf-vault-widget
# 5. UI Customization (These are read by the functions when called)
zstyle ':xc:*' separator "->" 
zstyle ':xc:*' fzf_colors "fg:7,hl:4,fg+:15,hl+:12,info:2,prompt:5,pointer:12"

# --- History ---
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt appendhistory
setopt sharehistory
setopt autocd

# --- Startup ---
echo "󱓞 System Version: Main"
if [[ -o interactive && "$TERM" =~ "foot|xterm-kitty" ]]; then
    python3 "$HOME/custom-scripts/Dashboard/dashboard.py"
fi
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local

source ~/.local/share/extraterm/extraterm-commands-0.9.4/setup_extraterm_zsh.zsh
export PATH="$HOME/.local/bin:$PATH"
[[ -f ~/.zsh_aliases ]] && source ~/.zsh_aliases
# --- RTFM plugin ---
source ~/arch-projects/mend/mend.plugin.zsh
# Created by newuser for 5.9
