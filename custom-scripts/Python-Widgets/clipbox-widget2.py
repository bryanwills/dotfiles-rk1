#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
# clipbox-widget.py — Clipboard manager, refactored to match Control Panel
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, Pango, GtkLayerShell
import os, subprocess, json, threading

WIDGET_W    = 700
WIDGET_H    = 680
PINS_FILE   = os.path.expanduser("~/.cache/clipbox-pins.json")
DISPLAY_MAX = 100

# Consistent Theme Colours
BG = "#1d2021"
BG_SEC = "#050505"
BORDER = "#222222"
ACC = "#9c7321"
FG = "#ffffff"
FG_DIM = "#aaaaaa"

CSS = f"""
window {{ background-color: {BG}; }}
.frame {{
    background-color: {BG};
    border-radius: 4px;
    border: 1px solid #333333;
    margin: 6px;
}}
.header {{
    background-color: {BG};
    border-radius: 4px;
    padding: 10px 14px; margin-bottom: 6px;
}}
.header-label {{
    color: {FG}; font-family: "JetBrains Mono";
    font-size: 16px; font-weight: bold;
}}
.count-lbl {{
    color: {FG}; font-family: "JetBrains Mono";
    font-size: 12px;
}}
.search-box {{
    background-color: {BG}; border-radius: 4px;
    border: 0px solid #9c7321; padding: 2px 8px;
    margin: 0px 12px 6px 12px;
}}
.search-entry {{
    background-color: transparent; color: #ffffff;
    font-family: "JetBrains Mono"; font-size: 14px;
    border: 2px solid #9c7321; padding: 6px 4px;
}}
.tab-bar {{ background-color: transparent; padding: 0px 12px 6px 12px; }}
.tab-btn {{
    background-color: transparent; color: {FG};
    border-radius: 4px; border: none; padding: 4px 14px;
    font-family: "JetBrains Mono"; font-size: 11px;
}}
.tab-active {{
    background-color: {ACC}; color: #000000;
    border-radius: 4px; border: none; padding: 4px 14px;
    font-family: "JetBrains Mono"; font-size: 11px; font-weight: bold;
}}
.preview-box {{
    background-color: {BG}; border-radius: 4px;
    border: 1px solid #9c7321;
    padding: 8px 12px; margin: 0px 12px 6px 12px;
}}
.preview-text {{
    color: {FG}; font-family: "JetBrains Mono";
    font-size: 11px;
}}
list {{
    background-color: transparent;
    padding: 4px 8px;
}}
row {{
    background-color: {BG};
    border-radius: 4px;
    border: 1px solid #9c7321;
    padding: 8px;
    margin: 4px 0px;
}}
row:selected {{
    background-color: #111111;
    border-color: {ACC};
}}
.clip-text {{
    color: {FG}; font-family: "JetBrains Mono"; font-size: 11px;
}}
.clip-id {{
    color: {FG_DIM}; font-family: "JetBrains Mono";
    font-size: 9px;
}}
.action-btn, .del-btn {{
    background-color: {BG}; color: {FG};
    border: 1px solid #9c7321; border-radius: 4px; padding: 4px 8px;
    font-family: "JetBrains Mono"; font-size: 10px;
}}
.action-btn:hover, .del-btn:hover {{ border-color: {ACC}; }}
.btn {{
    background-color: {BG}; color: {FG};
    border-radius: 4px; border: 1px solid #9c7321; padding: 7px 14px;
    font-family: "JetBrains Mono"; font-size: 11px;
}}
.btn:hover {{ border-color: {ACC}; }}
.btn-danger {{
    background-color: {BG}; color: #ff5555;
    border-radius: 4px; border: 1px solid #9c7321; padding: 7px 14px;
}}
.btn-danger:hover {{ border-color: #ff5555; }}
.status-bar {{ padding: 8px 14px; border-top: 1px solid {BORDER}; }}
.status-lbl {{
    color: {FG_DIM}; font-family: "JetBrains Mono";
    font-size: 9px;
}}
"""

STATUS_HINT = "Enter: copy • Ctrl+P: pin • Ctrl+D: delete • ESC: close"

def cliphist_list():
    try:
        out = subprocess.check_output(['cliphist','list'],
                                      stderr=subprocess.DEVNULL).decode(errors='replace')
        result = []
        for line in out.splitlines():
            if '\t' in line:
                cid, text = line.split('\t', 1)
                result.append((cid.strip(), text.strip()))
        return result
    except:
        return []

def cliphist_decode(cid, text):
    try:
        r = subprocess.run(['cliphist','decode'],
                           input=f"{cid}\t{text}".encode(), capture_output=True)
        return r.stdout
    except:
        return text.encode()

