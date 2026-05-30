-- Autostart Configuration for Hyprland v0.55
-- File: ~/.config/hypr/configs/autostart.lua

hl.on("hyprland.start", function () 
    -- 1. Core System & Polkit
    -- The hyprland.start event ensures these only run once at launch
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("/usr/lib/polkit-kde-authentication-agent-1")

    -- 2. Theme & Wallpaper
    hl.exec_cmd("awww-daemon & sleep 0.5 && awww img $(cat ~/.cache/wal/wal)")
    hl.exec_cmd("dunst")

    -- 3. Hardware & Utilities
    hl.exec_cmd("brightnessctl set $(cat ~/.cache/brightness_level)")

    -- 4. Clipboard management
    hl.exec_cmd("bash ~/.config/hypr/scripts/cliphist-start.sh")
    hl.exec_cmd("wl-paste --type text --watch cliphist store -max-items 200")
    hl.exec_cmd("wl-paste --type image --watch cliphist store -max-items 200")

    -- 5. Apps to workspaces
    -- Start Browser on workspace 1
    hl.exec_cmd("min")
    
    -- Start Terminal on workspace 2
    hl.exec_cmd("kitty")

    -- Choice of editor for workspace 3
    -- Toggle between these by commenting out the unwanted line
    hl.exec_cmd("geany")
    -- hl.exec_cmd("kitty --class yazi -e yazi")
end)

