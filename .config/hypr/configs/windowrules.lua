-- Window and Layer Rules for Hyprland v0.55
-- File: ~/.config/hypr/configs/windowrules.lua

-- Widgets Rules
-- v0.55 window_rule expects specific table keys for geometry
local widgets = {
    { name = "keybinds-widget", match = { class = "keybinds" }, float = true, size = {750, 650}, move = {585, 9}, border_size = 0, animation = "slide top" },
    { name = "aliases-widget", match = { class = "show-aliases" }, float = true, size = {750, 650}, move = {585, 9}, animation = "slide top" },
    { name = "clipbox-widget", match = { title = "clipbox-widget" }, float = true, size = {750, 650}, move = {585, 9}, border_size = 0, animation = "slide top" },
    { name = "control-panel-widget", match = { title = "control-panel.py" }, float = true, size = {750, 650}, move = {585, 50}, border_size = 0, animation = "slide top" },
    { name = "audio-widget", match = { title = "Audio Switcher" }, float = true, move = {710, 0}, size = {500, 250}, border_size = 0, animation = "slide top" },
    { name = "mirec-widget", match = { title = "Mirec" }, float = true, move = {10, 55}, size = {500, 250}, border_size = 0, animation = "slide top" },
    { name = "bt-widget", match = { class = "bt-menu" }, float = true, move = {660, 0}, size = {600, 400}, border_size = 0, animation = "slide top" },
    { name = "wifi-widget", match = { class = "floating_wifi" }, float = true, move = {560, 0}, size = {700, 400}, border_size = 0, animation = "slide top" },
    { name = "notif-widget", match = { class = "notif-widget.py" }, float = true, move = {800, 5}, size = {400, 600}, border_size = 0, animation = "slide top" }
}

for _, rule in ipairs(widgets) do
    hl.window_rule(rule)
end

-- App Launcher & Clipboard
-- Changed: active/inactive_opacity replaced by consolidated opacity
hl.window_rule({
	name = "budget-buddy",
	match = { class = "budget-buddy"},
	size = {740, 780},
	move = {550, 3},
	float = true,
	border_size = 2,
	border_color = "rgb(80, 65, 33)",
	animation = "slide top"
})
hl.window_rule({
	name = "rtm",
	match = { class = "rtm"},
	size = {800, 880},
	move = {550, 3},
	float = true,
	border_size = 2,
	border_color = "rgb(80, 65, 33)",
	animation = "slide top"
})
hl.window_rule({
    name = "notifications",
    match = { class = "dunst" },
    opacity = 0.8 
})

-- Music Widget
hl.window_rule({
    name = "music-player",
    match = { class = "music" },
    float = true,
    size = {1000, 850},
    center = true,
    border_size = 2,
    border_color = "rgb(80, 65, 33)"

    
})

-- System & Terminal Tools
hl.window_rule({
    name = "kitty",
    match = { class = "kitty" },
    border_size = 0,
    workspace = 2
})

-- File Managers
hl.window_rule({
    name = "file-managers",
    match = { class = "yazi" },
    animation = "fade",
    opacity = 1.0,
    workspace = 3,
    border_size = 0
})

-- Editors & Tools
hl.window_rule({
    name = "geany-rule",
    match = { class = "geany" },
    animation = "fade",
    workspace = 3,
    border_size = 0
})

hl.window_rule({
    name = "qalculate-rule",
    match = { class = "qalculate-gtk" },
    animation = "slide top",
    size = {600, 400},
    opacity = 1.0,
    border_size = 0
    
})

-- Browsers
hl.window_rule({ name = "browsers", match = { class = "falcon" }, workspace = 1, opacity = 1.0, border_size = 0 })
hl.window_rule({ name = "min-browser", match = { class = "Min" }, workspace = 1, opacity = 1.0, border_size = 0 })

-- System Dialogs
hl.window_rule({
    name = "save-open-rule",
    match = { title = "^.*(Save|Open).*$" },
    stay_focused = true,
    float = true,
    center = true
})

-- Special workplace
hl.workspace_rule({ 
    workspace = "special:magic",   
    on_created_empty = "foot"
})

hl.window_rule({
    match = { workspace = "special:magic" },
    border_size = 1,
    border_color = "rgb(ffff00)"
})

-- Layer Rules
hl.layer_rule({
    name = "notifications",
    match = { namespace = "dunst" },
    blur = true
})

