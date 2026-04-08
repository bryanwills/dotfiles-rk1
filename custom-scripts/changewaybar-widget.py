#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  changewaybar-widget.py — Waybar theme switcher
#  Bottom-centre, slides from bottom, GTK Layer Shell
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell
import os, subprocess, threading

THEME_DIR  = os.path.expanduser("~/.config/waybar/themes")
CONFIG_DIR = os.path.expanduser("~/.config/waybar")
WIDGET_W   = 220
MARGIN_H   = 680   # px from each side horizontally to centre it

# ── Pywal colors ──────────────────────────────────────────────────────────────
def get_wal_colors():
    try:
        with open(os.path.expanduser("~/.cache/wal/colors")) as f:
            return [l.strip() for l in f if l.strip()]
    except:
        return ["#1a1a2e","#16213e","#0f3460","#533483",
                "#e94560","#2d6a4f","#52b788","#a8dadc",
                "#457b9d","#1d3557","#2d6a4f","#52b788",
                "#a8dadc","#e9c46a","#f4a261","#ffffff"]

C   = get_wal_colors()
BG  = C[0];  BG2 = C[1];  ACC = C[2]
FG  = C[7];  FG2 = C[15] if len(C) > 15 else "#ffffff"
HIGH= C[4];  GRN = C[6]

CSS = f"""
window {{ background-color: transparent; }}
.frame {{
    background-color: alpha({BG}, 0.4);
    border-radius: 14px 14px 14px 14px;
    border: 2px solid {ACC};
    margin: 0px 3px;
}}
.header {{
    background-color: {BG2};
    border-radius: 10px 10px 0px 0px;
    padding: 10px 16px;
    margin-bottom: 8px;
}}
.header-label {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px; font-weight: bold;
}}
.current-lbl {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
}}
/* ListBox */
list {{ background-color: transparent; padding: 4px 10px; }}
row {{
    background-color: {BG2};
    border-radius: 8px;
    border: 2px solid transparent;
    padding: 0px;
    margin: 3px 0px;
}}
row:hover {{ border-color: {ACC}; }}
row:selected {{
    background-color: alpha({ACC}, 0.3);
    border-color: {ACC};
    outline: none;
}}
row:selected * {{ color: {FG2}; }}
.theme-name {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px; font-weight: bold;
}}
.theme-icon {{
    color: {ACC};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px; font-weight: bold;
    min-width: 28px;
}}
.theme-active {{
    color: {GRN};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
    opacity: 0.8;
}}
.status-bar {{
    padding: 6px 14px;
    border-top: 1px solid alpha({ACC}, 0.2);
}}
.status-lbl {{
    color: {FG};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 9px; opacity: 0.4;
}}
.applying-lbl {{
    color: {ACC};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
}}
"""

# ── Waybar icon map ───────────────────────────────────────────────────────────
# Simple ASCII waybar representations using nerd font icons
THEME_ICONS = {
    "full-bar-dark":       "󰹞  ════════════════════════",
    "full-bar-light":      "󰹟  ════════════════════════",
    "less-waybar":         "󰹞  ━━━━━━━   ━━━━━━━━━━━━━━",
    "rounded-dark":        "󰹞  ╭──────   ───────   ───╮",
    "rounded-light":       "󰹟  ╭──────   ───────   ───╮",
    "rounded-neon":        "󰊠  ╭──────   ───────   ───╮",
    "rounded-testing":     "󰙨  ╭──────   ───────   ───╮",
    "experimental-bar":    "󰭻  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄",
}

def get_current_theme():
    config_link = os.path.join(CONFIG_DIR, "config")
    try:
        target = os.readlink(config_link)
        # Extract theme name from symlink path
        parts = target.split(os.sep)
        if "themes" in parts:
            idx = parts.index("themes")
            if idx + 1 < len(parts):
                return parts[idx + 1]
    except:
        pass
    return None

