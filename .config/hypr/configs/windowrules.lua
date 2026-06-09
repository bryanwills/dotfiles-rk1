-- Window and Layer Rules for Hyprland v0.55
-- File: ~/.config/hypr/configs/windowrules.lua

-- Widgets Rules
-- v0.55 window_rule expects specific table keys for geometry
local widgets = {
    { name = "keybinds-widget", match = { class = "keybinds" }, float = true, size = {750, 650}, move = {585, 1}, border_size = 2, border_color = "rgb(767b7e)", animation = "slide top", opacity = 0.7 },
    { name = "aliases-widget", match = { class = "show-aliases" }, float = true, size = {750, 650}, move = {585, 1}, border_size = 2, border_color = "rgb(767b7e)", animation = "slide top", opacity = 0.7 },
    { name = "clipbox-widget", match = { title = "clipbox-widget" }, float = true, size = {700, 680}, move = {600, 3}, border_size = 0, border_color = "rgb(767b7e)", animation = "slide down" },
    { name = "control-panel-widget", match = { title = "control-panel.py" }, float = true, size = {750, 650}, move = {585, 50}, border_size = 2, border_color = "rgb(767b7e)", animation = "slide top", opacity = 0.9 },
    { name = "audio-widget", match = { class = "Audio Switcher" }, float = true, move = {710, 0}, size = {500, 250}, border_size = 2, border_color = "rgb(767b7e)", animation = "slide top", opacity = 0.7 },
    { name = "mirec-widget", match = { class = "Mirec" }, float = true, move = {5, 1}, size = {500, 300}, border_size = 2, border_color = "rgb(767b7e)", animation = "slide left", opacity = 0.7 },
    { name = "bt-widget", match = { class = "bt-menu" }, float = true, move = {660, 0}, size = {600, 400}, border_size = 2, border_color = "rgb(767b7e)", animation = "slide top", opacity = 0.7 },
    { name = "wifi-widget", match = { class = "floating_wifi" }, float = true, move = {560, 1}, size = {700, 400}, border_size = 2, border_color = "rgb(767b7e)", animation = "slide top", opacity = 0.7 },
    { name = "notif-widget", match = { class = "notif-widget.py" }, float = true, move = {800, 1}, size = {400, 600}, border_size = 2, border_color = "rgb(767b7e)", animation = "slide top", opacity = 0.7 },
    { name = "tt-widget", match = { class = "tt" }, float = true, move = {5, 0}, size = {550, 350}, border_size = 2, border_color = "rgb(767b7e)", animation = "slide left", opacity = 0.7 }
}

for _, rule in ipairs(widgets) do
    hl.window_rule(rule)
end

-- App Launcher & Clipboard
hl.window_rule({
	name = "hyprdash",
	match = { class = "hyprdash"},
	float = true,
	size = {1560, 1000},
	move = {350, 40},
	border_size = 0,
	animation = "gnomed",
})

hl.window_rule({
	name = "S-Bar",
	match = { title = "s-bar"},
	float = true,
	size = {500, 500},
	move = {700, 5},
	border_size = 0,
	animation = "slide top",
})

hl.window_rule({
	name = "floating yazi",
	match = { class = "floating_yazi"},
	float = false,
	size = {900, 600},
	center = true,
	animation = "gnomed",
})

hl.window_rule({
	name = "file_chooser",
	match = { class = "file_chooser"},
	float = true,
	size = {900, 600},
	center = true,
	animation = "gnomed",
})

hl.window_rule({ 
    name = "control-panel-widget", 
    match = { title = "control-panel2.py" }, 
    float = true, 
    size = {750, 800}, 
    move = {560, 0}, 
    border_size = 0,
    no_blur = false, 
    border_color = "rgb(767b7e)", 
    animation = "slide top" 
})

hl.window_rule({
    name = "App Launcher",
    match = { title = "launcher-widget" },
    float = true,
    move = {2, 2},
    border_size = 0,
    animation = "fadeIn",
})

hl.window_rule({
    name = "Wallpaper Changer",
    match = { class = "changewall-widget.py" },
    float = true,
    move = {355, 830},
    border_size = 0,
    animation = "gnomed",
})

