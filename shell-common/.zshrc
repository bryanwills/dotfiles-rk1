fastfetch
# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time Oh My Zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="powerlevel10k/powerlevel10k"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "dd.mm.yyyy"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# You may need to manually set your language environment
export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='nvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch $(uname -m)"

# Set personal aliases, overriding those provided by Oh My Zsh libs,
# plugins, and themes. Aliases can be placed here, though Oh My Zsh
# users are encouraged to define aliases within a top-level file in
# the $ZSH_CUSTOM folder, with .zsh extension. Examples:
# - $ZSH_CUSTOM/aliases.zsh
# - $ZSH_CUSTOM/macos.zsh
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

# ALL ALIASES GOES HERE
alias la="lsd -a"
alias nal="nano -l"
alias ..="cd .."
alias rtm="$HOME/custom-scripts/RTM/rtm.py"
alias mc="micro"

# YOUTUBE DOWNLOADS ALIASES
# Alias for a single song
alias song='yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-thumbnail --embed-metadata -o "~/Music/%(title)s.%(ext)s"'

# Alias for a whole album/playlist (creates a folder automatically)
alias album='yt-dlp -x --audio-format mp3 --audio-quality 0 --yes-playlist --embed-thumbnail --embed-metadata --parse-metadata "playlist_index:%(track_number)s" -o "~/Music/%(album,playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"'
# --- SYSTEM ALIASES ---
alias update="sudo pacman -Syu"
alias install="sudo pacman -S"
alias cleanup='sudo pacman -Rns $(pacman -Qtdq); sudo paccache -rk2'

# --- THE RICE ALIASES ---
# Open all your main "Island" configs in one go to tweak them
alias rice="nano ~/.config/hypr/hyprland.conf ~/.config/waybar/config ~/.config/waybar/style.css ~/.config/rofi/style.css"

# Reload everything after a manual tweak
alias reload="hyprctl reload && killall waybar && waybar &"

# Quick access to your scripts
alias wall="~/.config/hypr/scripts/changewall.sh"
alias keys="~/.config/hypr/scripts/keybinds.sh"

# Edit cmd_vault commands
alias vedit="$EDITOR ~/.local/share/cmd_vault.txt"

# Cliphist (Rofi Clipboard)
alias clip='cliphist list | rofi -dmenu -theme ~/.config/rofi/themes/rk1-dark.rasi | cliphist decode | wl-copy'

# Dashoboard
alias dashboard="python3 ~/custom-scripts/Dashboard/dashboard.py"

# Aliases viewer and selector
alias als="~/custom-scripts/Show-Aliases/show-aliases.sh"

# Arch Update Check before updating system
alias upcheck="/usr/bin/arch-update-check"

# Alias to run the AUR/GitHub release automator
alias uprelease='~/arch-projects/arch-update-check/release.sh'

# Opens keybinds.conf & windowrules.conf at the same time
alias hyprconf='micro -multiopen vsplit ~/.config/hypr/configs/keybinds.conf ~/.config/hypr/configs/windowrules.conf'

# Budget Buddy Finance Manager
alias budget='python3 ~/custom-scripts/Budget-Buddy/budget-buddy.py'
# Make sure this is at the very bottom of the file
[[ -f ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]] && \
    source ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# --- GNU Stow Aliases ---

# Activate a setup (e.g., 's-up setup-v1')
alias s-up='stow -d ~/dotfiles -t ~'

# Deactivate a setup (e.g., 's-down setup-v1')
alias s-down='stow -D -d ~/dotfiles -t ~'

# "Restow" (Quick refresh if you added new files to a folder)
alias s-re='stow -R -d ~/dotfiles -t ~'

# List active symlinks in your config (The "Are my links okay?" check)
# Corrected alias with quotes
alias s-check='find ~/.config -maxdepth 1 -type l -ls'