def apply_theme(name, status_cb, done_cb):
    theme_path = os.path.join(THEME_DIR, name)
    config_src = os.path.join(theme_path, "config")
    style_src  = os.path.join(theme_path, "style.css")
    config_dst = os.path.join(CONFIG_DIR, "config")
    style_dst  = os.path.join(CONFIG_DIR, "style.css")

    GLib.idle_add(status_cb, f"󰑓  Switching to {name}...")

    # Remove old symlinks
    for path in (config_dst, style_dst):
        try: os.remove(path)
        except: pass

    # Create new symlinks
    try:
        os.symlink(config_src, config_dst)
        os.symlink(style_src, style_dst)
    except Exception as e:
        GLib.idle_add(status_cb, f"Error: {e}")
        GLib.idle_add(done_cb, False)
        return

    # Restart waybar
    subprocess.run(['killall', 'waybar'], capture_output=True)
    import time; time.sleep(0.3)
    subprocess.Popen(['waybar'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Notify
    subprocess.Popen(['notify-send', 'Waybar', f'Theme switched to {name}'])

    GLib.idle_add(status_cb, f"✓  {name} applied")
    GLib.idle_add(done_cb, True)

# ── Widget ────────────────────────────────────────────────────────────────────
class WaybarWidget(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("changewaybar-widget")

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT,   True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT,  True)
        GtkLayerShell.set_exclusive_zone(self, -1)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 5)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT,   MARGIN_H)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT,  MARGIN_H)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        prov = Gtk.CssProvider()
        prov.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.connect("key-press-event", self._on_key)
        self.connect("destroy", Gtk.main_quit)

        self._applying   = False
        self._cur_theme  = get_current_theme()
        self._row_map    = {}   # ListBoxRow -> theme name

        # ── Frame ─────────────────────────────────────────────────────────────
        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        frame.get_style_context().add_class('frame')
        self.add(frame)

        # Header
        hdr = Gtk.Box(); hdr.get_style_context().add_class('header')
        hl  = Gtk.Label(label="󰖲  Waybar Theme Switcher")
        hl.get_style_context().add_class('header-label')
        hl.set_halign(Gtk.Align.START)
        self.cur_lbl = Gtk.Label(
            label=f"current: {self._cur_theme or 'unknown'}")
        self.cur_lbl.get_style_context().add_class('current-lbl')
        self.cur_lbl.set_halign(Gtk.Align.END)
        hdr.pack_start(hl, True, True, 0)
        hdr.pack_end(self.cur_lbl, False, False, 0)
        frame.pack_start(hdr, False, False, 0)

        # ListBox
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(380)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_activate_on_single_click(False)
        self.listbox.connect("row-activated", self._on_activate)
        scroll.add(self.listbox)
        frame.pack_start(scroll, True, True, 0)

        # Status
        sb = Gtk.Box(); sb.get_style_context().add_class('status-bar')
        self.status_lbl = Gtk.Label(label="Enter to apply  •  ESC to close")
        self.status_lbl.get_style_context().add_class('status-lbl')
        sb.pack_start(self.status_lbl, True, True, 0)
        frame.pack_start(sb, False, False, 0)

        self._build_list()
        GLib.idle_add(self._focus_current)

    def _build_list(self):
        themes = sorted(os.listdir(THEME_DIR)) if os.path.isdir(THEME_DIR) else []

        for name in themes:
            if not os.path.isdir(os.path.join(THEME_DIR, name)):
                continue

            row = Gtk.ListBoxRow()
            inner = Gtk.Box(spacing=12)
            inner.set_margin_top(8); inner.set_margin_bottom(8)
            inner.set_margin_start(12); inner.set_margin_end(12)

            # Waybar preview icon
            icon_str = THEME_ICONS.get(name, "󰹞  ──────────────────────────")
            icon_lbl = Gtk.Label(label=icon_str)
            icon_lbl.get_style_context().add_class('theme-icon')
            icon_lbl.set_halign(Gtk.Align.START)
            inner.pack_start(icon_lbl, True, True, 0)

            # Theme name
            name_lbl = Gtk.Label(label=name)
            name_lbl.get_style_context().add_class('theme-name')
            name_lbl.set_halign(Gtk.Align.START)
            inner.pack_start(name_lbl, False, False, 0)

            # Active indicator
            if name == self._cur_theme:
                active_lbl = Gtk.Label(label="● active")
                active_lbl.get_style_context().add_class('theme-active')
                active_lbl.set_halign(Gtk.Align.END)
                inner.pack_end(active_lbl, False, False, 0)

            row.add(inner)
            self.listbox.add(row)
            self._row_map[row] = name

        self.listbox.show_all()

    def _focus_current(self):
        for row, name in self._row_map.items():
            if name == self._cur_theme:
                self.listbox.select_row(row)
                row.grab_focus()
                return
        # No current — select first
        rows = self.listbox.get_children()
        if rows:
            self.listbox.select_row(rows[0])
            rows[0].grab_focus()

    def _on_activate(self, listbox, row):
        if self._applying:
            return
        name = self._row_map.get(row)
        if not name:
            return
        self._applying = True
        threading.Thread(
            target=apply_theme,
            args=(name, self._set_status, self._done),
            daemon=True).start()

    def _set_status(self, msg):
        self.status_lbl.set_text(msg)

    def _done(self, success):
        self._applying = False
        if success:
            self._cur_theme = self._row_map.get(
                self.listbox.get_selected_row(), self._cur_theme)
            self.cur_lbl.set_text(f"current: {self._cur_theme}")
            GLib.timeout_add(1500, Gtk.main_quit)

    def _on_key(self, widget, event):
        key = event.keyval
        if key == Gdk.KEY_Escape:
            Gtk.main_quit()
        elif key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            row = self.listbox.get_selected_row()
            if row:
                self._on_activate(self.listbox, row)

if __name__ == "__main__":
    win = WaybarWidget()
    win.show_all()
    Gtk.main()
