-- Keybinds for Hyprland v0.55
-- File: ~/.config/hypr/configs/keybinds.lua

local mainMod = "SUPER"
local altMod = "ALT"
local terminal = "kitty"
local backup_terminal = "foot"

-- Main Keybinds
hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + SHIFT + Return", hl.dsp.exec_cmd(backup_terminal))
hl.bind(mainMod .. " + X", hl.dsp.window.close())
hl.bind(mainMod .. " + Space", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen())
hl.bind(mainMod .. " + SHIFT + Q", hl.dsp.exit())
-- hl.bind(mainMod .. " + S", hl.dsp.exec_cmd("~/.local/bin/toggle-theme"))
hl.bind(mainMod .. " + S", hl.dsp.exec_cmd("kitty --class kitty-themes -e ~/custom-scripts/Shell-Widgets/kitty-toggle-theme"))
hl.bind(altMod .. " + N", hl.dsp.exec_cmd("~/.local/bin/nightlight"))

-- App Launchers
-- hl.bind(mainMod .. " + D", hl.dsp.exec_cmd("python3 $HOME/custom-scripts/Python-Widgets/launcher-widget.py"))
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd("python3 $HOME/custom-scripts/S-Bar/bar-ui.py"))
hl.bind(mainMod .. " + Y", hl.dsp.exec_cmd("kitty --class yazi -e yazi"))
-- hl.bind(mainMod .. " + T", hl.dsp.exec_cmd("thunar"))
hl.bind(altMod .. " + 1", hl.dsp.exec_cmd("kitty --class rtm -e python3 ~/arch-projects/RTM/rtm.py"))
hl.bind(altMod .. " + 2", hl.dsp.exec_cmd("kitty --class budget-buddy -e python3 ~/arch-projects/Budget-Buddy/budget-buddy.py"))
hl.bind(mainMod .." + M", hl.dsp.exec_cmd("min"))

-- Widgets
hl.bind(altMod .. " + A", hl.dsp.exec_cmd("kitty --class show-aliases -e $HOME/custom-scripts/Show-Aliases/show-aliases.sh"))
hl.bind(altMod .. " + B", hl.dsp.exec_cmd("kitty --class keybinds -e $HOME/custom-scripts/Shell-Widgets/keybinds.sh"))
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("kitty --class bt-menu -e $HOME/custom-scripts/bluetooth/bt"))
hl.bind(altMod .. " + W", hl.dsp.exec_cmd("kitty --class floating_wifi -e ~/custom-scripts/wifi/wwifi"))
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd("python3 /home/rk1/custom-scripts/Python-Widgets/changewall-widget.py"))
hl.bind(altMod .. " + M", hl.dsp.exec_cmd("kitty --class music --app-id=music kew"))
hl.bind(altMod .. " + R", hl.dsp.exec_cmd("kitty --class 'Mirec' -e $HOME/arch-projects/MIREC/mirec"))
hl.bind(altMod .. " + 9", hl.dsp.exec_cmd("kitty --class 'Audio Switcher' -e ~/custom-scripts/Shell-Widgets/change-audio.sh"))
hl.bind(altMod .. " + C", hl.dsp.exec_cmd("python3 /home/rk1/custom-scripts/Python-Widgets/clipbox-widget2.py"))
hl.bind(mainMod .. " + C", hl.dsp.exec_cmd("python3 /home/rk1/custom-scripts/Control-Panel/control-panel.py"))
hl.bind(altMod .. " + T", hl.dsp.exec_cmd("kitty --class schedule-widget -e ~/custom-scripts/Shell-Widgets/schedule-widget"))
hl.bind(mainMod .. " + T", hl.dsp.exec_cmd("kitty --class tt -e " .. os.getenv("HOME") .. "/.local/bin/tt tui"))
hl.bind(altMod .. " + I", hl.dsp.exec_cmd("kitty --class sysinfo-widget -e /home/rk1/custom-scripts/Shell-Widgets/sysinfo-widget"))
hl.bind(mainMod .. " + 0", hl.dsp.exec_cmd("python3 /home/rk1/custom-scripts/Control-Panel/theme-widget.py"))

hl.bind(mainMod .. " + P", hl.dsp.exec_cmd("hyprpicker -a -f hex"))
hl.bind(altMod .. "+ P", hl.dsp.exec_cmd("kitty --class pass -e ~/custom-scripts/pass"))
hl.bind(altMod .. "+ SPACE", hl.dsp.exec_cmd("python3 /home/rk1/custom-scripts/Hypr-Workspaces/hypr-workspaces.py"))
-- hl.bind(altMod .. "+ D", hl.dsp.exec_cmd("python3 ~/arch-projects/HyprDash/main.py"))

-- Navigation (Master Layout)
hl.bind(mainMod .. " + H", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + L", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + K", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + J", hl.dsp.focus({ direction = "down" }))

-- Master Layout Controls
-- Strings must match the arguments used in the previous terminal calls
hl.bind(altMod .. " + Space", hl.dsp.layout("swapwithmaster master"))
hl.bind(altMod .. " + J", hl.dsp.layout("cyclenext"))
hl.bind(altMod .. " + K", hl.dsp.layout("cycleprev"))
hl.bind(altMod .. " + L", hl.dsp.layout("mfact +0.05"))
hl.bind(altMod .. " + H", hl.dsp.layout("mfact -0.05"))
hl.bind(mainMod .. " + Equal", hl.dsp.layout("addmaster"))
hl.bind(mainMod .. " + Minus", hl.dsp.layout("removemaster"))

-- Workspaces
-- Using integers for workspace IDs to ensure compatibility with the focus table
for i = 1, 9 do
    hl.bind(mainMod .. " + " .. i, hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. i, hl.dsp.window.move({ workspace = i }))
end

-- Screenshots & Hardware Keys
-- Capture full screen and trigger a desktop notification upon success
hl.bind("Print", hl.dsp.exec_cmd("grim ~/Pictures/Screenshots/$(date +%Y%m%d_%H%M%S).png && notify-send 'Screenshot Captured'"))
hl.bind(mainMod .. " + Print", hl.dsp.exec_cmd([[slurp -b 00000000 -c ffff00 -w 1 | xargs -I {} sh -c "sleep 0.2 && grim -g '{}' ~/Pictures/Screenshots/$(date +%Y%m%d_%H%M%S).png" && notify-send "Screenshot Captured"]]))
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp",  hl.dsp.exec_cmd("brightnessctl set 5%+"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl set 5%-"), { locked = true, repeating = true })

-- Resize with keys
hl.bind(mainMod .. " + R", hl.dsp.window.resize(), { key = true })

-- Mouse Binds
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Special Workspace
-- Toggle special workspace
hl.bind("ALT + S", hl.dsp.window.move({ workspace = "special:magic" }))
-- To see the hiden window and workspace you can use: 
hl.bind("ALT + SHIFT + S", hl.dsp.workspace.toggle_special("magic"))

-- Testing Minimise function
hl.bind("ALT + X", function ()
    hl.dispatch(hl.dsp.workspace.toggle_special("minimize"))
    hl.dispatch(hl.dsp.window.move({workspace = "+0"}))
    hl.dispatch(hl.dsp.workspace.toggle_special("minimize"))
    hl.dispatch(hl.dsp.window.move({workspace = "special:minimize"}))
    hl.dispatch(hl.dsp.workspace.toggle_special("minimize"))
end)

-- Toggle Pseudo On/Off
hl.bind(mainMod .. "+ SPACE", function()
    hl.dsp.window.pseudo({ action = "toggle" })
end)
