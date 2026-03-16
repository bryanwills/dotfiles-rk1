#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  clipbox-widget.py — Clipboard manager, rebuilt with Gtk.ListBox
#  No EventBox focus tricks, native keyboard navigation
# ─────────────────────────────────────────────────────────────────────────────

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, Pango, GtkLayerShell
import os, subprocess, json, threading

WIDGET_W    = 860
WIDGET_H    = 580
PINS_FILE   = os.path.expanduser("~/.cache/clipbox-pins.json")
DISPLAY_MAX = 100

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
    background-color: alpha({BG}, 0.97);
    border-radius: 14px;
    border: 2px solid {ACC};
    margin: 6px;
}}
.header {{
    background-color: {BG2};
    border-radius: 10px 10px 0px 0px;
    padding: 10px 14px; margin-bottom: 6px;
}}
.header-label {{
    color: {FG2}; font-family: "JetBrainsMono Nerd Font";
    font-size: 13px; font-weight: bold;
}}
.count-lbl {{
    color: {FG}; font-family: "JetBrainsMono Nerd Font";
    font-size: 10px; opacity: 0.5;
}}
.search-box {{
    background-color: {BG2}; border-radius: 8px;
    border: 1px solid {ACC}; padding: 2px 8px;
    margin: 0px 12px 6px 12px;
}}
.search-entry {{
    background-color: transparent; color: {FG2};
    font-family: "JetBrainsMono Nerd Font"; font-size: 12px;
    border: none; box-shadow: none; padding: 6px 4px;
}}
.tab-bar {{ background-color: transparent; padding: 0px 12px 6px 12px; }}
.tab-btn {{
    background-color: transparent; color: {FG};
    border-radius: 8px; border: none; padding: 4px 14px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px; opacity: 0.6;
}}
.tab-btn:hover {{ opacity: 1.0; color: {FG2}; }}
.tab-active {{
    background-color: {ACC}; color: {FG2};
    border-radius: 8px; border: none; padding: 4px 14px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px; font-weight: bold;
}}
.preview-box {{
    background-color: {BG2}; border-radius: 8px;
    border: 1px solid alpha({ACC}, 0.4);
    padding: 8px 12px; margin: 0px 12px 6px 12px;
}}
.preview-text {{
    color: {FG}; font-family: "JetBrainsMono Nerd Font";
    font-size: 10px; opacity: 0.8;
}}
/* ListBox styling */
list {{
    background-color: transparent;
    padding: 4px 8px;
}}
row {{
    background-color: {BG2};
    border-radius: 10px;
    border: 4px solid transparent;
    padding: 6px 8px;
    margin: 2px 0px;
}}
row:hover {{
    background-color: alpha({ACC}, 0.2);
    border-color: {ACC};
}}
row:selected {{
    background-color: alpha({ACC}, 0.35);
    border-color: {ACC};
    outline: none;
}}
row:selected * {{ color: {FG2}; }}
.clip-text {{
    color: {FG2}; font-family: "JetBrainsMono Nerd Font"; font-size: 11px;
}}
.clip-id {{
    color: {FG2}; font-family: "JetBrainsMono Nerd Font";
    font-size: 9px; opacity: 0.4; min-width: 36px;
}}
.pin-icon {{ color: {GRN}; font-family: "JetBrainsMono Nerd Font"; font-size: 11px; }}
.action-btn {{
    background-color: transparent; color: {FG};
    border: none; border-radius: 4px; padding: 2px 5px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 10px; opacity: 0.4;
    min-height: 0px; min-width: 0px;
}}
.action-btn:hover {{ opacity: 1.0; color: {FG2}; background-color: alpha({ACC}, 0.3); }}
.del-btn {{
    background-color: transparent; color: {FG};
    border: none; border-radius: 4px; padding: 2px 5px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 10px; opacity: 0.6;
    min-height: 0px; min-width: 0px;
}}
.del-btn:hover {{ opacity: 1.0; color: {HIGH}; background-color: alpha({HIGH}, 0.2); }}
.btn {{
    background-color: {BG2}; color: {FG};
    border-radius: 8px; border: none; padding: 7px 14px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px;
}}
.btn:hover {{ background-color: {ACC}; color: {FG2}; }}
.btn-danger {{
    background-color: {BG2}; color: {HIGH};
    border-radius: 8px; border: none; padding: 7px 14px;
    font-family: "JetBrainsMono Nerd Font"; font-size: 11px;
}}
.btn-danger:hover {{ background-color: {HIGH}; color: {FG2}; }}
.status-bar {{ padding: 4px 14px; border-top: 1px solid alpha({ACC}, 0.2); }}
.status-lbl {{
    color: {FG2}; font-family: "JetBrainsMono Nerd Font";
    font-size: 9px; opacity: 0.8;
}}
.loading-lbl {{
    color: {FG2}; font-family: "JetBrainsMono Nerd Font";
    font-size: 11px; opacity: 0.8; padding: 20px;
}}
"""

STATUS_HINT = "↑↓: navigate  •  Enter: copy  •  Ctrl+P: pin  •  Ctrl+D: delete  •  ESC: close"

# ── Cliphist ──────────────────────────────────────────────────────────────────
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

# ── Widget ────────────────────────────────────────────────────────────────────
class ClipBox(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("clipbox-widget")

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_exclusive_zone(self, -1)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

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
        # Map from ListBoxRow -> (cid, text)
        self._row_data    = {}

        # ── Frame ─────────────────────────────────────────────────────────────
        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        frame.get_style_context().add_class('frame')
        frame.set_size_request(WIDGET_W, WIDGET_H)
        self.add(frame)

        # Header
        hdr = Gtk.Box(); hdr.get_style_context().add_class('header')
        hl  = Gtk.Label(label="󰅇  Clipboard")
        hl.get_style_context().add_class('header-label')
        hl.set_halign(Gtk.Align.START)
        self.count_lbl = Gtk.Label(label="Loading...")
        self.count_lbl.get_style_context().add_class('count-lbl')
        hdr.pack_start(hl, True, True, 0)
        hdr.pack_end(self.count_lbl, False, False, 0)
        frame.pack_start(hdr, False, False, 0)

        # Search
        sw = Gtk.Box(); sw.get_style_context().add_class('search-box')
        si = Gtk.Label(label="  "); si.get_style_context().add_class('search-entry')
        self.search = Gtk.Entry()
        self.search.get_style_context().add_class('search-entry')
        self.search.set_placeholder_text("Search clipboard...")
        self.search.connect("changed", self._on_search)
        self.search.connect("key-press-event", self._on_search_key)
        sw.pack_start(si, False, False, 0)
        sw.pack_start(self.search, True, True, 0)
        frame.pack_start(sw, False, False, 0)

        # Tabs
        tbar = Gtk.Box(spacing=6); tbar.get_style_context().add_class('tab-bar')
        self.tab_all    = Gtk.Button(label="󰉿  All")
        self.tab_pinned = Gtk.Button(label="  Pinned")
        for btn, name in [(self.tab_all,"all"),(self.tab_pinned,"pinned")]:
            btn.connect("clicked", lambda _, n=name: self._switch_tab(n))
            tbar.pack_start(btn, False, False, 0)
        frame.pack_start(tbar, False, False, 0)

        # Preview
        pb = Gtk.Box(); pb.get_style_context().add_class('preview-box')
        self.preview_lbl = Gtk.Label(label="Select an entry to preview")
        self.preview_lbl.get_style_context().add_class('preview-text')
        self.preview_lbl.set_halign(Gtk.Align.START)
        self.preview_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        self.preview_lbl.set_max_width_chars(100)
        self.preview_lbl.set_xalign(0)
        pb.pack_start(self.preview_lbl, True, True, 0)
        frame.pack_start(pb, False, False, 0)

        # ListBox — handles selection + keyboard natively
        self._scroll = Gtk.ScrolledWindow()
        self._scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_activate_on_single_click(False)
        self.listbox.connect("row-activated", self._on_row_activated)
        self.listbox.connect("selected-rows-changed", self._on_selection_changed)
        self._scroll.add(self.listbox)
        frame.pack_start(self._scroll, True, True, 0)

        # Buttons
        brow = Gtk.Box(spacing=8)
        brow.set_margin_top(8); brow.set_margin_bottom(8)
        brow.set_margin_start(12); brow.set_margin_end(12)
        for label, style, cb in [
            ("󰑓  Refresh",   'btn',        lambda _: self._start_load()),
            ("󰆴  Clear All", 'btn-danger', lambda _: self._clear_all()),
        ]:
            b = Gtk.Button(label=label); b.get_style_context().add_class(style)
            b.connect("clicked", cb); brow.pack_start(b, True, True, 0)
        frame.pack_start(brow, False, False, 0)

        # Status
        sb = Gtk.Box(); sb.get_style_context().add_class('status-bar')
        self.status_lbl = Gtk.Label(label=STATUS_HINT)
        self.status_lbl.get_style_context().add_class('status-lbl')
        sb.pack_start(self.status_lbl, True, True, 0)
        frame.pack_start(sb, False, False, 0)

        self._update_tab_styles()
        self._start_load()
        GLib.idle_add(self.search.grab_focus)

    # ── Loading ───────────────────────────────────────────────────────────────
    def _start_load(self):
        self._loading = True
        self._all_entries = []
        self._row_data = {}
        # Clear list
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

    # ── Tab ───────────────────────────────────────────────────────────────────
    def _switch_tab(self, name):
        self._cur_tab = name
        self._update_tab_styles()
        self._rebuild_list()

    def _update_tab_styles(self):
        for btn, n in [(self.tab_all,"all"),(self.tab_pinned,"pinned")]:
            ctx = btn.get_style_context()
            ctx.remove_class('tab-btn'); ctx.remove_class('tab-active')
            ctx.add_class('tab-active' if self._cur_tab == n else 'tab-btn')

    # ── List ──────────────────────────────────────────────────────────────────
    def _rebuild_list(self):
        if self._loading:
            return
        for row in self.listbox.get_children():
            self.listbox.remove(row)
        self._row_data = {}

        query   = self.search.get_text().lower().strip()
        entries = self._all_entries

        if self._cur_tab == "pinned":
            entries = [(c,t) for c,t in entries if t in self._pins]

        if query:
            entries = [(c,t) for c,t in entries if query in t.lower()]
        else:
            pinned   = [(c,t) for c,t in entries if t in self._pins]
            unpinned = [(c,t) for c,t in entries if t not in self._pins]
            entries  = pinned + unpinned[:DISPLAY_MAX - len(pinned)]

        for cid, text in entries:
            row = self._make_row(cid, text)
            self.listbox.add(row)
            self._row_data[row] = (cid, text)

        self.listbox.show_all()
        shown = len(entries)
        total = len(self._all_entries)
        suffix = f" (showing {shown}/{total})" if not query and shown < total else ""
        self.count_lbl.set_text(f"{shown} entries{suffix}")
        self.preview_lbl.set_text("Select an entry to preview")

    def _make_row(self, cid, text):
        is_pinned = text in self._pins
        row = Gtk.ListBoxRow()

        inner = Gtk.Box(spacing=8)
        inner.set_margin_top(2); inner.set_margin_bottom(2)
        inner.set_margin_start(4); inner.set_margin_end(4)

        # Pin indicator
        pin = Gtk.Label(label="" if is_pinned else "")
        pin.get_style_context().add_class('pin-icon' if is_pinned else 'clip-id')
        pin.set_size_request(18, -1)
        inner.pack_start(pin, False, False, 0)

        # ID
        id_lbl = Gtk.Label(label=cid)
        id_lbl.get_style_context().add_class('clip-id')
        id_lbl.set_size_request(36, -1)
        inner.pack_start(id_lbl, False, False, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep.set_margin_top(4); sep.set_margin_bottom(4)
        inner.pack_start(sep, False, False, 0)

        txt = Gtk.Label(label=text)
        txt.get_style_context().add_class('clip-text')
        txt.set_halign(Gtk.Align.START)
        txt.set_ellipsize(Pango.EllipsizeMode.END)
        txt.set_max_width_chars(75)
        txt.set_xalign(0)
        inner.pack_start(txt, True, True, 0)

        # Action buttons
        for icon, style, tip, cb in [
            ("󰐃" if not is_pinned else "󰐄", 'action-btn', "Pin/Unpin", lambda _, t=text: self._toggle_pin(t)),
            ("󰆴", 'del-btn', "Delete", lambda _, c=cid, t=text: self._delete_entry(c,t)),
        ]:
            b = Gtk.Button(label=icon)
            b.get_style_context().add_class(style)
            b.set_tooltip_text(tip)
            b.connect("clicked", cb)
            inner.pack_end(b, False, False, 0)

        row.add(inner)
        return row

    # ── Selection ─────────────────────────────────────────────────────────────
    def _on_selection_changed(self, listbox):
        row = listbox.get_selected_row()
        if row and row in self._row_data:
            cid, text = self._row_data[row]
            self.preview_lbl.set_text(text[:200] + ("…" if len(text) > 200 else ""))

    def _on_row_activated(self, listbox, row):
        if row in self._row_data:
            self._do_copy(*self._row_data[row])

    def _get_selected(self):
        row = self.listbox.get_selected_row()
        if row and row in self._row_data:
            return self._row_data[row]
        return None

    # ── Actions ───────────────────────────────────────────────────────────────
    def _do_copy(self, cid, text):
        threading.Thread(
            target=lambda: wl_copy(cliphist_decode(cid, text)),
            daemon=True).start()
        self._flash_status(f"✓  Copied: {text[:60]}")
        GLib.timeout_add(300, Gtk.main_quit)



    def _toggle_pin(self, text):
        if text in self._pins: self._pins.discard(text)
        else: self._pins.add(text)
        save_pins(self._pins)
        self._rebuild_list()

    def _delete_entry(self, cid, text):
        threading.Thread(target=cliphist_delete, args=(cid,text), daemon=True).start()
        self._pins.discard(text)
        save_pins(self._pins)
        self._all_entries = [(c,t) for c,t in self._all_entries
                             if not (c==cid and t==text)]
        self._rebuild_list()

    def _clear_all(self):
        if not self._confirm_clear:
            self._confirm_clear = True
            self._flash_status("󰆴  Press Clear All again to confirm — cannot be undone")
            return
        self._confirm_clear = False
        threading.Thread(
            target=lambda: subprocess.run(['cliphist','wipe'], capture_output=True),
            daemon=True).start()
        self._pins.clear(); save_pins(self._pins)
        self._start_load()

    def _flash_status(self, msg):
        self.status_lbl.set_text(msg)
        GLib.timeout_add(2000, lambda: self.status_lbl.set_text(STATUS_HINT) or False)

    # ── Keyboard ──────────────────────────────────────────────────────────────
    def _on_search(self, entry):
        self._rebuild_list()

    def _on_search_key(self, widget, event):
        key = event.keyval
        if key == Gdk.KEY_Down:
            rows = self.listbox.get_children()
            if rows:
                self.listbox.select_row(rows[0])
                # Must set focus to the row itself, not the listbox
                rows[0].grab_focus()
            return True
        if key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            rows = self.listbox.get_children()
            if rows and rows[0] in self._row_data:
                self._do_copy(*self._row_data[rows[0]])
            return True
        return False

    def _on_key(self, widget, event):
        key  = event.keyval
        ctrl = event.state & Gdk.ModifierType.CONTROL_MASK
        sel  = self._get_selected()

        if key == Gdk.KEY_Escape:
            Gtk.main_quit()
        elif key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter) and sel:
            self._do_copy(*sel)
        elif ctrl and key == Gdk.KEY_p and sel:
            self._toggle_pin(sel[1])
        elif ctrl and key == Gdk.KEY_d and sel:
            self._delete_entry(*sel)

        elif ctrl and key == Gdk.KEY_r:
            self._start_load()
        elif key == Gdk.KEY_Tab:
            self._switch_tab("pinned" if self._cur_tab == "all" else "all")

if __name__ == "__main__":
    win = ClipBox()
    win.show_all()
    GLib.idle_add(win.search.grab_focus)
    Gtk.main()