alias v1='stow -d ~/dotfiles -D setup-v2 -t ~; stow -d ~/dotfiles -S setup-v1 -t ~; swww img ~/.config/backgrounds/wall.png; hyprctl reload; kill -SIGUSR1 $(pgrep kitty)'
alias v2='stow -d ~/dotfiles -D setup-v1 -t ~; stow -d ~/dotfiles -S setup-v2 -t ~; swww img ~/.config/backgrounds/wall.png; hyprctl reload; kill -SIGUSR1 $(pgrep kitty)'
alias v3='stow -d ~/dotfiles -D setup-v1 -D setup-v2 -t ~; stow -d ~/dotfiles -S setup-v3 -t ~; swww img ~/.config/backgrounds/wall.png; hyprctl reload; kill -SIGUSR1 $(pgrep kitty)'
# Function to clean all setups (Internal helper)
alias v-clean='stow -d ~/dotfiles -D setup-v1 setup-v2 setup-v3 -t ~ 2>/dev/null'

alias reclaim="python3 ~/arch-projects/Reclaim-Linux/reclaim-linux.py"

# Timeshift aliases
alias restore-list='timeshift --list'
alias restore-now='sudo timeshift --restore'

# Now set the style AFTER sourcing
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=196,bold'


# cat ~/.cache/wal/sequences

# Yazi "Change Directory" on quit
function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
	yazi "$@" --cwd-file="$tmp"
	if cwd="$(cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
		builtin cd -- "$cwd"
	fi
	rm -f -- "$tmp"
}
export EDITOR='micro'
export VISUAL='geany'

dotsync() {
    # 1. Update the package list in your dotfiles
    pacman -Qqe > ~/dotfiles/pkglist.txt
    
    # 2. Jump to the dotfiles directory
    cd ~/dotfiles || return
    
    # 3. Show a "short & sweet" status of what has changed
    echo "󰚰  Changes detected in your dotfiles:"
    git status -sb
    echo ""
    
    # 4. Ask for permission to proceed
    echo -n "󰏖  Commit and push these changes? [y/N]: "
    read -q "REPLY"
    echo "" # Just for a new line
    
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Sync: $(date +'%H:%M')" -m "$(git status --porcelain)"
        git push
        date +"%m/%d %H:%M" > ~/.cache/last_synced
        echo "󰄬  Everything is safe on GitHub."
    else
        echo "󰅙  Sync aborted. No changes pushed."
    fi
}

export GTK_MESSAGES_DEBUG=none
export G_MESSAGES_DEBUG=none
export PATH="$HOME/custom-scripts:$PATH"

echo "󱓞 Remember to run 'dotsync' after your tweaks! Have a GOOD DAY!!!"

# Launch dashboard only in interactive desktop terminals
if [[ -o interactive && "$TERM" =~ "foot|xterm-kitty" ]]; then
    # Use the absolute path to be safe
    python3 "$HOME/custom-scripts/Dashboard/dashboard.py"
fi

# --- XC-Manager Settings ---
# Load the script
source ~/arch-projects/XC-Manager/xc-manager.sh

# Custom UI (zstyle)
# Change the separator to your favorite icon or symbol
zstyle ':xc:*' separator "->" 
# Set your FZF colors (Matches most dark/Arch themes)
zstyle ':xc:*' fzf_colors "fg:7,hl:4,fg+:15,hl+:12,info:2,prompt:5,pointer:12"

# --- History Settings (Required for 'xc' to work) ---
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt appendhistory
setopt sharehistory  # Highly recommended: shares history across all open terminals

if [ -f ~/.config/hypr/is_v1 ]; then
    CURRENT_V="V1-Dark"
elif [ -f ~/.config/hypr/is_v2 ]; then
    CURRENT_V="V2-Light"
elif [ -f ~/.config/hypr/is_v3 ]; then
    CURRENT_V="V3-Red"
else
    CURRENT_V="Unknown"
fi

echo "System Version: $CURRENT_V"
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
