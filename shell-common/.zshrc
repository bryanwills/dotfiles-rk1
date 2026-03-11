# Enable Powerlevel10k instant prompt
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

fastfetch

# --- Oh My Zsh Setup ---
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"

plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
)

# Completion Caching (The Speed Fix)
autoload -Uz compinit
if [[ -n ${ZDOTDIR:-$HOME}/.zcompdump(#qN.m-1) ]]; then
  compinit -C
else
  compinit
fi
zstyle ':omz:plugins:fortunes' skip-compinit yes

source $ZSH/oh-my-zsh.sh

# --- User Configuration ---
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
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
    rsync -a --delete ~/.config/kitty ~/dotfiles/setup-v3/.config/
    rsync -a --delete ~/.config/rofi ~/dotfiles/setup-v3/.config/
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

# --- Plugin & Theme Settings ---
[[ -f ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]] && \
    source ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=196,bold'

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
source ~/arch-projects/RTFM/rtfm.plugin.zsh
