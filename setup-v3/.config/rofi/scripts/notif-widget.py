#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  notif-widget.py — Notification History Centre for Dunst/Hyprland
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import os, subprocess, re

LOG_FILE = os.path.expanduser("~/.cache/notification_history.log")

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

C    = get_wal_colors()
BG   = C[0];  BG2 = C[1];  ACC = C[2]
FG   = C[7];  FG2 = C[15] if len(C) > 15 else "#ffffff"
HIGH = C[4]

CSS = f"""
window {{
    background-color: {BG};
    border-radius: 12px;
    border: 2px solid {ACC};
}}
.header {{
    background-color: {BG2};
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 10px;
}}
.header-label {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px;
    font-weight: bold;
}}
.subheader {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px;
    opacity: 0.8;
}}
.notif-row {{
    min-height: 40px;
    background-color: {BG2};
    border-radius: 8px;
    border: 4px solid {ACC};
    padding: 28px 14px;
    margin-top: 3px;
    margin-bottom: 3px;
    margin-left: 2px;
    margin-right: 2px;
}}
.notif-row:hover {{
    background-color: {ACC};
    border-color: {FG2};
}}
.notif-time {{
    color: #000000;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px;
    font-weight: bold;
    min-width: 52px;
}}
.notif-text {{
    color: #000000;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px;
}}
.empty-label {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
    opacity: 0.8;
    padding: 24px;
}}
.btn {{
    background-color: {BG2};
    color: {FG2};
    border-radius: 8px;
    border: none;
    padding: 8px 14px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px;
}}
.btn:hover {{
    background-color: {ACC};
    color: {FG2};
}}
.btn-danger {{
    background-color: {BG2};
    color: {FG2};
    border-radius: 8px;
    border: none;
    padding: 8px 14px;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px;
}}
.btn-danger:hover {{
    background-color: {HIGH};
    color: {FG2};
}}
.copied-toast {{
    background-color: {ACC};
    border-radius: 6px;
    padding: 4px 12px;
    margin-top: 6px;
}}
.copied-text {{
    color: {FG2};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
}}
"""

