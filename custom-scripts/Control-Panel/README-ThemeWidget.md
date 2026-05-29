# Theme Configuration Widget

Version: [v0.1.0]

A lightweight, native GTK utility designed to dynamically manage desktop themes, colour modes, and accents for bar-free configurations. This tool removes the need for heavy desktop shells by applying customized colour palettes directly to your system components.

## Features
* **Zero Shell Dependencies**: Operates completely independently of standard desktop shell components to preserve system RAM.
* **Dynamic Accent Swapping**: Instantly update interface highlights across your setup.
* **Predefined Palettes**: Switch between tailored dark modes, light modes, and muted configurations on the fly.

## Installation & Usage

1. **Make the script executable:**

`chmod +x theme-widget.py`

2. **Execute the widget directly or map it to a window manager keybinding:**

`./theme-widget.py`

## User Configuration

You can easily expand or alter the available theme characteristics by modifying the script files directly. Below are the structural snippets where you can insert your own custom values.

1. **Theme Modes Configuration**

To add or adjust base background layouts (such as shifting from deep dark to mid-grey profiles), locate and update the following dictionary block in the script source:

```zsh
# --- Background Preset Profiles ---
BG_PROFILES = {
    "dark": {
        "bg": "rgba(29, 32, 33, 0.9)",
        "text": "#ffffff",
        "hint": "#aaaaaa"
    },
    "d-glass": {
        "bg": "rgba(0, 0, 0, 0.40)",
        "text": "#e0e6ed",
        "hint": "#4c566a"
    },
    
    "light": {
        "bg": "rgba(247, 247, 247, 0.9)",
        "text": "#000000",
        "hint": "#555555"
    },
    "l-glass": {
        "bg": "rgba(255, 255, 255, 0.30)",
        "text": "#282828",
        "hint": "#666666"
    },
    "paper": {
        "bg": "rgba(251, 241, 199, 0.9)",
        "text": "#3c3836",
        "hint": "#7c6f64"
    },
    "translucent": {
        "bg": "rgba(74, 74, 74, 0.75)",
        "text": "#ffffff",
        "hint": "#aaaaaa"
    }
}
```
If you add any new BG_PROFILES, you will also need to add them here:
```zsh
# --- Row 1: Background Mode Selector ---
        for mode_name in BG_PROFILES.keys():
            btn_label = mode_name.capitalize()
            
            if mode_name == "dark": btn_label = "󰖔 Dark"
            elif mode_name == "d-glass": btn_label = "󰛢 D-Glass"
            elif mode_name == "light": btn_label = "󰖙 Light"
            elif mode_name == "l-glass": btn_label = "󰛢 L-Glass"
            elif mode_name == "paper": btn_label = "󰃛 Paper"
            elif mode_name == "translucent": btn_label = " Gray"
```            

2. **Accent Colours Configuration**

To include new highlight profiles that match your latest wallpaper additions, adapt the accent lookup mappings inside this configuration block:

```zsh
ACCENTS = {
    "Red": "#960723",
    "Blue": "#0e5989",
    "Gray": "#b7b7b8",
    "Cyan": "#51fefc",
    "Magenta": "#9d2dc0",
    "Green": "#29e171",
    "Yellow": "#c9a800",
    "Black": "#151515",
    "Fire": "rgba(255, 137, 22, 0.86)",
    "Flames": "#f8541f"
}
```
> *NOTE: If you have any questions or issues, please drop a message in the Discussions here on GitHub.*

### License

Distributed under the MIT License. See LICENSE for details.