def cliphist_delete(cid, text):
    try:
        subprocess.run(['cliphist','delete'],
                       input=f"{cid}\t{text}".encode(), capture_output=True)
    except:
        pass

def wl_copy(data):
    try:
        subprocess.run(['wl-copy'], input=data, capture_output=True)
    except:
        pass

def load_pins():
    try:
        with open(PINS_FILE) as f: return set(json.load(f))
    except: return set()

def save_pins(pins):
    try:
        with open(PINS_FILE,'w') as f: json.dump(list(pins), f)
    except: pass

class ClipBox(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("clipbox-widget")

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)
        self.set_size_request(WIDGET_W, WIDGET_H)

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

        self._pins        = load_pins()
        self._all_entries = []
        self._cur_tab     = "all"
        self._loading     = True
        self._confirm_clear = False
        self._row_data    = {}

        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        frame.get_style_context().add_class('frame')
        self.add(frame)

        hdr = Gtk.Box(); hdr.get_style_context().add_class('header')
        hl  = Gtk.Label(label="󰅇  Clipboard")
        hl.get_style_context().add_class('header-label')
        hl.set_halign(Gtk.Align.START)
        self.count_lbl = Gtk.Label(label="Loading...")
        self.count_lbl.get_style_context().add_class('count-lbl')
        hdr.pack_start(hl, True, True, 0)
        hdr.pack_end(self.count_lbl, False, False, 0)
        frame.pack_start(hdr, False, False, 0)

        sw = Gtk.Box(); sw.get_style_context().add_class('search-box')
        self.search = Gtk.Entry()
        self.search.get_style_context().add_class('search-entry')
        self.search.set_placeholder_text("Search...")
        self.search.connect("changed", self._on_search)
        self.search.connect("key-press-event", self._on_search_key)
        sw.pack_start(self.search, True, True, 0)
        frame.pack_start(sw, False, False, 0)

        tbar = Gtk.Box(spacing=6); tbar.get_style_context().add_class('tab-bar')
        self.tab_all    = Gtk.Button(label="󰉿  All")
        self.tab_pinned = Gtk.Button(label="󰐃  Pinned")
        for btn, name in [(self.tab_all,"all"),(self.tab_pinned,"pinned")]:
            btn.connect("clicked", lambda _, n=name: self._switch_tab(n))
            tbar.pack_start(btn, False, False, 0)
        frame.pack_start(tbar, False, False, 0)

        pb = Gtk.Box(); pb.get_style_context().add_class('preview-box')
        self.preview_lbl = Gtk.Label(label="Select an entry to preview")
        self.preview_lbl.get_style_context().add_class('preview-text')
        self.preview_lbl.set_halign(Gtk.Align.START)
        self.preview_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        self.preview_lbl.set_max_width_chars(100)
        pb.pack_start(self.preview_lbl, True, True, 0)
        frame.pack_start(pb, False, False, 0)

        self._scroll = Gtk.ScrolledWindow()
        self._scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect("row-activated", self._on_row_activated)
        self.listbox.connect("selected-rows-changed", self._on_selection_changed)
        self._scroll.add(self.listbox)
        frame.pack_start(self._scroll, True, True, 0)

        brow = Gtk.Box(spacing=8)
        brow.set_margin_top(8); brow.set_margin_bottom(8)
        brow.set_margin_start(12); brow.set_margin_end(12)
        for label, style, cb in [
            ("󰑓  Refresh", 'btn', lambda _: self._start_load()),
            ("󰆴  Clear All", 'btn-danger', lambda _: self._clear_all()),
        ]:
            b = Gtk.Button(label=label); b.get_style_context().add_class(style)
            b.connect("clicked", cb); brow.pack_start(b, True, True, 0)
        frame.pack_start(brow, False, False, 0)

        sb = Gtk.Box(); sb.get_style_context().add_class('status-bar')
        self.status_lbl = Gtk.Label(label=STATUS_HINT)
        self.status_lbl.get_style_context().add_class('status-lbl')
        sb.pack_start(self.status_lbl, True, True, 0)
        frame.pack_start(sb, False, False, 0)

        self._update_tab_styles()
        self._start_load()
        GLib.idle_add(self.search.grab_focus)

    def _start_load(self):
        self._loading = True
        self._all_entries = []
        self._row_data = {}
        for row in self.listbox.get_children():
            self.listbox.remove(row)
        self.count_lbl.set_text("Loading...")
        threading.Thread(target=self._bg_load, daemon=True).start()

    def _bg_load(self):
        entries = cliphist_list()
        GLib.idle_add(self._on_loaded, entries)

    def _on_loaded(self, entries):
        self._all_entries = entries
        self._loading = False
        self._rebuild_list()

    def _switch_tab(self, name):
        self._cur_tab = name
        self._update_tab_styles()
        self._rebuild_list()

    def _update_tab_styles(self):
        for btn, n in [(self.tab_all,"all"),(self.tab_pinned,"pinned")]:
            ctx = btn.get_style_context()
            ctx.remove_class('tab-btn'); ctx.remove_class('tab-active')
            ctx.add_class('tab-active' if self._cur_tab == n else 'tab-btn')

    def _rebuild_list(self):
        if self._loading: return
        for row in self.listbox.get_children():
            self.listbox.remove(row)
        self._row_data = {}
        query = self.search.get_text().lower().strip()
        entries = self._all_entries
        if self._cur_tab == "pinned":
            entries = [(c,t) for c,t in entries if t in self._pins]
        if query:
            entries = [(c,t) for c,t in entries if query in t.lower()]
        else:
            pinned = [(c,t) for c,t in entries if t in self._pins]
            unpinned = [(c,t) for c,t in entries if t not in self._pins]
            entries = pinned + unpinned[:DISPLAY_MAX - len(pinned)]
        for cid, text in entries:
            row = self._make_row(cid, text)
            self.listbox.add(row)
            self._row_data[row] = (cid, text)
        self.listbox.show_all()
        shown = len(entries)
        total = len(self._all_entries)
        self.count_lbl.set_text(f"{shown} entries")
        self.preview_lbl.set_text("Select an entry to preview")

    def _make_row(self, cid, text):
        is_pinned = text in self._pins
        row = Gtk.ListBoxRow()
        inner = Gtk.Box(spacing=8)
        inner.set_margin_top(4); inner.set_margin_bottom(4)
        inner.set_margin_start(8); inner.set_margin_end(8)
        id_lbl = Gtk.Label(label=cid)
        id_lbl.get_style_context().add_class('clip-id')
        inner.pack_start(id_lbl, False, False, 0)
        txt = Gtk.Label(label=text)
        txt.get_style_context().add_class('clip-text')
        txt.set_halign(Gtk.Align.START)
        txt.set_ellipsize(Pango.EllipsizeMode.END)
        txt.set_max_width_chars(75)
        inner.pack_start(txt, True, True, 0)
        for icon, style, tip, cb in [
            ("󰐃" if not is_pinned else "󰐄", 'action-btn', "Pin", lambda _, t=text: self._toggle_pin(t)),
            ("󰆴", 'del-btn', "Delete", lambda _, c=cid, t=text: self._delete_entry(c,t)),
        ]:
            b = Gtk.Button(label=icon)
            b.get_style_context().add_class(style)
            b.connect("clicked", cb)
            inner.pack_end(b, False, False, 0)
        row.add(inner)
        return row

    def _on_selection_changed(self, listbox):
        row = listbox.get_selected_row()
        if row and row in self._row_data:
            _, text = self._row_data[row]
            self.preview_lbl.set_text(text[:200] + ("…" if len(text) > 200 else ""))

    def _on_row_activated(self, listbox, row):
        if row in self._row_data: self._do_copy(*self._row_data[row])

    def _do_copy(self, cid, text):
        threading.Thread(target=lambda: wl_copy(cliphist_decode(cid, text)), daemon=True).start()
        Gtk.main_quit()

    def _toggle_pin(self, text):
        if text in self._pins: self._pins.discard(text)
        else: self._pins.add(text)
        save_pins(self._pins); self._rebuild_list()

    def _delete_entry(self, cid, text):
        threading.Thread(target=cliphist_delete, args=(cid,text), daemon=True).start()
        self._pins.discard(text); save_pins(self._pins)
        self._all_entries = [(c,t) for c,t in self._all_entries if not (c==cid and t==text)]
        self._rebuild_list()

    def _clear_all(self):
        if not self._confirm_clear:
            self._confirm_clear = True
            self.status_lbl.set_text("Confirm clear all?")
            return
        self._confirm_clear = False
        
        def smart_wipe_worker():
            subprocess.run(['cliphist', 'wipe'], capture_output=True)
            
            for text in self._pins:
                subprocess.run(['cliphist', 'store'], input=text.encode('utf-8'), capture_output=True)
            
            GLib.idle_add(self._start_load)

        threading.Thread(target=smart_wipe_worker, daemon=True).start()

    def _on_search(self, entry): self._rebuild_list()
    def _on_search_key(self, widget, event): return False
    def _on_key(self, widget, event):
        key = event.keyval
        if key == Gdk.KEY_Escape: Gtk.main_quit()

if __name__ == "__main__":
    win = ClipBox()
    win.show_all()
    Gtk.main()
