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
alias rice="nano ~/.config/hypr/hyprland.conf ~/.config/waybar/config ~/.config/waybar/style.css ~/.config/rofi/style.css"
alias reload="hyprctl reload && killall waybar && waybar &"
alias wall="~/.config/hypr/scripts/changewall.sh"
alias keys="~/.config/hypr/scripts/keybinds.sh"
alias dashboard="python3 ~/custom-scripts/Dashboard/dashboard.py"
alias hyprconf='micro -multiopen vsplit ~/.config/hypr/configs/keybinds.conf ~/.config/hypr/configs/windowrules.conf'

# --- YouTube Download Aliases ---
alias song='yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-thumbnail --embed-metadata -o "~/Music/%(title)s.%(ext)s"'
alias album='yt-dlp -x --audio-format mp3 --audio-quality 0 --yes-playlist --embed-thumbnail --embed-metadata --parse-metadata "playlist_index:%(track_number)s" -o "~/Music/%(album,playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"'

# --- Stow Aliases ---
alias s-up='stow -d ~/dotfiles -t ~'
alias s-down='stow -D -d ~/dotfiles -t ~'
alias s-re='stow -R -d ~/dotfiles -t ~'
alias s-check='find ~/.config -maxdepth 1 -type l -ls'

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
    pacman -Qqe > ~/dotfiles/pkglist.txt
    cd ~/dotfiles || return
    echo "󰚰  Changes detected in your dotfiles:"
    git status -sb
    echo -n "󰏖  Commit and push these changes? [y/N]: "
    read -q "REPLY"
    echo ""
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Sync: $(date +'%H:%M')" -m "$(git status --porcelain)"
        git push
        date +"%m/%d %H:%M" > ~/.cache/last_synced
        echo "󰄬  Everything is safe on GitHub."
    else
        echo "󰅙  Sync aborted."
    fi
}

# --- Plugin & Theme Settings ---
[[ -f ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]] && \
    source ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=196,bold'

# --- XC-Manager Settings ---
# Resolve the read-only conflict by unsetting if it exists, then sourcing
unset XC_VERSION 2>/dev/null
source ~/arch-projects/XC-Manager/xc-manager.sh
zstyle ':xc:*' separator "->" 
zstyle ':xc:*' fzf_colors "fg:7,hl:4,fg+:15,hl+:12,info:2,prompt:5,pointer:12"

# --- History ---
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt appendhistory
setopt sharehistory

# --- Startup ---
echo "󱓞 System Version: Main (Neon-Master)"
if [[ -o interactive && "$TERM" =~ "foot|xterm-kitty" ]]; then
    python3 "$HOME/custom-scripts/Dashboard/dashboard.py"
fi
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
