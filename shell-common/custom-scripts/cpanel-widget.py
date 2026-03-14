#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  cpanel-widget.py — Control panel: Network, Bluetooth, Power
#  Vertical icon strip, slides from right, power opens submenu in-place
#  Place at: ~/custom-scripts/cpanel-widget.py
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell
import subprocess, os

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
HIGH= C[4]

ICON_SIZE      = 32    # font size for nerd font icons
BTN_PAD        = 12    # padding inside each button
MARGIN_TOP     = 285   # px from top — increase to make panel shorter
MARGIN_BOTTOM  = 285   # px from bottom — increase to make panel shorter
MARGIN_RIGHT   = 8    # px from right edge

CSS = f"""
window {{
    background-color: transparent;
}}
.frame {{
    background-color: alpha({BG}, 0.5);
    border-radius: 26px;
    border: 2px solid {ACC};
    border-right: 2px solid {ACC};
    border-top: 5px solid {ACC};
    border-bottom: 5px solid {ACC};
    margin: 6px;
    padding: 6px;
}}
.section-title {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
    opacity: 0.4;
    margin-top: 4px;
    margin-bottom: 2px;
}}
.icon-btn {{
    background-color: {BG2};
    color: {FG2};
    border-radius: 10px;
    border: 2px solid transparent;
    padding: {BTN_PAD}px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: {ICON_SIZE}px;
    margin: 4px 4px;
    min-width: 54px;
    min-height: 54px;
}}
.icon-btn:hover {{
    background-color: {ACC};
    border-color: {FG2};
    color: {FG2};
}}
.icon-btn-active {{
    background-color: {ACC};
    color: {FG2};
    border-radius: 10px;
    border: 2px solid {FG2};
    padding: {BTN_PAD}px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: {ICON_SIZE}px;
    margin: 4px 2px;
    min-width: 64px;
    min-height: 64px;
}}
.icon-btn-danger {{
    background-color: {BG2};
    color: #ff0000;
    border-radius: 10px;
    border: 2px solid transparent;
    padding: {BTN_PAD}px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: {ICON_SIZE}px;
    margin: 4px 2px;
    min-width: 64px;
    min-height: 64px;
}}
.icon-btn-danger:hover {{
    background-color: {HIGH};
    border-color: {FG2};
    color: {FG2};
}}
.separator {{
    background-color: {ACC};
    min-height: 1px;
    margin: 6px 8px;
    opacity: 0.3;
}}
.back-btn {{
    background-color: transparent;
    color: {FG};
    border-radius: 8px;
    border: none;
    padding: 4px 8px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
    opacity: 0.6;
    margin-bottom: 4px;
}}
.back-btn:hover {{
    opacity: 1.0;
    color: {FG2};
}}
"""

# ── Widget ────────────────────────────────────────────────────────────────────
class CPanel(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("cpanel-widget")

        # ── Layer Shell ───────────────────────────────────────────────────────
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP,   True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM,True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP,    MARGIN_TOP)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, MARGIN_BOTTOM)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT,  MARGIN_RIGHT)
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

        # Outer frame
        self.frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.frame.get_style_context().add_class('frame')
        self.add(self.frame)

        # Stack to switch between main and power views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(200)
        self.frame.pack_start(self.stack, True, True, 0)

        self._build_main()
        self._build_power()
        self.stack.set_visible_child_name("main")

    # ── Main panel ────────────────────────────────────────────────────────────
    def _build_main(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_halign(Gtk.Align.CENTER)

        buttons = [
            ("   ",  "Network",    self._open_network,   'icon-btn'),
            ("󰂯",  "Bluetooth",  self._open_bluetooth, 'icon-btn'),
            (None, None, None, None),   # separator
            ("󰐥",  "Power",      self._show_power,     'icon-btn-danger'),
        ]

        for item in buttons:
            icon, label, cb, style = item
            if icon is None:
                sep = Gtk.Separator()
                sep.get_style_context().add_class('separator')
                box.pack_start(sep, False, False, 0)
                continue
            btn = Gtk.Button(label=icon)
            btn.get_style_context().add_class(style)
            btn.set_tooltip_text(label)
            btn.connect("clicked", lambda _, c=cb: c())
            box.pack_start(btn, False, False, 0)

        self.stack.add_named(box, "main")

    # ── Power submenu ─────────────────────────────────────────────────────────
    def _build_power(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_halign(Gtk.Align.CENTER)

        # Back button
        back = Gtk.Button(label="󰁍  back")
        back.get_style_context().add_class('back-btn')
        back.connect("clicked", lambda _: self.stack.set_visible_child_name("main"))
        box.pack_start(back, False, False, 0)

        sep = Gtk.Separator()
        sep.get_style_context().add_class('separator')
        box.pack_start(sep, False, False, 0)

        power_buttons = [
            ("󰤄", "Suspend",  self._suspend),
            ("󰑓", "Reboot",   self._reboot),
            ("󰐥", "Shutdown", self._shutdown),
            ("󰈆", "Logout",   self._logout),
        ]

        for icon, label, cb in power_buttons:
            btn = Gtk.Button(label=icon)
            btn.get_style_context().add_class('icon-btn-danger')
            btn.set_tooltip_text(label)
            btn.connect("clicked", lambda _, c=cb: c())
            box.pack_start(btn, False, False, 0)

        self.stack.add_named(box, "power")

    # ── Actions ───────────────────────────────────────────────────────────────
    def _open_network(self):
        subprocess.Popen(['kitty', '-e', 'nmtui'])
        Gtk.main_quit()

    def _open_bluetooth(self):
        subprocess.Popen(['overskride'])
        Gtk.main_quit()

    def _show_power(self):
        self.stack.set_visible_child_name("power")

    def _suspend(self):
        Gtk.main_quit()
        subprocess.Popen(['systemctl', 'suspend'])

    def _reboot(self):
        Gtk.main_quit()
        subprocess.Popen(['systemctl', 'reboot'])

    def _shutdown(self):
        Gtk.main_quit()
        subprocess.Popen(['systemctl', 'poweroff'])

    def _logout(self):
        Gtk.main_quit()
        subprocess.Popen(['loginctl', 'terminate-user', os.environ.get('USER', '')])

    def _on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            # If on power submenu, go back; otherwise close
            if self.stack.get_visible_child_name() == "power":
                self.stack.set_visible_child_name("main")
            else:
                Gtk.main_quit()

if __name__ == "__main__":
    win = CPanel()
    win.show_all()
    Gtk.main()