hl.window_rule({
    name = "Workspaces Profiles",
    match = { title = "hypr-workspaces.py" },
    float = true,
    size = {450, 560},
    move = {760, 12},
    border_size = 0,
    animation = "slide top",
})

hl.window_rule({
    name = "pass-manager",
    match = { class = "pass" },
    float = true,
    size = { 800, 400 },
    center = true,
    border_size = 0,
    animation = "gnomed",
    opacity = 0.6
})

hl.window_rule({
    name = "kitty-themes",
    match = { class = "kitty-themes" },
    float = true,
    size = { 400, 500 },
    move = {1515, 1},
    border_size = 0,
    animation = "slide right",
    no_max_size = true,
    opacity = 0.6
})

hl.window_rule({
    name = "theme-widget",
    match = { class = "theme-widget.py" },
    float = true,
    size = { 440, 240 },
    move = {1400, 0},
    border_size = 0,
    animation = "slide right",
})

hl.window_rule({
    name = "schedule-widget",
    match = { class = "schedule-widget" },
    float = true,
    size = { 450, 120 },
    center = true,
    border_size = 2,
    border_color = "rgb(767b7e)",
    animation = "gnomed",
    opacity = 0.6
})

-- Scheduler alert pop-up layout configuration
hl.window_rule({
    name = "schedule-alert",
    match = { class = "schedule-alert" },
    float = true,
    size = { 500, 200 },
    center = true,
    border_size = 2,
    border_color = "rgb(767b7e)",
    animation = "gnomed",
    opacity = 0.6
})

hl.window_rule({ 
    name = "sysinfo-widget", 
    match = { class = "sysinfo-widget" }, 
    float = true, 
    move = {1415, 0}, 
    size = {500, 450}, 
    border_size = 2, 
    border_color = "rgb(767b7e)", 
    animation = "slide right", 
    opacity = 0.8 
})

hl.window_rule({ 
    name = "control-panel-widget", 
    match = { title = "control-panel.py" }, 
    float = true, 
    size = {750, 800}, 
    move = {560, 0}, 
    border_size = 1,
    no_blur = false, 
    border_color = "rgb(767b7e)", 
    animation = "slide top" 
})

hl.window_rule({
	name = "budget-buddy",
	match = { class = "budget-buddy"},
	size = {740, 780},
	move = {550, 3},
	float = true,
	opacity = 0.9,
	border_size = 2,
	border_color = "rgb(767b7e)",
	animation = "slide top"
})
hl.window_rule({
	name = "rtm",
	match = { class = "rtm"},
	size = {800, 880},
	move = {550, 3},
	float = true,
	opacity = 0.9,
	border_size = 2,
	border_color = "rgb(767b7e)",
	animation = "slide top"
})
hl.window_rule({
    name = "notifications",
    match = { class = "dunst" },
    opacity = 0.9 
})

-- Music Widget
hl.window_rule({
    name = "music-player",
    match = { class = "music" },
    float = true,
    size = {1000, 850},
    center = true,
    opacity = 0.9,
    border_size = 2,
    border_color = "rgb(767b7e)"

    
})

-- System & Terminal Tools
hl.window_rule({
    name = "kitty",
    match = { class = "kitty" },
    float = true,
    size = {1545, 1069},
    move = {364, 1},
    border_size = 0,
    workspace = 2,
    opacity = 0.8,
    no_blur = false
})

-- File Managers
hl.window_rule({
    name = "yazi",
    match = { class = "yazi" },
    float = true,
    size = {1545, 1069},
    opacity = 0.8,
    workspace = 3,
    move = {364, 1},
    border_size = 0
})

hl.window_rule({
    name = "file-managers",
    match = { class = "thunar" },
    animation = "fade",
    opacity = 0.9,
    workspace = 4,
    border_size = 0
})

-- Editors & Tools
hl.window_rule({
    name = "geany-rule",
    match = { class = "geany" },
    animation = "fade",
    workspace = 5,
    opacity = 0.9,
    border_size = 0
})

hl.window_rule({
    name = "qalculate-rule",
    match = { class = "qalculate-gtk" },
    animation = "slide top",
    size = {600, 400},
    opacity = 0.9,
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

