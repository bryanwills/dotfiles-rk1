#!/bin/zsh

# High-density, code-focused clipboard viewer
cliphist list | rofi -dmenu -p "Clipboard" \
    -theme-str 'window { 
        width: 1000px; 
        height: 600px; 
        border: 2px; 
        border-color: white; 
        background-color: rgba(0, 0, 0, 0.6); 
        border-radius: 0px; 
    }' \
    -theme-str 'listview { 
        columns: 1; 
        lines: 12; 
        spacing: 2px; 
        fixed-height: false;
    }' \
    -theme-str 'element { 
        padding: 4px 10px; 
        margin: 0px;
    }' \
    -theme-str 'element-text { 
        font: "JetBrainsMono Nerd Font 10"; 
        vertical-align: 0.5;
    }' \
    -theme-str 'element selected { 
        border: 0px 0px 0px 4px; 
        border-color: white; 
        background-color: rgba(255, 255, 255, 0.1); 
    }' \
    -theme-str 'element-icon { enabled: false; }' \
    | cliphist decode | wl-copy