# ── Log parsing ───────────────────────────────────────────────────────────────
def parse_log():
    entries = []
    pattern = re.compile(r'^\[(\d{2}:\d{2})\]\s+(.+)$')
    try:
        with open(LOG_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                m = pattern.match(line)
                entries.append((m.group(1), m.group(2)) if m else ("--:--", line))
    except FileNotFoundError:
        pass
    entries.reverse()
    return entries

# ── Widget ────────────────────────────────────────────────────────────────────
class NotifWidget(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("notif-centre")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)

        # Enable RGBA visual for xray/transparency support
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_default_size(460, 600)

        prov = Gtk.CssProvider()
        prov.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.connect("key-press-event", self._on_key)
        self.connect("destroy", Gtk.main_quit)

        # ── Root ──────────────────────────────────────────────────────────────
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.set_margin_top(12); root.set_margin_bottom(12)
        root.set_margin_start(12); root.set_margin_end(12)
        self.add(root)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hdr.get_style_context().add_class('header')
        hl = Gtk.Label(label="󰂚  Notification Centre")
        hl.get_style_context().add_class('header-label')
        hl.set_halign(Gtk.Align.START)
        self.count_lbl = Gtk.Label(label="")
        self.count_lbl.get_style_context().add_class('subheader')
        self.count_lbl.set_halign(Gtk.Align.END)
        hdr.pack_start(hl, True, True, 0)
        hdr.pack_end(self.count_lbl, False, False, 0)
        root.pack_start(hdr, False, False, 0)

        # Scrollable list
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(480)
        scroll.set_max_content_height(480)
        root.pack_start(scroll, True, True, 0)

        # Inner box with padding so borders aren't clipped
        list_wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        list_wrap.set_margin_top(16); list_wrap.set_margin_bottom(16)
        list_wrap.set_margin_start(2); list_wrap.set_margin_end(2)
        scroll.add(list_wrap)
        self.list_box = list_wrap

        # Toast
        self.toast_box = Gtk.Box()
        self.toast_box.get_style_context().add_class('copied-toast')
        self.toast_box.set_halign(Gtk.Align.CENTER)
        toast_lbl = Gtk.Label(label="󰆏  Copied to clipboard")
        toast_lbl.get_style_context().add_class('copied-text')
        self.toast_box.pack_start(toast_lbl, False, False, 0)
        self.toast_box.set_no_show_all(True)
        root.pack_start(self.toast_box, False, False, 6)

        # Buttons
        btn_row = Gtk.Box(spacing=8)
        btn_row.set_margin_top(10)
        for label, style, cb in [
            ("󰑓  Refresh",  'btn',        lambda _: self._reload()),
            ("󰆴  Clear All", 'btn-danger', lambda _: self._clear()),
        ]:
            b = Gtk.Button(label=label)
            b.get_style_context().add_class(style)
            b.connect("clicked", cb)
            btn_row.pack_start(b, True, True, 0)
        root.pack_start(btn_row, False, False, 0)

        self._reload()

    def _reload(self):
        for child in self.list_box.get_children():
            self.list_box.remove(child)

        entries = parse_log()
        count = len(entries)
        self.count_lbl.set_text(f"{count} notification{'s' if count != 1 else ''}")

        if not entries:
            empty = Gtk.Label(label="󰂛  No notifications yet")
            empty.get_style_context().add_class('empty-label')
            empty.set_halign(Gtk.Align.CENTER)
            self.list_box.pack_start(empty, False, False, 0)
        else:
            for time_str, message in entries:
                self._add_row(time_str, message)

        self.list_box.show_all()

    def _add_row(self, time_str, message):
        row = Gtk.EventBox()
        row.get_style_context().add_class('notif-row')

        inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        inner.set_margin_top(6); inner.set_margin_bottom(6)
        inner.set_margin_start(6); inner.set_margin_end(6)

        # Time badge
        time_lbl = Gtk.Label(label=time_str)
        time_lbl.get_style_context().add_class('notif-time')
        time_lbl.set_halign(Gtk.Align.START)
        time_lbl.set_valign(Gtk.Align.CENTER)
        time_lbl.set_size_request(52, -1)

        # Separator line
        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep.set_margin_top(2); sep.set_margin_bottom(2)

        # Message
        msg_lbl = Gtk.Label(label=message)
        msg_lbl.get_style_context().add_class('notif-text')
        msg_lbl.set_halign(Gtk.Align.START)
        msg_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        msg_lbl.set_max_width_chars(48)
        msg_lbl.set_tooltip_text(message)
        msg_lbl.set_xalign(0)

        inner.pack_start(time_lbl, False, False, 0)
        inner.pack_start(sep, False, False, 0)
        inner.pack_start(msg_lbl, True, True, 0)
        row.add(inner)

        row.connect("button-press-event",
                    lambda w, e, m=message: self._copy(m))
        self.list_box.pack_start(row, False, False, 0)

    def _copy(self, text):
        try:
            proc = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
            proc.communicate(text.encode())
            self._show_toast()
        except Exception as e:
            print(f"Copy failed: {e}")

    def _show_toast(self):
        self.toast_box.set_no_show_all(False)
        self.toast_box.show_all()
        GLib.timeout_add(2000, self._hide_toast)

    def _hide_toast(self):
        self.toast_box.hide()
        return False

    def _clear(self):
        dialog = Gtk.MessageDialog(
            transient_for=self, modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Clear all notifications?")
        dialog.format_secondary_text("This cannot be undone.")
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            open(LOG_FILE, 'w').close()
            subprocess.Popen(['notify-send', 'System', 'Notification history cleared'])
            self._reload()

    def _on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()

if __name__ == "__main__":
    win = NotifWidget()
    win.show_all()
    Gtk.main()
