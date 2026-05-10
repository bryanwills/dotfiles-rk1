#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
# notif-widget.py — Notification History Centre (Modernised Design)
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import os, subprocess, re

LOG_FILE = os.path.expanduser("~/.cache/notification_history.log")

# ── Modern Design Palette ────────────────────────────────────────────────────
BG      = "#000000"
BG_SEC  = "#050505"
BORDER  = "#222222"
ACC     = "#52fa69"
FG      = "#ffffff"
FG_DIM  = "#aaaaaa"
TM_COL  = "#40d904"

CSS = f"""
window {{ background-color: #000000; }}
.frame {{
    background-color: {BG};
    border-radius: 4px;
    border: 1px solid #333333;
}}
.header {{
    background-color: {BG_SEC};
    border-radius: 4px;
    padding: 10px 16px;
    margin-bottom: 6px;
}}
.header-label {{
    color: {FG};
    font-family: "JetBrains Mono";
    font-size: 16px; font-weight: bold;
}}
.subheader {{
    color: {FG_DIM};
    font-family: "JetBrains Mono";
    font-size: 14px;
}}
.notif-row {{
    background-color: {BG_SEC};
    border-radius: 2px;
    border: 4px solid {BORDER};
    padding: 12px;
    margin: 4px 4px;
}}
.notif-row:hover {{
    border-color: {ACC};
}}
.notif-time {{
    color: {TM_COL};
    font-family: "JetBrains Mono";
    font-size: 14px;
    min-width: 45px;
}}
.notif-text {{
    color: {FG};
    font-family: "JetBrains Mono";
    font-size: 14px;
}}
.empty-label {{
    color: {FG_DIM};
    font-family: "JetBrains Mono";
    font-size: 14px;
    padding: 24px;
}}
.btn {{
    background-color: #111111;
    color: {FG};
    border-radius: 4px;
    border: 2px solid {BORDER};
    padding: 8px 14px;
    font-family: "JetBrains Mono";
    font-size: 14px;
}}
.btn:hover {{ border-color: {ACC}; }}
.btn-danger {{
    background-color: #111111;
    color: #ff5555;
    border-radius: 4px;
    border: 1px solid {BORDER};
    padding: 8px 14px;
    font-family: "JetBrains Mono";
    font-size: 14px;
}}
.btn-danger:hover {{ border-color: #ff5555; }}
.copied-toast {{
    background-color: {ACC};
    border-radius: 4px;
    padding: 6px 12px;
    margin-top: 6px;
}}
.copied-text {{
    color: #000000;
    font-family: "JetBrains Mono";
    font-size: 11px;
    font-weight: bold;
}}
"""

STATUS_HINT = "Click to copy"

# ── Log parsing ──────────────────────────────────────────────────────────────
def parse_log():
    entries = []
    pattern = re.compile(r'^\[(\d{2}:\d{2})\]\s+(.+)$')
    try:
        with open(LOG_FILE) as f:
            for line in f:
                line = line.strip()
                if not line: continue
                m = pattern.match(line)
                entries.append((m.group(1), m.group(2)) if m else ("--:--", line))
    except FileNotFoundError: pass
    entries.reverse()
    return entries

# ── Widget ────────────────────────────────────────────────────────────────────
class NotifWidget(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("notif-centre")
        self.set_decorated(True)
        self.set_resizable(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)

        self.set_skip_taskbar_hint(True)
        self.set_default_size(460, 600)

        prov = Gtk.CssProvider()
        prov.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.connect("key-press-event", self._on_key)
        self.connect("destroy", Gtk.main_quit)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.set_margin_top(12); root.set_margin_bottom(12)
        root.set_margin_start(12); root.set_margin_end(12)
        self.add(root)

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

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(480)
        root.pack_start(scroll, True, True, 0)

        list_wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        list_wrap.set_margin_top(10)
        scroll.add(list_wrap)
        self.list_box = list_wrap

        self.toast_box = Gtk.Box()
        self.toast_box.get_style_context().add_class('copied-toast')
        self.toast_box.set_halign(Gtk.Align.CENTER)
        toast_lbl = Gtk.Label(label="󰆏  Copied")
        toast_lbl.get_style_context().add_class('copied-text')
        self.toast_box.pack_start(toast_lbl, True, True, 6)
        self.toast_box.set_no_show_all(True)
        root.pack_start(self.toast_box, False, False, 6)

        btn_row = Gtk.Box(spacing=8)
        btn_row.set_margin_top(10)
        for label, style, cb in [
            ("󰑓  Refresh", 'btn', lambda _: self._reload()),
            ("󰆴  Clear All", 'btn-danger', lambda _: self._clear()),
        ]:
            b = Gtk.Button(label=label)
            b.get_style_context().add_class(style)
            b.connect("clicked", cb)
            btn_row.pack_start(b, True, True, 0)
        root.pack_start(btn_row, False, False, 0)

        self._reload()

    def _reload(self):
        for child in self.list_box.get_children(): self.list_box.remove(child)
        entries = parse_log()
        self.count_lbl.set_text(f"{len(entries)} items")
        if not entries:
            empty = Gtk.Label(label="󰂛  No notifications")
            empty.get_style_context().add_class('empty-label')
            self.list_box.pack_start(empty, False, False, 0)
        else:
            for time, msg in entries: self._add_row(time, msg)
        self.list_box.show_all()

    def _add_row(self, time_str, message):
        row = Gtk.EventBox()
        row.get_style_context().add_class('notif-row')
        inner = Gtk.Box(spacing=12)
        inner.set_margin_start(4); inner.set_margin_end(4)
        time_lbl = Gtk.Label(label=time_str)
        time_lbl.get_style_context().add_class('notif-time')
        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        msg_lbl = Gtk.Label(label=message)
        msg_lbl.get_style_context().add_class('notif-text')
        msg_lbl.set_halign(Gtk.Align.START)
        msg_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        msg_lbl.set_max_width_chars(50)
        inner.pack_start(time_lbl, False, False, 0)
        inner.pack_start(sep, False, False, 0)
        inner.pack_start(msg_lbl, True, True, 0)
        row.add(inner)
        row.connect("button-press-event", lambda w, e, m=message: self._copy(m))
        self.list_box.pack_start(row, False, False, 0)

    def _copy(self, text):
        try:
            proc = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
            proc.communicate(text.encode())
            self.toast_box.show_all()
            GLib.timeout_add(2000, lambda: self.toast_box.hide() or False)
        except: pass

    def _clear(self):
        open(LOG_FILE, 'w').close()
        self._reload()

    def _on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape: Gtk.main_quit()

if __name__ == "__main__":
    win = NotifWidget()
    win.show_all()
    Gtk.main()
